<template>
  <v-container class="container">
    <v-title class="title">Stabler</v-title>

    <v-description class="description">Select the stable version you want to download and apply</v-description>
    <div v-if="!loading" class="dropdown-container">
      <v-select 
        v-model="selectedVersion"
        :items="versions"
      />
      <a
        :href="`https://github.com/bluerobotics/blueos/releases/tag/${selectedVersion}`"
        target="_blank"
        rel="noopener noreferrer"
        title="View release notes on GitHub"
      >
        <span> <v-icon color="#135DA3" icon="mdi-information-variant-box" /> </span>
      </a>
    </div>
    <div v-if="!loading" class="button-container">
      <v-btn @click="sync">Refresh Stables</v-btn>
      <v-btn @click="download">Pull and Apply</v-btn>
    </div>

    <v-card-actions v-if="!loading">
      <v-chip small outlined>
        Last synced: {{ lastSynced }} 
      </v-chip>
    </v-card-actions>

    <v-dialog
      v-model="dialog"
      width="500px"
      persistent
    >
      <v-card
        class="text-center"
      >
        <v-card-title>
          <v-icon icon="mdi-alert" />
          Action required
        </v-card-title>
        <v-card-text
          class="text-left"
        >
          Please reload all your open BlueOS tabs to ensure you're using the latest version.
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-snackbar-queue v-model="errorMessages" timeout="2000" color="error" />
    
    <v-overlay
      :z-index="10"
      :model-value="loading"
      class="d-flex align-center justify-center"
    >
      <spinning-logo
        size="250px"
        subtitle="Processing..."
      />
    </v-overlay>
  </v-container>
</template>

<script>
import axios from 'axios'
import SpinningLogo from './SpinningLogo.vue'
import { ref } from 'vue'


export default {
  name: 'App',
  components: {
    SpinningLogo,
  },
  setup() {
    return {
      versions: ref(['']),
      selectedVersion: ref(''),
      loading: ref(false),
      lastSynced: ref(''),
      dialog: ref(false),
      errorMessages: ref([]),
    }
  },
  async mounted() {
    try {
      const [versionsResponse, lastSyncedResponse] = await Promise.all([
        axios.get('/stable-versions'),
        axios.get('/last-updated')
      ])

      if (versionsResponse.status !== 200) {
        this.errorMessages.push('Error fetching versions')
        return
      }

      this.versions = versionsResponse.data.stables
      this.selectedVersion = this.versions[0]
      this.lastSynced = lastSyncedResponse.data.timestamp
    } catch (error) {
      this.errorMessages.push('Error initializing the application')
    }
  },
  methods: {
    async download() {
      this.loading = true
      try {
        const response = await axios.get('/download', {
          params: {
            version: this.selectedVersion
          }
        })
        if (response.data.status === 200) {
          this.dialog = true
        } else {
          this.errorMessages.push(response.data.message)
        }
      } catch (error) {
        this.errorMessages.push('Error downloading the version')
      } finally {
        this.loading = false
      }
    },
    async sync() {
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

.dropdown-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.button-container {
  display: flex;
  gap: 12px;
}

.info-icon {
  font-size: 20px;
  font-weight: normal;
  display: inline-block;
  color: #135DA3;
}
</style>
