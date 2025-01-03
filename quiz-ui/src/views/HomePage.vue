<script setup>
import { ref, onMounted } from 'vue';
import quizApiService from '@/services/QuizApiService';

const registeredScores = ref([]);

onMounted(async () => {
  const quizInfoPromise = quizApiService.getQuizInfo();
  const quizInfoApiResult = await quizInfoPromise;
  console.log(quizInfoApiResult);
  registeredScores.value = quizInfoApiResult.data.scores;
  console.log('Scores', registeredScores);
});
</script>

<template>
  <h1>Home page</h1>
  <router-link to="/new-quiz">Démarrer le quiz !</router-link>
  <div v-for="scoreEntry in registeredScores" v-bind:key="scoreEntry.date">
    {{ scoreEntry.playerName }} - {{ scoreEntry.score }}
  </div>
</template>
