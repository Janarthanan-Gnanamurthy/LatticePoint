<template>
  <div class="deploy-dashboard">
    <button 
      @click="openDeployModal" 
      class="btn btn-primary flex items-center"
      :disabled="isDeploying"
    >
      <svg v-if="isDeploying" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7l4-4m0 0l4 4m-4-4v18"></path>
      </svg>
      {{ isDeploying ? 'Deploying...' : 'Share Dashboard' }}
    </button>

    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-xl font-bold mb-4">Share Your Dashboard</h3>
        
        <div v-if="deploymentStage === 'initial'">
          <p class="mb-4">Create a public link to share your dashboard with others.</p>
          <div class="mb-4">
            <label class="block text-sm font-medium mb-1">Dashboard Name</label>
            <input 
              v-model="dashboardName" 
              class="w-full p-2 border rounded"
              placeholder="My Awesome Dashboard"
            />
          </div>
          <div class="flex justify-end gap-2">
            <button @click="closeModal" class="px-4 py-2 border rounded hover:bg-gray-100">Cancel</button>
            <button @click="deployDashboard" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Deploy</button>
          </div>
        </div>

        <div v-else-if="deploymentStage === 'deploying'" class="text-center py-6">
          <svg class="animate-spin mx-auto h-10 w-10 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p class="mt-4 text-lg">Setting up your dashboard...</p>
          <p class="text-sm text-gray-500 mt-2">This may take a moment.</p>
        </div>

        <div v-else-if="deploymentStage === 'success'" class="py-4">
          <div class="flex items-center justify-center mb-4">
            <svg class="w-10 h-10 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </div>
          <h4 class="text-lg font-semibold text-center mb-4">Dashboard Published!</h4>
          
          <div class="bg-gray-50 p-3 rounded mb-4">
            <label class="block text-sm font-medium mb-1">Share this link:</label>
            <div class="flex">
              <input 
                ref="shareUrlInput"
                readonly
                :value="deployedUrl" 
                class="w-full p-2 border rounded-l bg-white"
              />
              <button 
                @click="copyShareUrl" 
                class="px-3 py-2 bg-gray-200 hover:bg-gray-300 rounded-r border-t border-r border-b"
              >
                <svg v-if="!copied" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"></path>
                </svg>
                <svg v-else class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
              </button>
            </div>
          </div>
          
          <div class="flex justify-end">
            <button @click="closeModal" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Done</button>
          </div>
        </div>

        <div v-else-if="deploymentStage === 'error'" class="py-4">
          <div class="flex items-center justify-center mb-4">
            <svg class="w-10 h-10 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </div>
          <h4 class="text-lg font-semibold text-center mb-2">Deployment Failed</h4>
          <p class="text-center text-gray-600 mb-4">{{ errorMessage }}</p>
          
          <div class="flex justify-end">
            <button @click="closeModal" class="px-4 py-2 border rounded hover:bg-gray-100 mr-2">Close</button>
            <button @click="resetDeployment" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Try Again</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import { apiClient } from '@/services/apiService';

export default defineComponent({
  name: 'DeployDashboard',
  
  props: {
    dashboardWidgets: {
      type: Array,
      required: true
    },
    datasetInfo: {
      type: Object,
      required: true
    }
  },
  
  data() {
    return {
      showModal: false,
      isDeploying: false,
      deploymentStage: 'initial', // 'initial', 'deploying', 'success', 'error'
      dashboardName: '',
      deployedUrl: '',
      errorMessage: '',
      copied: false
    };
  },
  
  methods: {
    openDeployModal() {
      this.showModal = true;
      this.deploymentStage = 'initial';
      this.dashboardName = '';
    },
    
    closeModal() {
      this.showModal = false;
    },
    
    resetDeployment() {
      this.deploymentStage = 'initial';
    },
    
    async deployDashboard() {
      if (!this.dashboardName.trim()) {
        this.errorMessage = 'Please enter a dashboard name';
        this.deploymentStage = 'error';
        return;
      }
      
      // Check if dataset has data
      const hasData = this.datasetInfo && 
                      this.datasetInfo.headers && 
                      this.datasetInfo.headers.length > 0 && 
                      this.datasetInfo.rows && 
                      this.datasetInfo.rows.length > 0;
      
      if (!hasData) {
        if (!confirm('This dashboard appears to have no data. Widgets will appear empty in the shared view. Continue anyway?')) {
          return;
        }
      }
      
      this.deploymentStage = 'deploying';
      this.isDeploying = true;
      
      try {
        // Prepare dashboard data
        const dashboardData = {
          name: this.dashboardName.trim(),
          widgets: this.dashboardWidgets,
          dataset: {
            headers: this.datasetInfo.headers,
            rows: this.datasetInfo.rows
          }
        };
        
        // Deploy dashboard to backend service
        const response = await apiClient.post('http://localhost:8000/api/deploy-dashboard', dashboardData);
        
        // Set the deployed URL
        this.deployedUrl = response.data.deployUrl;
        this.deploymentStage = 'success';
      } catch (error) {
        console.error('Error deploying dashboard:', error);
        this.errorMessage = error.response?.data?.message || 'Failed to deploy dashboard. Please try again.';
        this.deploymentStage = 'error';
      } finally {
        this.isDeploying = false;
      }
    },
    
    copyShareUrl() {
      const urlInput = this.$refs.shareUrlInput;
      urlInput.select();
      document.execCommand('copy');
      
      this.copied = true;
      setTimeout(() => {
        this.copied = false;
      }, 2000);
    }
  }
});
</script> 