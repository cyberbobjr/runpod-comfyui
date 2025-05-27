<script setup>
defineProps({
  feature: {
    type: String,
    default: 'This Feature'
  }
});
</script>

<template>
  <div class="p-6 max-w-4xl mx-auto">
    <div class="card">
      <div class="flex flex-col items-center justify-center py-12">
        <svg class="w-16 h-16 text-text-light-muted mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
        </svg>
        <h3 class="text-xl font-semibold text-primary mb-2">{{ feature }} is coming soon!</h3>
        <p class="text-text-light-muted">
          This feature is under development and will be available in a future update.
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.placeholder-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}
</style>
