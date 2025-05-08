import os
import json
import hashlib
import requests
from dotenv import load_dotenv
import argparse
import sys

def compute_autov1_hash(filepath):
    """Calcule le hash AutoV1 (SHA256 hex) d'un fichier."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def resolve_dest_path(dest, base_dir):
    """Remplace ${BASE_DIR} par la vraie valeur."""
    return dest.replace("${BASE_DIR}", base_dir)

def load_models(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    base_dir = data["config"]["BASE_DIR"]
    models = []
    for group in data["groups"].values():
        for model in group:
            dest = resolve_dest_path(model["dest"], base_dir)
            models.append({"dest": dest, "meta": model})
    return models

def load_civitai_token():
    load_dotenv()
    return os.getenv("CIVITAI_TOKEN")

def query_civitai_by_hash(hash_value, token):
    url = f"https://civitai.com/api/v1/model-versions/by-hash/{hash_value}"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    else:
        return None

def parse_args():
    parser = argparse.ArgumentParser(
        description="Outils de vérification et d'enrichissement des modèles.",
        usage="%(prog)s [--civitai] [--hash-only] [--size-only]"
    )
    parser.add_argument("--civitai", action="store_true", help="Récupère les URLs CivitAI des modèles trouvés")
    parser.add_argument("--hash-only", action="store_true", help="Génère uniquement les hash des modèles déclarés dans le json")
    parser.add_argument("--size-only", action="store_true", help="Génère uniquement la taille (en octets) des modèles déclarés dans le json")
    args = parser.parse_args()
    if not args.civitai and not args.hash_only and not args.size_only:
        parser.print_help()
        sys.exit(0)
    return args

def process_size_only(models):
    updated = False
    for model in models:
        path = model["dest"]
        if not os.path.exists(path):
            print(f"Fichier manquant: {path}")
            continue
        size = os.path.getsize(path)
        print(f"Taille pour {path}: {size} octets")
        model["meta"]["size"] = size
        updated = True
        print("-" * 60)
    return updated

def process_hash_only(models):
    updated = False
    for model in models:
        path = model["dest"]
        if not os.path.exists(path):
            print(f"Fichier manquant: {path}")
            continue
        print(f"Calcul du hash pour: {path}")
        hash_value = compute_autov1_hash(path)
        print(f"Hash AutoV1: {hash_value}")
        model["meta"]["hash"] = hash_value
        updated = True
        print("-" * 60)
    return updated

def process_civitai(models, token):
    updated = False
    for model in models:
        path = model["dest"]
        if not os.path.exists(path):
            print(f"Fichier manquant: {path}")
            continue
        print(f"Calcul du hash pour: {path}")
        hash_value = compute_autov1_hash(path)
        print(f"Hash AutoV1: {hash_value}")
        model["meta"]["hash"] = hash_value
        result = query_civitai_by_hash(hash_value, token)
        if result:
            print(f"Trouvé sur CivitAI: {result.get('name', 'Nom inconnu')} (ID: {result.get('id', '-')})")
            print("Réponse complète CivitAI :")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            model_id = result.get("modelId")
            if model_id:
                civitai_url = f"https://civitai.com/models/{model_id}"
                model["meta"]["src"] = civitai_url
                updated = True
        else:
            print("Aucun modèle trouvé sur CivitAI pour ce hash.")
        print("-" * 60)
    return updated

def update_json(models_json, models):
    with open(models_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    base_dir = data["config"]["BASE_DIR"]
    for group_name, group in data["groups"].items():
        for i, model in enumerate(group):
            dest = resolve_dest_path(model["dest"], base_dir)
            for m in models:
                if m["dest"] == dest:
                    if "src" in m["meta"]:
                        model["src"] = m["meta"]["src"]
                    if "hash" in m["meta"]:
                        model["hash"] = m["meta"]["hash"]
                    if "size" in m["meta"]:
                        model["size"] = m["meta"]["size"]
    with open(models_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    args = parse_args()
    models_json = "models.json"
    if not os.path.exists(models_json):
        print("models.json introuvable.")
        return
    models = load_models(models_json)
    updated = False

    if args.size_only:
        updated = process_size_only(models)
    elif args.civitai:
        token = load_civitai_token()
        updated = process_civitai(models, token)
    elif args.hash_only:
        updated = process_hash_only(models)

    if updated:
        update_json(models_json, models)

if __name__ == "__main__":
    main()