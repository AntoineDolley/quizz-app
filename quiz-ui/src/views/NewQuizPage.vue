<script setup>
import { ref } from 'vue';

const username = ref('');
</script>

<template>
  <div class="form-container">
    <p>Saisissez votre nom :</p>
    <form>
      <div class="mb-3">
        <input
          type="text"
          class="form-control"
          placeholder="Username"
          aria-label="Username"
          v-model="username"
        />
      </div>
      <p>{{ username }}</p>
      <button type="button" class="btn btn-outline-danger">GO!</button>
    </form>
  </div>
</template>

<style>
@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}
</style>
