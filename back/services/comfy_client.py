# comfy_client.py

import requests
import time
import json
import uuid
import websockets
import asyncio

class ComfyClient:
    def __init__(self, base_url="http://127.0.0.1:8188"):
        self.base_url = base_url

    def send_prompt(self, workflow: dict) -> str:
        """Envoie un workflow à ComfyUI et retourne le prompt_id"""
        prompt_id = str(uuid.uuid4())
        payload = {
            "prompt": workflow["prompt"],
            "prompt_id": prompt_id
        }
        res = requests.post(f"{self.base_url}/prompt", json=payload)
        res.raise_for_status()
        return prompt_id

    def wait_for_completion(self, prompt_id: str, timeout=60):
        """Attend que le job soit terminé (polling /history)"""
        start = time.time()
        while time.time() - start < timeout:
            res = requests.get(f"{self.base_url}/history")
            res.raise_for_status()
            data = res.json()
            if prompt_id in data:
                return data[prompt_id]
            time.sleep(0.5)
        raise TimeoutError("Prompt timeout")

    def get_output_images(self, prompt_result: dict) -> list[str]:
        """Récupère les chemins relatifs des images générées"""
        images = []
        for node_id, outputs in prompt_result["outputs"].items():
            for output in outputs["images"]:
                images.append(output["filename"])
        return images

    async def listen_preview(self, on_preview_callback):
        """Écoute les events WebSocket pour les preview live"""
        uri = self.base_url.replace("http", "ws") + "/ws"
        async with websockets.connect(uri) as websocket:
            while True:
                msg = await websocket.recv()
                data = json.loads(msg)
                if data.get("type") == "preview":
                    await on_preview_callback(data)
