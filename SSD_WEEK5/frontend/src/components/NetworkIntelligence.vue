<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">Network Intelligence</h1>
    
    <!-- IP Lookup Section -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-2">IP Lookup</h2>
      <div class="flex gap-2">
        <input
          v-model="ipAddress"
          type="text"
          placeholder="Enter IP address"
          class="flex-1 p-2 border rounded"
        />
        <button
          @click="lookupIp"
          class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Lookup
        </button>
      </div>
      <div v-if="ipInfo" class="mt-4">
        <h3 class="font-semibold mb-2">IP Information:</h3>
        <div class="bg-gray-100 p-4 rounded">
          <div v-for="(value, key) in ipInfo" :key="key" class="mb-2">
            <span class="font-medium">{{ formatKey(key) }}:</span>
            <span>{{ formatValue(value) }}</span>
          </div>
        </div>
        <button
          v-if="currentReportId"
          @click="downloadIpReport"
          class="mt-2 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
        >
          Download Report
        </button>
      </div>
    </div>

    <!-- Domain Analysis Section -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-2">Domain Analysis</h2>
      <div class="flex gap-2">
        <input
          v-model="domain"
          type="text"
          placeholder="Enter domain"
          class="flex-1 p-2 border rounded"
        />
        <button
          @click="analyzeDomain"
          class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Analyze
        </button>
      </div>
      <div v-if="domainInfo" class="mt-4">
        <h3 class="font-semibold mb-2">Domain Information:</h3>
        <div class="bg-gray-100 p-4 rounded">
          <div v-for="(value, key) in domainInfo" :key="key" class="mb-2">
            <span class="font-medium">{{ formatKey(key) }}:</span>
            <span>{{ formatValue(value) }}</span>
          </div>
        </div>
        <button
          v-if="currentReportId"
          @click="downloadDomainReport"
          class="mt-2 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
        >
          Download Report
        </button>
      </div>
    </div>

    <!-- Username Search Section -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-2">Username Search</h2>
      <div class="flex gap-2">
        <input
          v-model="username"
          type="text"
          placeholder="Enter username"
          class="flex-1 p-2 border rounded"
        />
        <button
          @click="searchUsername"
          class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          :disabled="isSearching"
        >
          {{ isSearching ? 'Searching...' : 'Search' }}
        </button>
      </div>
      <div v-if="usernameResults" class="mt-4">
        <h3 class="font-semibold mb-2">Search Results:</h3>
        <div class="bg-gray-100 p-4 rounded">
          <div v-if="usernameResults.error" class="text-red-500 mb-2">
            {{ usernameResults.error }}
          </div>
          <div v-else>
            <p class="mb-2">Found {{ usernameResults.found_count }} profiles</p>
            <ul class="list-disc pl-5">
              <li v-for="profile in usernameResults.profiles" :key="profile" class="mb-1">
                <a :href="profile" target="_blank" class="text-blue-500 hover:underline">
                  {{ profile }}
                </a>
              </li>
            </ul>
          </div>
        </div>
        <button
          v-if="currentReportId"
          @click="downloadUsernameReport"
          class="mt-2 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
        >
          Download Report
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'NetworkIntelligence',
  data() {
    return {
      ipAddress: '',
      ipInfo: null,
      domain: '',
      domainInfo: null,
      username: '',
      usernameResults: null,
      isSearching: false,
      currentReportId: null
    };
  },
  methods: {
    formatKey(key) {
      return key.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ');
    },
    formatValue(value) {
      if (typeof value === 'object') {
        return JSON.stringify(value, null, 2);
      }
      return value;
    },
    async lookupIp() {
      try {
        const response = await axios.get(`/api/netint/ip?ip=${this.ipAddress}`);
        this.ipInfo = response.data;
        this.currentReportId = response.data.report_id;
      } catch (error) {
        console.error('Error looking up IP:', error);
        this.ipInfo = { error: error.response?.data?.error || 'Failed to lookup IP' };
      }
    },
    async analyzeDomain() {
      try {
        const response = await axios.get(`/api/netint/domain/analyze?domain=${this.domain}`);
        this.domainInfo = response.data;
        this.currentReportId = response.data.report_id;
      } catch (error) {
        console.error('Error analyzing domain:', error);
        this.domainInfo = { error: error.response?.data?.error || 'Failed to analyze domain' };
      }
    },
    async searchUsername() {
      if (!this.username.trim()) {
        this.usernameResults = { error: 'Please enter a username' };
        return;
      }

      this.isSearching = true;
      this.usernameResults = null;

      try {
        const response = await axios.post('/api/sherlock', {
          username: this.username.trim()
        });
        this.usernameResults = response.data;
        this.currentReportId = response.data.report_id;
      } catch (error) {
        console.error('Error searching username:', error);
        this.usernameResults = {
          error: error.response?.data?.error || 'Failed to search username'
        };
      } finally {
        this.isSearching = false;
      }
    },
    downloadIpReport() {
      if (this.currentReportId) {
        window.location.href = `/api/reports/${this.currentReportId}/download`;
      }
    },
    downloadDomainReport() {
      if (this.currentReportId) {
        window.location.href = `/api/reports/${this.currentReportId}/download`;
      }
    },
    downloadUsernameReport() {
      if (this.currentReportId) {
        window.location.href = `/api/reports/${this.currentReportId}/download`;
      }
    }
  }
};
</script>

<style scoped>
.container {
  max-width: 1200px;
}
</style> 