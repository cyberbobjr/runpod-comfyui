# CivitAI API Client

## Fonctionnalités Avancées

### Gestion des Requêtes
- Gestion des limites de taux
- Nouvelles méthodes avancées
- Support du streaming de fichiers
- Logging intégré

### Nouvelles Méthodes
- `create_webhook()` : Créer des webhooks
- `get_user_details()` : Obtenir les informations de l'utilisateur
- `bulk_download_model_files()` : Téléchargement en masse
- `generate_model_comparison()` : Comparer des modèles
- `stream_model_version_files()` : Téléchargement en streaming

## Installation
```bash
pip install requests
```

## Configuration Avancée
```python
client = CivitAIClient(
    api_key="votre_clé_api",
    max_retries=3,      # Nombre de tentatives en cas d'erreur
    retry_delay=5,      # Délai entre les tentatives
    logger=mon_logger   # Logger personnalisé (optionnel)
)
```

## Exemples Avancés

### Téléchargement en Masse
```python
# Télécharger plusieurs versions de modèles
model_version_ids = [123, 456, 789]
downloaded_files = client.bulk_download_model_files(
    model_version_ids, 
    output_directory="./downloads"
)
```

### Streaming de Fichiers
```python
# Télécharger un fichier en streaming
for chunk in client.stream_model_version_files(model_version_id=12345):
    # Traiter chaque chunk
    process_chunk(chunk)
```

### Création de Webhook
```python
webhook = client.create_webhook(
    events=["model.create", "model.update"],
    url="https://mon-webhook.com/callback",
    secret="mon_secret_webhook"
)
```

### Comparaison de Modèles
```python
# Comparer plusieurs modèles
comparison = client.generate_model_comparison([123, 456, 789])
print(comparison)
```

## Gestion des Erreurs
- `RateLimitError` pour les limites de requêtes
- Logging détaillé des erreurs
- Mécanisme de nouvelle tentative configurable

## Sécurité
- Support des clés API
- Webhooks avec clé secrète
- Validation des paramètres

## Logging
```python
# Configuration du logging
import logging
logging.basicConfig(level=logging.INFO)
```

## Recommandations
- Utilisez toujours une clé API pour les endpoints privés
- Respectez les limites de requêtes de CivitAI
- Gérez les exceptions potentielles

## Contribution
Contributions, issues et pull requests sont les bienvenues.

## Licence
[À spécifier - par exemple MIT ou Apache 2.0]
# CivitAI API Client

## Description
Client Python complet pour l'API CivitAI, implémentant tous les principaux endpoints documentés.

## Fonctionnalités
- Recherche de modèles avec filtres avancés
- Récupération des versions de modèles
- Recherche de modèles par hash
- Téléchargement de fichiers de modèles
- Récupération d'images
- Gestion des avis et signalements

## Installation
```bash
pip install requests
```

## Utilisation de Base

### Initialisation
```python
from civitai_api_client import CivitAIClient

# Sans clé API (endpoints publics)
client = CivitAIClient()

# Avec clé API (endpoints privés)
client = CivitAIClient("votre_clé_api")
```

### Recherche de Modèles
```python
# Recherche de LORA avec filtres
lora_results = client.get_models(
    model_type="LORA", 
    query="anime", 
    limit=5
)

for model in lora_results.get('items', []):
    print(f"Nom: {model['name']}, ID: {model['id']}")
```

### Recherche par Hash
```python
# Trouver un modèle par son hash
hash_result = client.get_model_version_by_hash("votre_hash")
if hash_result:
    print("Modèle trouvé :", hash_result)
```

### Récupération d'Images
```python
# Obtenir des images pour un modèle spécifique
images = client.get_images(
    model_id=123456, 
    nsfw=False, 
    limit=10
)
```

### Téléchargement de Modèle
```python
# Télécharger un fichier de version de modèle
fichier_modele = client.download_model_version_file(model_version_id=789012)
with open("modele.safetensors", "wb") as f:
    f.write(fichier_modele)
```

## Filtres Avancés
Le client supporte de nombreux filtres pour chaque méthode :
- Recherche par nom, tag, type de modèle
- Filtrage par utilisateur
- Tri des résultats
- Pagination
- Filtres NSFW

## Gestion des Erreurs
- Exceptions pour les erreurs HTTP
- Gestion des réponses 404
- Validation des paramètres

## Notes Importantes
- Certains endpoints nécessitent une clé API
- Respectez les limites de l'API
- Consultez la documentation officielle de CivitAI

## Contribution
Les contributions sont les bienvenues. Ouvrez une issue ou une pull request.

## Licence
[À spécifier - par exemple MIT ou Apache 2.0]