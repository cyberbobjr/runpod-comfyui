# CivitAI Model Enhancement Documentation

## Overview

The ModelScannerService now includes enhanced model identification capabilities using CivitAI's API. When a model cannot be automatically classified (category = "other"), the system will attempt to identify it using various hashing algorithms and CivitAI's model database.

## Features

### Hash Algorithms Supported

The system supports multiple hashing algorithms for model identification:

- **AutoV1**: CivitAI's first-generation hash (SHA256 of first 8KB)
- **AutoV2**: CivitAI's second-generation hash (SHA256 of first 8KB + last 8KB)
- **SHA256**: Standard SHA256 hash of entire file
- **CRC32**: Fast CRC32 checksum
- **Blake3**: Modern fast hashing algorithm (optional, requires blake3 package)

### Rate Limiting

The system implements respectful rate limiting when querying CivitAI:
- Uses only AutoV2 hash algorithm to minimize API calls
- Single API request per unknown model
- 3-second delay after each API call to reduce server load
- Fails gracefully if API limits are reached

## Usage

### Automatic Enhancement

When scanning models, the system automatically attempts CivitAI enhancement for unknown models:

```python
from back.services.model_scanner_service import ModelScannerService

# Scan models directory - unknown models will be enhanced automatically
result = ModelScannerService.scan_models_directory()

# Check enhanced models
for model in result['models']['checkpoints']:
    if 'civitai_info' in model:
        print(f"Enhanced model: {model['name']}")
        print(f"CivitAI Name: {model['civitai_info']['model_name']}")
        print(f"Model Type: {model['civitai_info']['model_type']}")
```

### Manual Enhancement

You can also manually enhance specific models:

```python
from back.services.model_scanner_service import ModelScannerService

model_info = {
    "name": "unknown_model.safetensors",
    "path": "/path/to/model.safetensors",
    "category": "other"
}

enhanced_model = ModelScannerService._enhance_model_with_civitai(model_info)
if enhanced_model:
    print(f"Model identified as: {enhanced_model['civitai_info']['model_name']}")
```

### Hash Utilities

Use the hash utilities directly:

```python
from back.utils.hash_utils import HashUtils

# Single hash
hash_value = HashUtils.get_file_hash("/path/to/model.safetensors", "AutoV2")

# Multiple hashes
hashes = HashUtils.get_multiple_hashes("/path/to/model.safetensors", ["AutoV1", "AutoV2", "SHA256"])
```

## Configuration

### CivitAI Token

Set up your CivitAI token using the TokenService:

```python
from back.services.token_service import TokenService

# Set tokens
TokenService.set_tokens(hf_token=None, civitai_token="your_civitai_token_here")

# Get tokens
tokens = TokenService.get_tokens()
print(f"CivitAI Token: {tokens['civitai_token']}")
```

### Environment Variables

Add your CivitAI token to the `.env` file:

```
CIVITAI_TOKEN=your_civitai_token_here
```

## Enhanced Model Information

When a model is successfully enhanced with CivitAI data, the model info includes:

```python
{
    "name": "model.safetensors",
    "path": "/path/to/model.safetensors",
    "category": "checkpoints",  # Updated from "other"
    "civitai_info": {
        "model_id": 12345,
        "model_name": "Amazing Model",
        "model_type": "checkpoint",
        "version_id": 67890,
        "version_name": "v1.0",
        "base_model": "SD 1.5",
        "description": "An amazing model for...",
        "tags": ["realistic", "portrait"],
        "nsfw": False,
        "creator": "model_creator",
        "download_url": "https://civitai.com/...",
        "image_urls": ["https://image1.jpg", "https://image2.jpg"],
        "stats": {
            "downloadCount": 5000,
            "favoriteCount": 500,
            "commentCount": 100
        },
        "hash_algorithm": "AutoV2",
        "hash_value": "ABC123..."
    }
}
```

## Error Handling

The system handles various error conditions gracefully:

- **No CivitAI token**: Skips enhancement, logs debug message
- **File not found**: Returns None, logs warning
- **API rate limits**: Respects limits, implements delays
- **Hash computation errors**: Tries next algorithm, logs warnings
- **Network errors**: Fails gracefully, logs errors

## Best Practices

1. **Set up CivitAI token** before scanning large model collections
2. **Monitor logs** for rate limiting warnings
3. **Use AutoV2** as the primary hash algorithm (most compatible)
4. **Be patient** - each unknown model adds a 3-second delay for respectful API usage
5. **Batch operations** during off-peak hours to be respectful to CivitAI
6. **Cache results** - enhanced model info is cached in scan results

## Testing

Run the test suite to verify functionality:

```bash
python -m pytest back/tests/test_model_scanner_civitai.py -v
python -m pytest back/tests/test_hash_utils.py -v
```

## Dependencies

Required packages (added to requirements.txt):
- `blake3==0.4.1` (optional, for Blake3 hashing)

All other dependencies are part of the standard Python library or existing project requirements.
