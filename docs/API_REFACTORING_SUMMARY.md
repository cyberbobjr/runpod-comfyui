# Refactoring API Service - Résumé des modifications

## Problème initial
Le fichier `api.ts` original était difficile à mocker pour les tests unitaires car il exportait directement une instance Axios configurée avec des variables globales.

## Solution implémentée
Refactorisation complète vers une architecture basée sur une classe `ApiConfig` qui encapsule toute la logique de configuration.

## Changements apportés

### 1. Nouvelle classe `ApiConfig`
- **Encapsulation** : Toute la logique de configuration API dans une classe
- **Injection de dépendances** : Possibilité de passer des configurations personnalisées
- **Isolation** : Chaque instance est indépendante
- **Testabilité** : Facilement mockable

### 2. Fichiers modifiés/créés

#### Modifié
- `front/src/services/api.ts` - Refactorisation complète vers la classe `ApiConfig`
- `front/src/services/__tests__/api.test.ts` - Nouveaux tests unitaires démontrant le mocking

#### Créés
- `docs/API_CONFIG_GUIDE.md` - Guide complet d'utilisation
- `front/src/types/user.types.ts` - Types TypeScript pour les exemples
- `front/src/components/examples/UserManagementExample.vue` - Composant exemple avec injection de dépendances
- `front/src/components/examples/__tests__/UserManagementExample.test.ts` - Tests complets du composant

### 3. Fonctionnalités de la classe `ApiConfig`

#### Interface de configuration
```typescript
interface ApiConfigOptions {
  baseURL?: string;
  timeout?: number;
  tokenStorageKey?: string;
  router?: Router;
}
```

#### Méthodes publiques
- `getAuthToken()` - Récupère le token d'authentification
- `setAuthToken(token)` - Définit le token d'authentification
- `removeAuthToken()` - Supprime le token d'authentification
- `setRouter(router)` - Configure le routeur pour les redirections
- `getApiInstance()` - Retourne l'instance Axios configurée
- `getTokenStorageKey()` - Retourne la clé de stockage du token

### 4. Compatibilité ascendante
Le refactoring maintient la compatibilité avec l'ancien code :
```typescript
// Ancien code - fonctionne toujours
import api, { getAuthToken, setAuthToken } from '@/services/api';

// Nouveau code - utilisation de la classe
import { ApiConfig } from '@/services/api';
const apiConfig = new ApiConfig();
```

### 5. Avantages pour les tests

#### Avant (difficile à mocker)
```typescript
// Problématique : instance globale difficile à mocker
const api = axios.create({...});
export default api;
```

#### Après (facilement mockable)
```typescript
// Solution 1: Mock de la classe complète
const MockApiConfig = vi.fn().mockImplementation(() => ({
  getAuthToken: vi.fn().mockReturnValue('mock-token'),
  getApiInstance: vi.fn().mockReturnValue({
    get: vi.fn().mockResolvedValue({ data: 'mock' })
  })
}));

// Solution 2: Injection de dépendances
class UserService {
  constructor(private apiConfig = new ApiConfig()) {}
}

// Dans les tests
const userService = new UserService(mockApiConfig);
```

### 6. Patterns de test implémentés

1. **Mock complet de la classe**
2. **Spy sur des méthodes spécifiques**
3. **Injection de dépendances**
4. **Tests d'intégration avec axios mocké**

### 7. Documentation et exemples

- Guide complet d'utilisation dans `docs/API_CONFIG_GUIDE.md`
- Composant Vue exemple avec injection de dépendances
- Tests unitaires complets démontrant toutes les techniques de mocking
- Patterns de migration depuis l'ancien système

## Résultat

✅ **Testabilité** : La classe `ApiConfig` est facilement mockable
✅ **Flexibilité** : Configuration personnalisable pour différents environnements
✅ **Maintenabilité** : Code mieux organisé et documenté
✅ **Compatibilité** : L'ancien code continue de fonctionner
✅ **TypeScript** : Support complet avec interfaces et types
✅ **Best practices** : Injection de dépendances et patterns de test modernes

## Utilisation recommandée

### Pour les nouveaux composants
```typescript
export class MyService {
  constructor(private apiConfig = new ApiConfig()) {}
}
```

### Pour les tests
```typescript
const mockApiConfig = {
  getApiInstance: vi.fn().mockReturnValue({
    get: vi.fn().mockResolvedValue({ data: 'mock' })
  })
} as any;

const service = new MyService(mockApiConfig);
```

Cette refactorisation résout complètement le problème de testabilité tout en améliorant l'architecture générale du service API.
