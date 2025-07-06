<template>
  <div>
    <h2>Génération d’image</h2>
    <form @submit.prevent="generateImage">
      <input v-model="prompt" placeholder="Prompt..." class="input" />
      <button type="submit" class="btn">Générer</button>
    </form>

    <div v-if="preview || final">
      <h3 v-if="!final">Prévisualisation en cours…</h3>
      <h3 v-if="final">Image finale</h3>
      <img :src="final || preview || undefined" class="preview-img" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useComfySocket } from "@/composables/useComfySocket";

const prompt = ref("");
const preview = ref<string | null>(null);
const final = ref<string | null>(null);
let stopWatch: (() => void) | null = null;

async function generateImage() {
  const res = await fetch("/api/comfyui/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt: prompt.value }),
  });

  const { prompt_id } = await res.json();
  const { previewImage, finalImage } = useComfySocket(prompt_id);

  preview.value = null;
  final.value = null;

  stopWatch?.();
  const unwatch1 = watch(previewImage, (val) => (preview.value = val));
  const unwatch2 = watch(finalImage, (val) => (final.value = val));
  stopWatch = () => {
    unwatch1();
    unwatch2();
  };
}
</script>

<style scoped>
.preview-img {
  width: 512px;
  border: 1px solid #ccc;
  margin-top: 1rem;
}
.input {
  padding: 0.5rem;
  width: 300px;
}
.btn {
  padding: 0.5rem 1rem;
  margin-left: 1rem;
}
</style>
