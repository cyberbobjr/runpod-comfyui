import os
import json
import requests
import shutil

def load_env(env_path):
    """Charge les variables d'environnement depuis un fichier .env."""
    env = {}
    if not os.path.exists(env_path):
        return env
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip()
    return env

def get_free_space_mb(folder):
    """Retourne l'espace libre en Mo pour le dossier donné."""
    total, used, free = shutil.disk_usage(folder)
    return free // (1024 * 1024)

def file_matches_version(filepath, expected_version):
    """Vérifie si le fichier correspond à la version attendue (par exemple via un hash ou une taille)."""
    if not os.path.exists(filepath):
        return False
    if expected_version is None:
        return True
    # Exemple simple : version = taille en octets
    actual_size = os.path.getsize(filepath)
    return str(actual_size) == str(expected_version)

def download_file(url, dest, headers=None):
    """Télécharge un fichier avec indicateur de progression, vitesse, taille totale et restante."""
    import time
    try:
        with requests.get(url, stream=True, headers=headers) as r:
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0))
            if total == 0:
                print("Impossible d'obtenir la taille du fichier.")
            downloaded = 0
            start_time = time.time()
            with open(dest, 'wb') as f:
                bar_length = 30  # Longueur de la barre de progression
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        now = time.time()
                        elapsed = now - start_time
                        speed = downloaded / 1024 / 1024 / (elapsed if elapsed > 0 else 1)  # Mo/s
                        percent = (downloaded / total * 100) if total else 0
                        remaining = total - downloaded
                        filled_length = int(bar_length * downloaded // total) if total else 0
                        bar = '=' * filled_length + '-' * (bar_length - filled_length)
                        print(
                            f"\r[{bar}] {percent:6.2f}% | "
                            f"{downloaded/1024/1024:7.2f}M / {total/1024/1024:7.2f}M | "
                            f"Restant: {remaining/1024/1024:7.2f}M | "
                            f"Vitesse: {speed:6.2f} Mo/s",
                            end="", flush=True
                        )
            print()  # Saut de ligne après la barre de progression
        return True
    except Exception as e:
        print(f"\nErreur lors du téléchargement de {url} : {e}")
        return False

def main():
    json_path = os.path.join(os.path.dirname(__file__), "models.json")
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    env = load_env(env_path)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    config = data.get("config", {})
    base_dir = config.get("BASE_DIR", "")
    # Priorité : .env puis variable d'environnement système
    hf_token = env.get("HF_TOKEN") or os.environ.get("HF_TOKEN")
    civitai_token = env.get("CIVITAI_TOKEN") or os.environ.get("CIVITAI_TOKEN")
    models = data.get("models", [])

    for entry in models:
        url = entry["url"]
        dest = entry["dest"]
        headers = entry.get("headers", {})

        # Ajout du token civitai si applicable
        if "civitai.com" in url and civitai_token:
            if "token=" not in url:
                sep = "&" if "?" in url else "?"
                url = f"{url}{sep}token={civitai_token}"

        # Remplacement de la variable BASE_DIR dans le chemin de destination
        dest_real = dest.replace("${BASE_DIR}", base_dir).replace("$BASE_DIR", base_dir)

        # Ajout automatique du Bearer HuggingFace si applicable
        if "huggingface.co" in url and hf_token:
            if not headers:
                headers = {}
            headers["Authorization"] = f"Bearer {hf_token}"

        os.makedirs(os.path.dirname(dest_real), exist_ok=True)

        # Récupère la taille du fichier sur le serveur
        try:
            head = requests.head(url, headers=headers, allow_redirects=True)
            server_size = int(head.headers.get('content-length', 0))
        except Exception as e:
            print(f"Impossible de récupérer la taille du fichier distant pour {url}: {e}")
            server_size = 0

        # Vérifie la taille locale
        local_exists = os.path.exists(dest_real)
        local_size = os.path.getsize(dest_real) if local_exists else -1

        # Décide s'il faut télécharger
        if local_exists and local_size == server_size:
            print(f"OK: {dest_real} déjà présent et à jour (taille identique).")
            continue
        elif local_exists and local_size != server_size:
            print(f"ATTENTION: {dest_real} existe mais la taille diffère ({local_size} != {server_size}), il sera re-téléchargé.")

        free_mb = get_free_space_mb(os.path.dirname(dest_real))
        if free_mb < 500:  # seuil de 500 Mo libres
            print(f"ERREUR: Espace disque insuffisant pour {dest_real} ({free_mb} Mo restants)")
            continue

        print(f"Téléchargement de {url} vers {dest_real} ...")
        success = download_file(url, dest_real, headers)
        if success:
            print(f"Succès: {dest_real} téléchargé.")
        else:
            print(f"Échec: {dest_real} non téléchargé.")

if __name__ == "__main__":
    main()
