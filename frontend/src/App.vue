<template>
  <div class="container">
    <div class="title">Stabler</div>

    <div class="description">Select the stable version you want to download and apply:</div>
    <div v-if="!loading">
      <select class="dropdown" v-model="selectedVersion">
        <option v-for="version in versions" :key="version" :value="version">{{ version }}</option>
      </select>
    </div>
    <div v-if="!loading">
      <button class="button" :disabled="loading" @click="syncStables">Sync Stables</button>
      <button class="button" :disabled="loading" @click="doRequest">Pull and Apply</button>
    </div>
    <v-overlay
      :z-index="10"
      :value="loading"
    >
      <spinning-logo
        size="100%"
        subtitle="Applying version..."
      />
    </v-overlay>
    <div class="description" v-if="!loading"> Last synced: {{ lastSynced }} </div>
  </div>
</template>

<script>
import axios from 'axios'
import SpinningLogo from './SpinningLogo.vue'

export default {
  name: 'App',
  components: {
    SpinningLogo,
  },
  data() {
    return {
      versions: [],
      selectedVersion: '',
      loading: false,
      lastSynced: ''
    }
  },
  async mounted() {
    const response = await axios.get('/stable-versions')
    this.versions = response.data.stables
    this.selectedVersion = this.versions[0]
    const lastSyncedResponse = await axios.get('/last-updated')
    this.lastSynced = lastSyncedResponse.data.timestamp
  },
  methods: {
    async doRequest() {
      this.loading = true
      try {
        await axios.get('/download', {
          params: {
            version: this.selectedVersion
          }
        })
      } catch (error) {
        console.error('Error:', error)
      } finally {
        this.loading = false
      }
    },
    async syncStables() {
      this.loading = true
      const response = await axios.get('/sync')
      this.lastSynced = response.data.timestamp
      this.loading = false
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
  margin-right: 10px;
}

.dropdown {
  font-size: 15px;
  padding: 5px 10px;
  border-radius: 5px;
  margin-bottom: 20px;
}
</style>
