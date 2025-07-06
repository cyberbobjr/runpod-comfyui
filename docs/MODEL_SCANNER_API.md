# Model Scanner API Documentation

## Overview

Le système de scan de modèles fournit une API pour découvrir et analyser automatiquement tous les modèles disponibles dans le répertoire `models` de ComfyUI. Il catégorise les modèles par type (checkpoints, VAE, CLIP, etc.) et fournit des informations détaillées sur chaque fichier.

## Endpoints

### 1. Scanner le répertoire des modèles

```http
GET /api/models/scanner/scan
```

Effectue un scan complet du répertoire des modèles et retourne tous les modèles trouvés, organisés par catégorie.

**Réponse :**
```json
{
  "models_directory": "/path/to/models",
  "total_models": 42,
  "models": {
    "checkpoints": [
      {
        "name": "model1.safetensors",
        "path": "/path/to/models/checkpoints/model1.safetensors",
        "relative_path": "checkpoints/model1.safetensors",
        "subdirectory": "checkpoints",
        "size": 2000000000,
        "size_mb": 2000.0,
        "extension": ".safetensors",
        "type": ["checkpoint", "diffusion_loader"],
        "identified_type": "checkpoint",
        "exists": true
      }
    ],
    "vae": [
      {
        "name": "vae1.safetensors",
        "path": "/path/to/models/vae/vae1.safetensors",
        "relative_path": "vae/vae1.safetensors",
        "subdirectory": "vae",
        "size": 500000000,
        "size_mb": 500.0,
        "extension": ".safetensors",
        "type": ["vae"],
        "identified_type": "vae",
        "exists": true
      }
    ],
    "clip": [
      {
        "name": "clip1.safetensors",
        "path": "/path/to/models/clip/clip1.safetensors",
        "relative_path": "clip/clip1.safetensors",
        "subdirectory": "clip",
        "size": 300000000,
        "size_mb": 300.0,
        "extension": ".safetensors",
        "type": ["clip"],
        "exists": true
      }
    ]
  }
}
```

### 2. Résumé des modèles

```http
GET /api/models/scanner/summary
```

Retourne un résumé statistique des modèles découverts.

**Réponse :**
```json
{
  "total_models": 42,
  "models_directory": "/path/to/models",
  "categories": {
    "checkpoints": {
      "count": 15,
      "total_size_mb": 30000.0
    },
    "vae": {
      "count": 5,
      "total_size_mb": 2500.0
    },
    "clip": {
      "count": 8,
      "total_size_mb": 2400.0
    },
    "loras": {
      "count": 12,
      "total_size_mb": 1200.0
    },
    "controlnet": {
      "count": 2,
      "total_size_mb": 4000.0
    }
  }
}
```

### 3. Recherche de modèles

```http
GET /api/models/scanner/search?query=stable&category=checkpoints
```

Recherche des modèles par nom ou chemin, avec filtrage optionnel par catégorie.

**Paramètres :**
- `query` (string, obligatoire) : Terme de recherche (minimum 2 caractères)
- `category` (string, optionnel) : Catégorie à filtrer

**Réponse :**
```json
{
  "query": "stable",
  "category": "checkpoints",
  "matches": {
    "checkpoints": [
      {
        "name": "stable_diffusion_v1.safetensors",
        "path": "/path/to/models/checkpoints/stable_diffusion_v1.safetensors",
        "relative_path": "checkpoints/stable_diffusion_v1.safetensors",
        "subdirectory": "checkpoints",
        "size": 2000000000,
        "size_mb": 2000.0,
        "extension": ".safetensors",
        "type": ["checkpoint", "diffusion_loader"],
        "exists": true
      }
    ]
  },
  "total_matches": 1
}
```

### 4. Liste des catégories

```http
GET /api/models/scanner/categories
```

Retourne la liste des catégories disponibles avec leurs descriptions.

**Réponse :**
```json
{
  "categories": [
    "checkpoints",
    "vae",
    "clip",
    "controlnet",
    "embeddings",
    "loras",
    "hypernetworks",
    "upscale_models",
    "style_models",
    "diffusion_models",
    "unet",
    "text_encoders",
    "other"
  ],
  "category_descriptions": {
    "checkpoints": "Full model checkpoints and diffusion models",
    "vae": "Variational Autoencoders",
    "clip": "CLIP text encoders",
    "controlnet": "ControlNet models",
    "embeddings": "Text embeddings and textual inversions",
    "loras": "LoRA (Low-Rank Adaptation) models",
    "hypernetworks": "Hypernetwork models",
    "upscale_models": "Upscaling models",
    "style_models": "Style transfer models",
    "diffusion_models": "Diffusion models and UNet architectures",
    "unet": "UNet architectures",
    "text_encoders": "Text encoding models",
    "other": "Uncategorized models"
  }
}
```

### 5. Types de modèles supportés

```http
GET /api/models/scanner/types
```

Retourne des informations sur les types de modèles supportés et les extensions de fichiers.

**Réponse :**
```json
{
  "supported_extensions": [
    ".safetensors",
    ".sft",
    ".ckpt",
    ".pt",
    ".pth",
    ".bin"
  ],
  "model_classifications": {
    "checkpoint": "Full model checkpoints that can be loaded directly",
    "diffusion_loader": "Models compatible with diffusion loaders",
    "vae": "Variational Autoencoders for image encoding/decoding",
    "clip": "CLIP models for text encoding",
    "controlnet": "ControlNet models for guided generation",
    "lora": "LoRA models for fine-tuning",
    "embeddings": "Text embeddings and textual inversions",
    "upscale": "Models for image upscaling",
    "hypernetworks": "Hypernetwork models",
    "style": "Style transfer models",
    "unknown": "Models with unknown or unclassified types"
  },
  "directory_mapping": {
    "checkpoints": ["checkpoint", "diffusion_loader"],
    "vae": ["vae"],
    "clip": ["clip"],
    "controlnet": ["controlnet"],
    "embeddings": ["embeddings"],
    "loras": ["lora"],
    "hypernetworks": ["hypernetworks"],
    "upscale_models": ["upscale"],
    "style_models": ["style"],
    "diffusion_models": ["diffusion_loader"],
    "unet": ["diffusion_loader"],
    "text_encoders": ["clip"]
  }
}
```

## Catégories de modèles

### Checkpoints
- **Types :** `checkpoint`, `diffusion_loader`
- **Extensions :** `.safetensors`, `.ckpt`, `.pt`, `.pth`
- **Description :** Modèles complets incluant UNet, VAE et encodeurs de texte

### VAE (Variational Autoencoders)
- **Types :** `vae`
- **Extensions :** `.safetensors`, `.sft`, `.pt`, `.pth`
- **Description :** Modèles pour l'encodage/décodage d'images

### CLIP (Contrastive Language-Image Pre-training)
- **Types :** `clip`
- **Extensions :** `.safetensors`, `.bin`, `.pt`
- **Description :** Encodeurs de texte pour la compréhension des prompts

### ControlNet
- **Types :** `controlnet`
- **Extensions :** `.safetensors`, `.pth`
- **Description :** Modèles pour le contrôle guidé de la génération

### LoRA (Low-Rank Adaptation)
- **Types :** `lora`
- **Extensions :** `.safetensors`, `.pt`
- **Description :** Modèles de fine-tuning légers

### Embeddings
- **Types :** `embeddings`
- **Extensions :** `.pt`, `.bin`, `.safetensors`
- **Description :** Inversions textuelles et embeddings personnalisés

### Hypernetworks
- **Types :** `hypernetworks`
- **Extensions :** `.pt`, `.pth`
- **Description :** Réseaux de neurones pour la modification de style

### Upscale Models
- **Types :** `upscale`
- **Extensions :** `.pth`, `.safetensors`
- **Description :** Modèles pour l'amélioration de la résolution

## Logique de catégorisation

Le système catégorise automatiquement les modèles en fonction de :

1. **Structure des répertoires** : Analyse du nom du sous-répertoire
2. **Nom du fichier** : Recherche de mots-clés dans le nom
3. **Taille du fichier** : Analyse de la taille pour déterminer le type probable
4. **Extension** : Vérification de l'extension pour la compatibilité

## Codes d'erreur

- **401** : Non authentifié
- **400** : Paramètres de recherche invalides
- **500** : Erreur lors du scan ou de la recherche
- **404** : Répertoire de modèles non trouvé

## Utilisation

Ces endpoints permettent de :
- Découvrir automatiquement tous les modèles disponibles
- Organiser les modèles par type pour une meilleure navigation
- Rechercher des modèles spécifiques
- Obtenir des statistiques sur l'usage de l'espace disque
- Identifier les modèles compatibles avec différents loaders ComfyUI
