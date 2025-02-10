<template>
<div class="container mx-auto p-4">
		<h1 class="text-3xl font-bold mb-4">AI Data Analysis and Visualization</h1>
		<div class="space-y-6">
		<!-- File Upload Section -->
		<div class="bg-white rounded-lg shadow-md p-6">
				<div class="flex items-center justify-center w-full">
				<label class="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
						<div class="flex flex-col items-center justify-center pt-5 pb-6">
						<svg class="w-8 h-8 mb-4 text-gray-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
								<path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
						</svg>
						<p class="mb-2 text-sm text-gray-500">
								<span class="font-semibold">Click to upload</span> or drag and drop
						</p>
						<p class="text-xs text-gray-500">CSV files only (multiple files allowed)</p>
						</div>
						<input 
							type="file" 
							class="hidden" 
							@change="handleFileUpload" 
							accept=".csv" 
							multiple
						/>
				</label>
				</div>

				<!-- File Selection Info -->
				<div v-if="files.length > 0" class="mt-4 space-y-2">
					<div v-for="(file, index) in files" :key="index" class="flex items-center justify-between text-sm text-gray-600 bg-gray-50 p-2 rounded">
						<div class="flex items-center gap-2">
							<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-500" viewBox="0 0 20 20" fill="currentColor">
								<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
							</svg>
							<span>{{ file.name }}</span>
						</div>
						<button @click="removeFile(index)" class="text-red-500 hover:text-red-700">
							<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
								<path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
							</svg>
						</button>
					</div>
				</div>
		</div>

		<!-- Data Preview -->
		<div v-if="previewData.length > 0" class="bg-white rounded-lg shadow-md p-6 mb-6 overflow-x-auto">
				<h3 class="text-lg font-semibold text-gray-900 mb-4">Data Preview</h3>
				<div v-for="(fileData, index) in previewData" :key="index" class="mb-6">
					<h4 class="text-md font-medium text-gray-700 mb-2">{{ files[index].name }}</h4>
					<div class="overflow-x-auto">
						<table class="table table-zebra w-full">
							<thead>
								<tr class="bg-gray-100">
									<th v-for="header in fileData.headers" :key="header" class="px-4 py-2 text-left text-sm font-medium text-gray-900">
										{{ header }}
									</th>
								</tr>
							</thead>
							<tbody>
								<tr v-for="(row, rowIndex) in fileData.displayedRows" :key="rowIndex" class="border-t border-gray-200">
									<td v-for="(cell, cellIndex) in row" :key="cellIndex" class="px-4 py-2 text-sm text-gray-600">
										{{ cell }}
									</td>
								</tr>
							</tbody>
						</table>
					</div>
					<div class="mt-2 text-sm text-gray-500">
						Showing {{ fileData.displayedRows.length }} of {{ fileData.totalRows }} rows
					</div>
				</div>
		</div>

		<!-- Prompt Input Section -->
		<div class="bg-white rounded-lg shadow-md p-6">
				<h3 class="text-lg font-semibold text-gray-900 mb-4">Process Your Data</h3>
				<div class="space-y-4">
				<div class="space-y-2">
						<label class="text-sm text-gray-600">Enter your request:</label>
						<textarea 
						v-model="userPrompt" 
						placeholder="e.g., 'Show me a bar chart of combined sales by region' or 'Calculate the average revenue across all datasets'"
						class="textarea textarea-bordered w-full h-32 text-sm"
						></textarea>
						<p class="text-xs text-gray-500">
						You can ask for data transformations, visualizations, or statistical analysis across multiple datasets.
						</p>
				</div>
				
				<div class="flex gap-4">
						<button 
						@click="processData" 
						class="btn btn-primary flex-1"
						:disabled="files.length === 0 || !userPrompt || loading"
						>
						<span class="flex items-center gap-2">
								<svg v-if="!loading" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
								<path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd" />
								</svg>
								<div v-else class="loading loading-spinner loading-sm"></div>
								{{ loading ? 'Processing...' : 'Process Data' }}
						</span>
						</button>
						<!-- New Button to Navigate to Dashboard Builder -->
						<button 
							@click="goToDashboard" 
							class="btn btn-secondary flex-1"
							:disabled="!files.length || loading"
						>
							Build Dashboard
						</button>
				</div>
				</div>
		</div>

		<!-- Loading Overlay -->
		<div v-if="loading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
				<div class="bg-white p-6 rounded-lg shadow-lg">
				<div class="loading loading-spinner loading-lg"></div>
				<p class="mt-4 text-gray-700">Processing your request...</p>
				</div>
		</div>

		<!-- Results Section -->
		<div v-if="processedData" class="card bg-base-100 shadow-xl">
				<!-- Visualization Result -->
				<div v-if="processedData.type === 'visualization'" class="card-body">
						<h2 class="card-title">{{ processedData.visualization?.options?.plugins?.title?.text || 'Visualization' }}</h2>
						<div class="chart-container">
								<canvas ref="chartCanvas"></canvas>
						</div>
				</div>
				
				<!-- Statistical Result -->
				<div v-else-if="processedData.type === 'statistical'" class="card-body">
						<h2 class="card-title">Statistical Analysis Results</h2>
						<div class="overflow-x-auto">
								<table class="table w-full">
										<thead>
												<tr>
														<th v-for="column in Object.keys(processedData.data[0] || {})" :key="column" class="px-4 py-2 text-left">
																{{ column }}
														</th>
												</tr>
										</thead>
										<tbody>
												<tr v-for="(row, index) in processedData.data" :key="index">
														<td v-for="column in Object.keys(row)" :key="column" class="px-4 py-2">
																{{ row[column] }}
														</td>
												</tr>
										</tbody>
								</table>
						</div>
				</div>
				
				<!-- Transformation Result -->
				<div v-else class="card-body">
						<h2 class="card-title">Transformed Data</h2>
						<div class="overflow-x-auto">
								<table class="table w-full">
										<thead>
												<tr>
														<th v-for="column in processedData.columns" :key="column" class="px-4 py-2 text-left">
																{{ column }}
														</th>
												</tr>
										</thead>
										<tbody>
												<tr v-for="(row, index) in processedData.data" :key="index">
														<td v-for="column in processedData.columns" :key="column" class="px-4 py-2">
																{{ row[column] }}
														</td>
												</tr>
										</tbody>
								</table>
						</div>
				</div>
		</div>
		</div>
</div>
</template>

<script>
import Chart from 'chart.js/auto';
import { nextTick } from 'vue';
import * as XLSX from 'xlsx';
import { useDataStore } from '@/stores/datasetStore';
import { useRouter } from 'vue-router';

export default {
	name: "DataProcessor",
	data() {
		return {
			files: [],
			fileContent: '',
			previewData: [],
			headers: [],
			rows: [],
			userPrompt: '',
			loading: false,
			processedData: null,
			chartInstance: null
		};
	},

	setup() {
    const dataStore = useDataStore();
    const router = useRouter();
    return { dataStore, router };
  },

	methods: {
		handleFileUpload(event) {
      const newFiles = Array.from(event.target.files);
      
      // Validate file types
      const invalidFiles = newFiles.filter(file => !file.name.toLowerCase().endsWith('.csv'));
      if (invalidFiles.length > 0) {
        alert('Only CSV files are supported');
        return;
      }

      this.files = [...this.files, ...newFiles];
      this.loadPreviewData(newFiles);
    },

    loadPreviewData(newFiles) {
      newFiles.forEach(file => {
        const reader = new FileReader();
        reader.onload = (e) => {
          const content = e.target.result;
          const lines = content.split('\n');
          const headers = this.headers = lines[0].split(',');
          const rows = this.rows = lines.slice(1)
            .filter(line => line.trim())
            .map(line => line.split(','));
          
          this.previewData.push({
            headers,
            displayedRows: rows.slice(0, 5),
            totalRows: rows.length
          });
        };
        reader.readAsText(file);
      });
    },

    removeFile(index) {
      this.files.splice(index, 1);
      this.previewData.splice(index, 1);
      
      // If no files remain, clear the headers and rows
      if (this.files.length === 0) {
        this.headers = [];
        this.rows = [];
      }
    },

    goToDashboard() {
      if (!this.files.length) {
        alert('Please upload a file first.');
        return;
      }

      // Store the data in Pinia
      this.dataStore.setData(
        this.files,
        this.previewData,
        this.headers,
        this.rows
      );

      // Navigate to dashboard builder
      this.router.push({ name: 'DashboardBuilder' });
    },


		async processData() {
			if (this.files.length === 0 || !this.userPrompt) {
				alert('Please upload files and enter a prompt.');
				return;
			}

			this.loading = true;
			this.processedData = null;

			try {
				const formData = new FormData();
				this.files.forEach(file => {
					formData.append('files', file);
				});
				formData.append('prompt', this.userPrompt);

				const response = await fetch('http://localhost:8000/process', {
					method: 'POST',
					body: formData,
				});

				if (!response.ok) {
					throw new Error(`HTTP error! status: ${response.status}`);
				}

				const result = await response.json();
				this.processedData = result;

				// If it's a visualization, create the chart
				if (result.type === 'visualization') {
					this.$nextTick(() => this.updateChart());
				}
			} catch (error) {
				console.error('Error processing data:', error);
				alert('An error occurred while processing your request. Please try again.');
			} finally {
				this.loading = false;
			}
		},

		async updateChart() {
			if (this.chartInstance) {
				this.chartInstance.destroy();
				this.chartInstance = null;
			}
			// if (!this.isDataValid) return;
			try {
				const ctx = this.$refs.chartCanvas?.getContext('2d');
				if (!ctx) return;
				const chartConfig = JSON.parse(JSON.stringify(this.processedData.visualization));
				chartConfig.options = {
				...chartConfig.options,
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					...chartConfig.options.plugins,
					tooltip: {
					callbacks: {
						label: (context) => `Revenue: ${this.formatCurrency(context.raw)}`,
					},
					},
				},
				scales: {
					...chartConfig.options.scales,
					y: {
					...chartConfig.options.scales.y,
					ticks: {
						callback: (value) => this.formatCurrency(value),
					},
					},
				},
				};
				this.chartInstance = new Chart(ctx, chartConfig);
			} catch (error) {
				console.error('Error creating chart:', error);
				this.$emit('chart-error', error);
			}
			},
		formatCurrency(value) {
			return new Intl.NumberFormat('en-IN', {
				style: 'currency',
				currency: 'INR',
				maximumFractionDigits: 0,
			}).format(value);
		},
	},

	mounted() {
		if (this.processedData?.visualization) {
			this.updateChart();
		}
	},

	beforeUnmount() {
		if (this.chartInstance) {
			this.chartInstance.destroy();
		}
	},

	watch: {
		'processedData.visualization': {
			handler() {
				nextTick(() => this.updateChart());
			},
			deep: true
		}
	}
};
</script>

<style scoped>
.chart-container {
	position: relative;
	height: 400px;
	width: 100%;
}
</style>