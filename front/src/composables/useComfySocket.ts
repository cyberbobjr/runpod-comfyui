import { ref, onUnmounted } from "vue";

export function useComfySocket(promptId: string) {
  const previewImage = ref<string | null>(null);
  const finalImage = ref<string | null>(null);
  const ws = new WebSocket("ws://localhost:8188/ws");

  ws.onmessage = async (event) => {
    const data = JSON.parse(event.data);

    if (data.type === "preview" && data.prompt_id === promptId) {
      previewImage.value = "data:image/png;base64," + data.image;
    }

    if (data.type === "executed" && data.prompt_id === promptId) {
      // Attendre que ComfyUI ait fini l'écriture du fichier
      setTimeout(async () => {
        const res = await fetch("http://localhost:8188/history");
        const history = await res.json();
        const result = history[promptId];

        const allOutputs = Object.values(result.outputs);
        for (const out of allOutputs) {
          if (out && typeof out === "object" && "images" in out && Array.isArray((out as any).images)) {
            for (const img of (out as { images: { filename: string }[] }).images) {
              finalImage.value = `http://localhost:8188/output/${img.filename}`;
              break;
            }
          }
        }
      }, 500);
    }
  };

  onUnmounted(() => ws.close());

  return { previewImage, finalImage };
}
