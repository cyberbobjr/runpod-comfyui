# Documentation des nouveaux types pour l'API Models

## Nouveaux types ajoutés

### `ModelsConfig`
Interface pour la configuration des modèles :
```typescript
interface ModelsConfig {
  BASE_DIR: string      // Répertoire de base pour les modèles
  group_order: string[] // Ordre d'affichage des groupes
}
```

### `ApiModelEntry`
Interface pour chaque entrée de modèle dans la réponse API :
```typescript
interface ApiModelEntry {
  url: string           // URL de téléchargement
  dest: string          // Destination du fichier
  git?: string          // Repository Git (optionnel)
  type: string          // Type de modèle (unet, clip, vae, etc.)
  tags?: string[]       // Tags associés (base, fp8, nsfw, etc.)
  src?: string          // Source/origine du modèle
  hash?: string         // Hash de vérification
  size?: number         // Taille du fichier en octets
  exists: boolean       // Indique si le fichier existe localement
  comments?: string     // Commentaires additionnels
  filename?: string     // Nom du fichier
}
```

### `CompleteModelsApiResponse`
Interface pour la réponse complète de l'API `/api/models/` :
```typescript
interface CompleteModelsApiResponse {
  config: ModelsConfig                        // Configuration
  groups: Record<string, ApiModelEntry[]>    // Groupes de modèles
}
```

## Exemple d'utilisation

```typescript
// Import des types
import type { CompleteModelsApiResponse, ApiModelEntry } from '@/stores/types/models.types';

// Fonction pour récupérer les modèles
async function fetchModels(): Promise<CompleteModelsApiResponse> {
  const response = await api.get<CompleteModelsApiResponse>('/api/models/');
  return response.data;
}

// Utilisation
const modelsData = await fetchModels();

// Accès à la configuration
console.log('Base directory:', modelsData.config.BASE_DIR);
console.log('Group order:', modelsData.config.group_order);

// Parcourir les groupes
Object.entries(modelsData.groups).forEach(([groupName, models]) => {
  console.log(`Group: ${groupName}`);
  
  models.forEach((model: ApiModelEntry) => {
    console.log(`  - ${model.type}: ${model.dest}`);
    console.log(`    Size: ${model.size} bytes`);
    console.log(`    Exists: ${model.exists}`);
    console.log(`    Tags: ${model.tags?.join(', ') || 'None'}`);
  });
});

// Filtrer les modèles existants
const existingModels = Object.values(modelsData.groups)
  .flat()
  .filter(model => model.exists);

// Filtrer par type
const fluxModels = Object.values(modelsData.groups)
  .flat()
  .filter(model => model.type === 'unet' && model.tags?.includes('base'));
```

## Types de modèles courants

D'après la réponse API, voici les types de modèles identifiés :
- `clip` - Modèles d'encodage de texte
- `vae` - Variational Autoencoders
- `unet` - Modèles de diffusion principaux
- `diffusion_models` - Modèles de diffusion
- `controlnet` - Modèles ControlNet
- `loras` - Adaptateurs LoRA
- `upscale_models` - Modèles d'upscaling
- `checkpoints` - Points de contrôle complets
- `text_encoders` - Encodeurs de texte
- `clip_vision` - Modèles de vision CLIP
- `infinite_you` - Modèles spécialisés
- `pulid` - Modèles PuLID
- `sam` - Modèles SAM (Segment Anything)

## Tags courants

- `base` - Modèle de base
- `fp8` - Précision 8-bit flottant
- `gguf` - Format GGUF
- `nsfw` - Contenu adulte
- `redux` - Version Redux
- `controlnet` - Relatif à ControlNet
- `icedit` - Relatif à ICEdit
