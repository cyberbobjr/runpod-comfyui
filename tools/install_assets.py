import os
import shutil
from glob import glob

# Déterminer le chemin cible
default_path = r"/comfyui"
comfyui_path = os.environ.get("COMFYUI_PATH", default_path)

workflows_src = os.path.join(os.getcwd(), "workflows")
workflows_dst = os.path.join(comfyui_path, "user", "default", "workflows")

images_src = os.path.join(os.getcwd(), "images")
images_dst = os.path.join(comfyui_path, "input", "Poses")

# Créer les dossiers de destination s'ils n'existent pas
os.makedirs(workflows_dst, exist_ok=True)
os.makedirs(images_dst, exist_ok=True)

# Copier les fichiers JSON (workflows)
for json_file in glob(os.path.join(workflows_src, "*.json")):
    dst_file = os.path.join(workflows_dst, os.path.basename(json_file))
    if not os.path.exists(dst_file):
        shutil.copy2(json_file, workflows_dst)

# Copier les fichiers images (jpg, png, jpeg, bmp, gif, webp)
image_exts = ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.gif", "*.webp")
for ext in image_exts:
    for img_file in glob(os.path.join(images_src, ext)):
        dst_file = os.path.join(images_dst, os.path.basename(img_file))
        if not os.path.exists(dst_file):
            shutil.copy2(img_file, images_dst)

print("Installation terminée.")
