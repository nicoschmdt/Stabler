<template>
  <div class="container">
    <div class="title">Stabler</div>

    <div class="description">Select the stable version you want to download and apply:</div>
    <div>
      <select class="dropdown" v-model="selectedVersion">
        <option v-for="version in versions" :key="version" :value="version">{{ version }}</option>
      </select>
    </div>
    <div>
      <button class="button" :disabled="loading" @click="doRequest">Pull and Apply</button>
    </div>
  </div>
  <div v-if="loading">
    <div>Applying version...</div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'App',
  data() {
    return {
      versions: ['1.3.1', '1.4.2'],
      selectedVersion: '1.4.2',
      loading: false
    }
  },
  methods: {
    async doRequest() {
      this.loading = true
      try {
        await axios.get('/download', {
          params: {
            version: this.selectedVersion
          }
          // por um spinner aqui (ver como tá sendo feito no blueos)
        })
      } catch (error) {
        console.error('Error:', error)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100vh;
  padding-top: 20px;
}

.title {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 20px;
}

.description {
  font-size: 18px;
  margin-bottom: 20px;
  align-self: flex-start;
}

.button {
  font-size: 15px;
  padding: 5px 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  align-items: center;
}

.dropdown {
  font-size: 15px;
  padding: 5px 10px;
  border-radius: 5px;
  margin-bottom: 20px;
}
</style>
