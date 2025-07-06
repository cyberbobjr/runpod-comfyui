import requests
import logging
from typing import Dict, List, Optional, Union, Any, Generator
from urllib.parse import urlencode

class RateLimitError(Exception):
    """Exception levée lorsque la limite de l'API est atteinte"""
    pass

class CivitAIClient:
    """
    Client complet pour l'API CivitAI avec gestion avancée des requêtes
    """
    BASE_URL = "https://civitai.com/api/v1"
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        max_retries: int = 3,
        retry_delay: int = 5,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialise le client CivitAI avec des options avancées

        :param api_key: Clé API CivitAI
        :param max_retries: Nombre maximum de tentatives de requête
        :param retry_delay: Délai entre les tentatives (en secondes)
        :param logger: Logger personnalisé
        """
        self.api_key = api_key
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Configuration du logger
        self.logger = logger or logging.getLogger(__name__)
        
        # En-têtes de base
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "CivitAI-PythonClient/1.0"
        }
        
        # Ajouter l'autorisation si une clé est fournie
        if api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

    def _make_request(
        self, 
        endpoint: str, 
        method: str = 'GET', 
        params: Optional[Dict] = None, 
        data: Optional[Dict] = None,
        stream: bool = False
    ) -> Union[Dict[str, Any], Generator[bytes, None, None]]:
        """
        Méthode générique avancée pour effectuer des requêtes à l'API

        :param endpoint: Point de terminaison de l'API
        :param method: Méthode HTTP
        :param params: Paramètres de requête
        :param data: Données pour POST/PUT
        :param stream: Activer le streaming pour les grands fichiers
        :return: Réponse JSON ou générateur de contenu
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Nettoyer les paramètres None
        if params:
            params = {k: v for k, v in params.items() if v is not None}
        
        # Préparation des tentatives
        attempts = 0
        
        while attempts < self.max_retries:
            try:
                # Choix de la méthode de requête
                if method == 'GET':
                    response = requests.get(
                        url, 
                        headers=self.headers, 
                        params=params,
                        stream=stream
                    )
                elif method == 'POST':
                    response = requests.post(
                        url, 
                        headers=self.headers, 
                        json=data,
                        params=params
                    )
                else:
                    raise ValueError(f"Méthode HTTP non supportée : {method}")
                
                # Gestion des codes de statut spécifiques
                if response.status_code == 429:
                    # Limite de taux atteinte
                    raise RateLimitError("Limite de requêtes API atteinte")
                
                # Lever une exception pour les erreurs HTTP
                response.raise_for_status()
                
                # Streaming ou réponse JSON
                if stream:
                    return response.iter_content(chunk_size=8192)
                
                return response.json()
            
            except RateLimitError:
                # Gérer spécifiquement les limites de taux
                self.logger.warning(f"Limite de taux atteinte. Nouvelle tentative dans {self.retry_delay} secondes.")
                import time
                time.sleep(self.retry_delay)
                attempts += 1
            
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Erreur de requête : {e}")
                raise
        
        # Si toutes les tentatives échouent
        raise Exception("Échec de la requête après plusieurs tentatives")

    def create_webhook(
        self, 
        events: List[str], 
        url: str, 
        secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Créer un webhook pour recevoir des notifications

        :param events: Liste des événements à suivre
        :param url: URL de destination du webhook
        :param secret: Clé secrète pour sécuriser le webhook
        :return: Détails du webhook créé
        """
        data = {
            "events": events,
            "url": url,
            "secret": secret
        }
        
        return self._make_request("webhooks", method="POST", data=data)

    def get_user_details(self) -> Dict[str, Any]:
        """
        Récupère les détails de l'utilisateur connecté

        :return: Informations du profil utilisateur
        """
        if not self.api_key:
            raise ValueError("Une clé API est requise pour ce endpoint")
        
        return self._make_request("user")

    def bulk_download_model_files(
        self, 
        model_version_ids: List[int], 
        output_directory: str = "."
    ) -> List[str]:
        """
        Téléchargement en masse de fichiers de modèles

        :param model_version_ids: Liste des ID de versions de modèles
        :param output_directory: Répertoire de sauvegarde
        :return: Liste des chemins des fichiers téléchargés
        """
        import os
        
        downloaded_files = []
        
        for version_id in model_version_ids:
            try:
                # Récupérer les informations de la version du modèle
                version_info = self._make_request(f"model-versions/{version_id}")
                
                # Télécharger chaque fichier de la version
                for file_index, file_info in enumerate(version_info.get('files', [])):
                    # Créer le nom de fichier
                    filename = f"{version_id}_{file_index}_{file_info.get('name', 'model_file')}"
                    filepath = os.path.join(output_directory, filename)
                    
                    # Télécharger le fichier
                    file_content = self.download_model_version_file(version_id, file_index)
                    
                    # Sauvegarder le fichier
                    with open(filepath, "wb") as f:
                        f.write(file_content)
                    
                    downloaded_files.append(filepath)
                    
                    self.logger.info(f"Téléchargé : {filepath}")
            
            except Exception as e:
                self.logger.error(f"Erreur lors du téléchargement de la version {version_id}: {e}")
        
        return downloaded_files

    def generate_model_comparison(
        self, 
        model_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Générer une comparaison entre plusieurs modèles

        :param model_ids: Liste des ID de modèles à comparer
        :return: Résultats de la comparaison
        """
        data = {
            "modelIds": model_ids
        }
        
        return self._make_request("model-comparisons", method="POST", data=data)

    def stream_model_version_files(
        self, 
        model_version_id: int,
        file_index: int = 0
    ) -> Generator[bytes, None, None]:
        """
        Télécharger un fichier de modèle en streaming

        :param model_version_id: ID de la version du modèle
        :param file_index: Index du fichier à télécharger
        :return: Générateur de contenu de fichier
        """
        # Récupérer les informations de la version du modèle
        version_info = self._make_request(f"model-versions/{model_version_id}")
        
        # Vérifier l'existence du fichier
        if not version_info.get('files') or file_index >= len(version_info['files']):
            raise ValueError("Index de fichier invalide")
        
        # URL de téléchargement
        file_url = version_info['files'][file_index]['downloadUrl']
        
        # Téléchargement en streaming
        return self._make_request(
            file_url.replace(self.BASE_URL, ''), 
            stream=True
        )

def main():
    """
    Exemple d'utilisation avancée du client CivitAI
    """
    # Configuration du logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialiser le client
    client = CivitAIClient(
        api_key="votre_clé_api",
        max_retries=3,
        retry_delay=5
    )
    
    try:
        # Exemple de recherche de modèles
        lora_results = client.get_models(
            model_type="LORA", 
            query="anime", 
            limit=5
        )
        
        # Comparaison de modèles
        model_ids = [model['id'] for model in lora_results.get('items', [])]
        if len(model_ids) > 1:
            comparison = client.generate_model_comparison(model_ids)
            print("Comparaison de modèles :", comparison)
        
        # Téléchargement en masse
        if model_ids:
            downloaded_files = client.bulk_download_model_files(
                [model_ids[0]], 
                output_directory="./downloads"
            )
            print("Fichiers téléchargés :", downloaded_files)
    
    except Exception as e:
        print(f"Erreur lors de l'exécution : {e}")

if __name__ == "__main__":
    main()
import requests
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urlencode

class CivitAIClient:
    """
    Client complet pour l'API CivitAI (https://wiki.civitai.com/wiki/Civitai_API)
    
    Documentation officielle : https://wiki.civitai.com/wiki/Civitai_API
    """
    BASE_URL = "https://civitai.com/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialise le client CivitAI

        :param api_key: Clé API CivitAI (optionnelle, certains endpoints ne la requièrent pas)
        """
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

    def _make_request(
        self, 
        endpoint: str, 
        method: str = 'GET', 
        params: Optional[Dict] = None, 
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Méthode générique pour effectuer des requêtes à l'API

        :param endpoint: Point de terminaison de l'API
        :param method: Méthode HTTP (GET, POST, etc.)
        :param params: Paramètres de requête
        :param data: Données pour POST/PUT
        :return: Réponse JSON de l'API
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Nettoyer les paramètres None
        if params:
            params = {k: v for k, v in params.items() if v is not None}
        
        try:
            if method == 'GET':
                response = requests.get(
                    url, 
                    headers=self.headers, 
                    params=params
                )
            elif method == 'POST':
                response = requests.post(
                    url, 
                    headers=self.headers, 
                    json=data,
                    params=params
                )
            else:
                raise ValueError(f"Méthode HTTP non supportée : {method}")
            
            # Gérer les erreurs d'API
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.HTTPError as e:
            print(f"Erreur HTTP : {e}")
            print(f"Détails de la réponse : {e.response.text}")
            raise

    def get_models(
        self, 
        query: Optional[str] = None,
        tag: Optional[str] = None,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        model_type: Optional[str] = None,
        sort: Optional[str] = None,
        period: Optional[str] = None,
        rating: Optional[float] = None,
        favorites: Optional[bool] = None,
        hidden: Optional[bool] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Recherche et liste des modèles avec de nombreux filtres

        :param query: Terme de recherche
        :param tag: Filtrer par tag
        :param user_id: Filtrer par ID utilisateur
        :param username: Filtrer par nom d'utilisateur
        :param model_type: Type de modèle (Checkpoint, LORA, etc.)
        :param sort: Méthode de tri
        :param period: Période de recherche
        :param rating: Note minimale
        :param favorites: Filtrer les favoris
        :param hidden: Filtrer les modèles cachés
        :param page: Numéro de page
        :param limit: Nombre de résultats par page
        :return: Résultats de recherche de modèles
        """
        params = {
            "query": query,
            "tag": tag,
            "userId": user_id,
            "username": username,
            "type": model_type,
            "sort": sort,
            "period": period,
            "rating": rating,
            "favorites": favorites,
            "hidden": hidden,
            "page": page,
            "limit": limit
        }
        
        return self._make_request("models", params=params)

    def get_model_versions(
        self, 
        model_id: int, 
        page: int = 1, 
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Récupère les versions d'un modèle spécifique

        :param model_id: ID du modèle
        :param page: Numéro de page
        :param limit: Nombre de résultats par page
        :return: Versions du modèle
        """
        params = {
            "page": page,
            "limit": limit
        }
        
        return self._make_request(f"models/{model_id}/model-versions", params=params)

    def get_model_version_by_hash(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """
        Recherche une version de modèle par son hash

        :param file_hash: Hash du fichier
        :return: Informations de la version du modèle
        """
        try:
            return self._make_request(f"model-versions/by-hash/{file_hash}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    def get_images(
        self,
        model_id: Optional[int] = None,
        model_version_id: Optional[int] = None,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        nsfw: Optional[bool] = None,
        sort: Optional[str] = None,
        period: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Recherche et récupère des images avec divers filtres

        :param model_id: Filtrer par ID de modèle
        :param model_version_id: Filtrer par ID de version de modèle
        :param user_id: Filtrer par ID utilisateur
        :param username: Filtrer par nom d'utilisateur
        :param nsfw: Filtrer le contenu NSFW
        :param sort: Méthode de tri
        :param period: Période de recherche
        :param page: Numéro de page
        :param limit: Nombre de résultats par page
        :return: Résultats de recherche d'images
        """
        params = {
            "modelId": model_id,
            "modelVersionId": model_version_id,
            "userId": user_id,
            "username": username,
            "nsfw": nsfw,
            "sort": sort,
            "period": period,
            "page": page,
            "limit": limit
        }
        
        return self._make_request("images", params=params)

    def get_reviews(
        self,
        model_id: int,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Récupère les avis pour un modèle spécifique

        :param model_id: ID du modèle
        :param page: Numéro de page
        :param limit: Nombre de résultats par page
        :return: Avis du modèle
        """
        params = {
            "page": page,
            "limit": limit
        }
        
        return self._make_request(f"models/{model_id}/reviews", params=params)

    def report_model(
        self,
        model_id: int,
        reason: str,
        details: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Signaler un modèle

        :param model_id: ID du modèle à signaler
        :param reason: Raison du signalement
        :param details: Détails supplémentaires (optionnel)
        :return: Résultat du signalement
        """
        data = {
            "modelId": model_id,
            "reason": reason,
            "details": details
        }
        
        return self._make_request("reports", method="POST", data=data)

    def download_model_version_file(
        self, 
        model_version_id: int,
        file_index: int = 0
    ) -> bytes:
        """
        Télécharge un fichier spécifique d'une version de modèle

        :param model_version_id: ID de la version du modèle
        :param file_index: Index du fichier à télécharger (défaut: premier fichier)
        :return: Contenu binaire du fichier
        """
        # Récupérer les informations de la version du modèle
        version_info = self._make_request(f"model-versions/{model_version_id}")
        
        # Vérifier l'existence du fichier
        if not version_info.get('files') or file_index >= len(version_info['files']):
            raise ValueError("Index de fichier invalide")
        
        # URL de téléchargement
        file_url = version_info['files'][file_index]['downloadUrl']
        
        # Télécharger le fichier
        response = requests.get(file_url, headers=self.headers)
        response.raise_for_status()
        
        return response.content