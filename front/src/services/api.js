import axios from 'axios';
import router from '../router';

// Déterminer la baseURL en fonction de l'environnement
const isDevelopment = import.meta.env.MODE === 'development';
const baseURL = isDevelopment 
  ? 'http://localhost:8082/api' 
  : window.location.origin + '/api'; // Utilise l'URL courante en production

// Constante pour la clé du token
const TOKEN_STORAGE_KEY = 'auth_token';

// Créer une instance Axios
const api = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Intercepteur pour ajouter le token d'authentification à chaque requête
api.interceptors.request.use(config => {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

// Intercepteur pour gérer les réponses et les erreurs
api.interceptors.response.use(
  response => response,
  error => {
    // Gérer l'erreur 401 (Non autorisé)
    if (error.response && error.response.status === 401) {
      console.log('Erreur 401: Session expirée ou non authentifié');
      
      // Supprimer le token du localStorage
      localStorage.removeItem(TOKEN_STORAGE_KEY);
      
      // Si on n'est pas déjà sur la page login, rediriger vers /login
      if (router.currentRoute.value.name !== 'login') {
        // Stocker l'URL actuelle pour y revenir après login
        const currentPath = router.currentRoute.value.fullPath;
        router.push({ 
          name: 'login', 
          query: { redirect: currentPath }
        });
      }
    }
    
    return Promise.reject(error);
  }
);

// Méthode spécialisée pour le téléchargement de fichiers
api.downloadFile = async function(path, filename) {
  try {
    const response = await this.get(`/file/download?path=${encodeURIComponent(path)}`, {
      responseType: 'blob'
    });
    
    // Récupérer le type MIME depuis les headers de la réponse
    const contentType = response.headers['content-type'] || 'application/octet-stream';
    
    // Créer un blob avec le bon type MIME
    const blob = new Blob([response.data], { type: contentType });
    const url = window.URL.createObjectURL(blob);
    
    // Créer un élément <a> temporaire pour déclencher le téléchargement
    const link = document.createElement('a');
    link.href = url;
    link.download = filename; // Nom de fichier explicite
    link.style.display = 'none'; // Masquer le lien
    
    // Ajouter au DOM, cliquer, puis supprimer
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Nettoyer l'URL blob après un court délai
    setTimeout(() => {
      window.URL.revokeObjectURL(url);
    }, 100);
    
    return true;
  } catch (error) {
    console.error('Download error:', error);
    throw error;
  }
};

// Exporter aussi la constante pour utilisation ailleurs si nécessaire
export { TOKEN_STORAGE_KEY };
export default api;
