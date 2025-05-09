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

def compute_autov1_hash(filepath):
    """Calcule le hash AutoV1 (SHA256 hex) d'un fichier."""
    import hashlib
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def file_matches_version(filepath, expected_size):
    """Vérifie si le fichier correspond à la taille attendue."""
    if not os.path.exists(filepath):
        return False
    if expected_size:
        actual_size = os.path.getsize(filepath)
        if str(actual_size) == str(expected_size):
            return True
    return False

def download_file(url, dest, headers=None):
    """Télécharge un fichier avec indicateur de progression, vitesse, taille totale, temps restant estimé et timeout."""
    import time
    try:
        with requests.get(url, stream=True, headers=headers, timeout=10) as r:
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0))
            if total == 0:
                print("Impossible d'obtenir la taille du fichier.")
            downloaded = 0
            start_time = time.time()
            last_progress = time.time()
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
                        # Calcul du temps restant estimé
                        if speed > 0:
                            remaining_sec = remaining / 1024 / 1024 / speed
                            mins, secs = divmod(int(remaining_sec), 60)
                            time_left = f"{mins}m{secs:02d}s"
                        else:
                            time_left = "--"
                        print(
                            f"\r[{bar}] {percent:6.2f}% | "
                            f"{downloaded/1024/1024:7.2f}M / {total/1024/1024:7.2f}M | "
                            f"Temps restant: {time_left} | "
                            f"Vitesse: {speed:6.2f} Mo/s",
                            end="", flush=True
                        )
                        last_progress = now
                    # Timeout si aucun progrès depuis 60s
                    if time.time() - last_progress > 60:
                        print("\nTéléchargement bloqué : timeout après 60s sans progrès.")
                        return False
            print()  # Saut de ligne après la barre de progression
        return True
    except requests.exceptions.Timeout:
        print(f"\nErreur : téléchargement de {url} annulé (timeout réseau).")
        return False
    except Exception as e:
        print(f"\nErreur lors du téléchargement de {url} : {e}")
        return False

def load_models_config(json_path):
    """Charge la configuration des modèles depuis le fichier JSON."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    config = data.get("config", {})
    base_dir = config.get("BASE_DIR", "")
    groups = data.get("groups", {})
    return base_dir, groups

def human_readable_size(size_bytes):
    """Retourne une taille lisible (Ko/Mo/Go) sans balise."""
    if size_bytes is None:
        return ""
    size_bytes = int(size_bytes)
    if size_bytes < 1024:
        return f"{size_bytes} o"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes/1024:.2f} Ko"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes/1024/1024:.2f} Mo"
    else:
        return f"{size_bytes/1024/1024/1024:.2f} Go"

def select_models_interactively(groups, base_dir):
    """Affiche une interface interactive pour sélectionner les modèles à télécharger, groupés par groupe."""
    from prompt_toolkit_rich_checkbox import RichCheckboxList

    model_choices = []
    model_refs = []
    preselected_indices = []
    local_paths = []
    group_titles = []
    idx_counter = 0

    for group_name, models in groups.items():
        # Ajoute un séparateur/titre de groupe (non sélectionnable)
        group_titles.append((len(model_choices), group_name))
        model_choices.append((f"[bold underline]{group_name}[/bold underline]", ""))  # Pas de style, non sélectionnable
        model_refs.append((None, None, None))  # Placeholder pour garder l'alignement
        local_paths.append(None)
        idx_counter += 1

        for idx, entry in enumerate(models):
            if entry.get("disable", "").lower() == "true":
                continue
            model_type = entry.get("type", "?")
            filename = os.path.basename(entry['dest'])
            tags = entry.get("tags", [])
            tags_str = ""
            if tags:
                tags_str = " [" + ", ".join(tags) + "]"
            dest_real = entry["dest"].replace("${BASE_DIR}", base_dir).replace("$BASE_DIR", base_dir)
            expected_size = entry.get("size")
            is_installed = file_matches_version(dest_real, expected_size)
            # Style rouge si tag nsfw, sinon pas de couleur
            style = ""
            if any(t.lower() == "nsfw" for t in tags):
                style = "red"
            # Taille affichée
            size_str = ""
            if expected_size:
                size_str = human_readable_size(expected_size)
            elif os.path.exists(dest_real):
                size_str = human_readable_size(os.path.getsize(dest_real))
            if size_str:
                size_str = f" {size_str}"
            label = f"    [bold]{model_type}[/bold] {filename}{tags_str}{size_str}"
            model_choices.append((label, style))
            model_refs.append((group_name, idx, entry))
            local_paths.append(dest_real)
            if is_installed:
                preselected_indices.append(len(model_choices) - 1)
            idx_counter += 1

    if not any(ref[2] for ref in model_refs):
        print("Aucun modèle disponible à télécharger.")
        return []

    # On ne veut pas permettre la sélection des titres de groupe
    selectable_indices = [i for i, ref in enumerate(model_refs) if ref[2] is not None]
    selector = RichCheckboxList(model_choices, preselected_indices=preselected_indices)

    # Patch pour empêcher la sélection des titres de groupe
    orig_get_key_bindings = selector.get_key_bindings
    kb = orig_get_key_bindings()
    @kb.add(' ')
    def _(event):
        if selector.current in selectable_indices:
            selector.selected[selector.current] = not selector.selected[selector.current]
            event.app.invalidate()
    selector.control.key_bindings = kb

    selected_indices = selector.run()

    if selected_indices is None:
        print("Aucun modèle sélectionné.")
        return []

    # Suppression des fichiers décochés et présents sur le disque
    for idx, dest_real in enumerate(local_paths):
        entry = model_refs[idx][2]
        if entry is None:
            continue
        if idx not in selected_indices and os.path.exists(dest_real):
            try:
                os.remove(dest_real)
                print(f"Supprimé: {dest_real}")
            except Exception as e:
                print(f"Erreur lors de la suppression de {dest_real}: {e}")

    selected_entries = []
    for idx, (group_name, _, entry) in enumerate(model_refs):
        if entry is None:
            continue
        dest_real = entry["dest"].replace("${BASE_DIR}", base_dir).replace("$BASE_DIR", base_dir)
        expected_size = entry.get("size")
        is_installed = file_matches_version(dest_real, expected_size)
        # On ne garde que les modèles non déjà installés ou incorrects
        if idx in selected_indices and not is_installed:
            selected_entries.append((group_name, entry))
    return selected_entries

def download_models(selected_entries, base_dir, hf_token, civitai_token):
    """Télécharge les modèles sélectionnés."""
    for group_name, entry in selected_entries:
        url = entry["url"]
        dest = entry["dest"]
        headers = entry.get("headers", {})

        if "civitai.com" in url and civitai_token:
            if "token=" not in url:
                sep = "&" if "?" in url else "?"
                url = f"{url}{sep}token={civitai_token}"

        if "huggingface.co" in url and hf_token:
            if not headers:
                headers = {}
            headers["Authorization"] = f"Bearer {hf_token}"

        dest_real = dest.replace("${BASE_DIR}", base_dir).replace("$BASE_DIR", base_dir)
        os.makedirs(os.path.dirname(dest_real), exist_ok=True)

        # Priorité : taille du JSON > taille serveur
        expected_size = entry.get("size")
        server_size = None
        if expected_size is None:
            try:
                head = requests.head(url, headers=headers, allow_redirects=True)
                server_size = int(head.headers.get('content-length', 0))
            except Exception as e:
                print(f"Impossible de récupérer la taille du fichier distant pour {url}: {e}")
                server_size = 0
            expected_size = server_size

        # Vérifie à nouveau avant téléchargement
        if file_matches_version(dest_real, expected_size):
            print(f"OK: {dest_real} déjà présent et à jour (taille identique).")
            continue

        free_mb = get_free_space_mb(os.path.dirname(dest_real))
        if free_mb < 500:
            print(f"ERREUR: Espace disque insuffisant pour {dest_real} ({free_mb} Mo restants)")
            continue

        print(f"Téléchargement de {url} vers {dest_real} ...")
        success = download_file(url, dest_real, headers)
        if success:
            print(f"Succès: {dest_real} téléchargé.")
        else:
            print(f"Échec: {dest_real} non téléchargé.")

def main():
    json_path = os.path.join(os.path.dirname(__file__), "models.json")
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    env = load_env(env_path)
    base_dir, groups = load_models_config(json_path)
    hf_token = env.get("HF_TOKEN") or os.environ.get("HF_TOKEN")
    civitai_token = env.get("CIVITAI_TOKEN") or os.environ.get("CIVITAI_TOKEN")
    selected_entries = select_models_interactively(groups, base_dir)
    if selected_entries:
        download_models(selected_entries, base_dir, hf_token, civitai_token)

if __name__ == "__main__":
    main()
