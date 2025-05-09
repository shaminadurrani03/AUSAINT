<template>
  <div class="network-intelligence">
    <h2 class="text-2xl font-bold mb-6">Network Intelligence</h2>
    
    <!-- IP Lookup Section -->
    <div class="mb-8">
      <h3 class="text-xl font-semibold mb-4">IP Lookup</h3>
      <div class="flex gap-4 mb-4">
        <input
          v-model="ipAddress"
          type="text"
          placeholder="Enter IP address (e.g., 8.8.8.8)"
          class="flex-1 p-2 border rounded"
          :class="{ 'border-red-500': ipError }"
        />
        <button
          @click="lookupIp"
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          :disabled="isLoading"
        >
          {{ isLoading ? 'Loading...' : 'Lookup IP' }}
        </button>
      </div>
      <div v-if="ipError" class="text-red-500 mb-4">{{ ipError }}</div>
      <div v-if="ipResult" class="bg-white p-4 rounded shadow">
        <h4 class="font-semibold mb-2">IP Information</h4>
        <div class="grid grid-cols-2 gap-4">
          <div v-for="(value, key) in ipResult" :key="key" class="p-2 bg-gray-50 rounded">
            <span class="font-medium">{{ formatKey(key) }}:</span>
            <span class="ml-2">{{ value }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Domain Analysis Section -->
    <div>
      <h3 class="text-xl font-semibold mb-4">Domain Analysis</h3>
      <div class="flex gap-4 mb-4">
        <input
          v-model="domain"
          type="text"
          placeholder="Enter domain (e.g., example.com)"
          class="flex-1 p-2 border rounded"
          :class="{ 'border-red-500': domainError }"
        />
        <button
          @click="analyzeDomain"
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          :disabled="isLoading"
        >
          {{ isLoading ? 'Analyzing...' : 'Analyze Domain' }}
        </button>
      </div>
      <div v-if="domainError" class="text-red-500 mb-4">{{ domainError }}</div>

      <!-- Domain Analysis Results -->
      <div v-if="domainResult" class="space-y-6">
        <!-- WHOIS Information -->
        <div class="bg-white p-4 rounded shadow">
          <h4 class="font-semibold mb-2">WHOIS Information</h4>
          <div class="grid grid-cols-2 gap-4">
            <div v-for="(value, key) in domainResult.whois" :key="key" class="p-2 bg-gray-50 rounded">
              <span class="font-medium">{{ formatKey(key) }}:</span>
              <span class="ml-2">{{ formatValue(value) }}</span>
            </div>
          </div>
        </div>

        <!-- Subdomains -->
        <div class="bg-white p-4 rounded shadow">
          <h4 class="font-semibold mb-2">Subdomains ({{ domainResult.subdomains.total_subdomains }})</h4>
          <div class="grid grid-cols-3 gap-2">
            <div v-for="subdomain in domainResult.subdomains.subdomains" :key="subdomain" class="p-2 bg-gray-50 rounded">
              {{ subdomain }}
            </div>
          </div>
        </div>

        <!-- DNS Records -->
        <div class="bg-white p-4 rounded shadow">
          <h4 class="font-semibold mb-2">DNS Records ({{ domainResult.dns_records.total_records }})</h4>
          <div class="space-y-2">
            <div v-for="(record, index) in domainResult.dns_records.records" :key="index" class="p-2 bg-gray-50 rounded">
              <div class="grid grid-cols-3 gap-4">
                <div><span class="font-medium">Name:</span> {{ record.name }}</div>
                <div><span class="font-medium">Type:</span> {{ record.type }}</div>
                <div><span class="font-medium">Value:</span> {{ record.value }}</div>
              </div>
            </div>
          </div>
        </div>
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
      domain: '',
      ipResult: null,
      domainResult: null,
      ipError: null,
      domainError: null,
      isLoading: false
    };
  },
  methods: {
    formatKey(key) {
      return key
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    },
    formatValue(value) {
      if (Array.isArray(value)) {
        return value.join(', ');
      }
      return value;
    },
    async lookupIp() {
      if (!this.ipAddress) {
        this.ipError = 'Please enter an IP address';
        return;
      }

      this.isLoading = true;
      this.ipError = null;
      this.ipResult = null;

      try {
        const response = await axios.get(`http://localhost:3000/api/netint/ip?ip=${this.ipAddress}`);
        this.ipResult = response.data;
      } catch (error) {
        this.ipError = error.response?.data?.error || 'Failed to lookup IP address';
      } finally {
        this.isLoading = false;
      }
    },
    async analyzeDomain() {
      if (!this.domain) {
        this.domainError = 'Please enter a domain';
        return;
      }

      this.isLoading = true;
      this.domainError = null;
      this.domainResult = null;

      try {
        const response = await axios.get(`http://localhost:3000/api/netint/domain/analyze?domain=${this.domain}`);
        this.domainResult = response.data;
      } catch (error) {
        this.domainError = error.response?.data?.error || 'Failed to analyze domain';
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.network-intelligence {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.grid {
  display: grid;
}

.grid-cols-2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.grid-cols-3 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.gap-2 {
  gap: 0.5rem;
}

.gap-4 {
  gap: 1rem;
}

.space-y-2 > * + * {
  margin-top: 0.5rem;
}

.space-y-6 > * + * {
  margin-top: 1.5rem;
}
</style> 