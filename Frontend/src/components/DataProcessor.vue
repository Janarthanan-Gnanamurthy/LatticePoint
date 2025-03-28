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
						<h4 class="text-md font-medium text-gray-700 mb-2">
								{{ files[index] && files[index].name ? files[index].name : 
									(files[index] ? 'Transformed Data' : 'File ' + (index + 1)) }}
						</h4>
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
				<div v-if="processedData.type === 'visualization'" class="card-body p-6">
						<div class="chart-wrapper bg-white rounded-lg shadow p-4">
								<div class="chart-container">
										<canvas ref="chartCanvas"></canvas>
								</div>
						</div>
						<div class="mt-4 flex justify-end gap-4">
							<button @click="continueModification" class="btn btn-secondary">
								<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
									<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clip-rule="evenodd" />
								</svg>
								Continue Modification
							</button>
							<button @click="downloadData" class="btn btn-primary">
								<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
									<path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
								</svg>
								Download Data
							</button>
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
						<div class="mt-4 flex justify-end gap-4">
							<button @click="continueModification" class="btn btn-secondary">
								<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
									<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clip-rule="evenodd" />
								</svg>
								Continue Modification
							</button>
							<button @click="downloadData" class="btn btn-primary">
								<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
									<path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
								</svg>
								Download Data
							</button>
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
						<div class="mt-4 flex justify-end gap-4">
							<button @click="continueModification" class="btn btn-secondary">
								<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
									<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clip-rule="evenodd" />
								</svg>
								Continue Modification
							</button>
							<button @click="downloadData" class="btn btn-primary">
								<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
									<path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
								</svg>
								Download Data
							</button>
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

	created() {
		// Initialize the dataStore
		this.dataStore = useDataStore();
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

		try {
			// Use direct store import
			const store = useDataStore();
			console.log('Store accessed directly in goToDashboard', store);
			
			// Store the data directly in the store state
			store.$state.files = this.files;
			store.$state.previewData = this.previewData;
			store.$state.headers = this.headers;
			store.$state.rows = this.rows;
			
			// Save to sessionStorage manually
			sessionStorage.setItem('dataStore', JSON.stringify({
				files: this.files,
				previewData: this.previewData,
				headers: this.headers,
				rows: this.rows,
				processedData: null
			}));
			
			console.log('Data stored for dashboard builder');
			
			// Navigate to dashboard builder
			this.router.push({ name: 'DashboardBuilder' });
		} catch (error) {
			console.error('Error in goToDashboard:', error);
			alert('An error occurred while preparing the dashboard. Please try again.');
		}
	},


		async processData() {
			if (this.files.length === 0 || !this.userPrompt) {
				alert('Please upload files and enter a prompt.');
				return;
			}

			this.loading = true;
			this.processedData = null;

			try {
				console.log('Processing data with prompt:', this.userPrompt);
				
				const formData = new FormData();
				
				// Check if we're using real files or transformed data
				const isRealFiles = this.files.some(file => file.size > 0);
				
				if (isRealFiles) {
					// Original flow with real files
					this.files.forEach(file => {
						formData.append('files', file);
					});
				} else {
					// We're working with transformed data
					console.log('Using transformed data from previous operations');
					
					// Create a CSV representation of our data
					const headers = this.headers;
					const csvContent = [
						headers.join(','),
						...this.rows.map(row => 
							headers.map(header => 
								typeof row[header] === 'undefined' ? '' : row[header]
							).join(',')
						)
					].join('\n');
					
					// Create a file from the CSV content
					const transformedFile = new File([csvContent], 'transformed_data.csv', { type: 'text/csv' });
					formData.append('files', transformedFile);
					console.log('Created transformed file:', transformedFile);
				}
				
				formData.append('prompt', this.userPrompt);

				const response = await fetch('http://localhost:8000/api/process', {
					method: 'POST',
					body: formData,
				});

				if (!response.ok) {
					throw new Error(`HTTP error! status: ${response.status}`);
				}

				const result = await response.json();
				console.log('Received data from backend:', result);
				this.processedData = result;

				// If it's a visualization, create the chart
				if (result.type === 'visualization') {
					console.log('Visualization data:', result.visualization);
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
			}

			try {
				const canvas = this.$refs.chartCanvas;
				if (!canvas) {
					console.error('Chart canvas element not found');
					return;
				}

				const ctx = canvas.getContext('2d');
				if (!ctx) {
					console.error('Chart canvas context not found');
					return;
				}

				const chartData = this.processedData?.visualization;
				console.log('Chart data before creation:', chartData);
				
				if (!chartData) {
					console.error('No visualization data available');
					return;
				}

				// Wait for the next tick to ensure canvas is ready
				await this.$nextTick();

				// Ensure proper canvas dimensions
				canvas.style.height = '400px';
				canvas.style.width = '100%';

				// Create chart configuration
				const chartConfig = {
					type: chartData.type,
					data: {
						labels: chartData.data.labels,
						datasets: chartData.data.datasets.map(dataset => ({
							...dataset,
							backgroundColor: dataset.backgroundColor,
							borderColor: dataset.borderColor,
							borderWidth: 1,
							barThickness: 50, // Add fixed bar thickness
							maxBarThickness: 75, // Maximum bar thickness
							minBarLength: 2 // Minimum bar length in pixels
						}))
					},
					options: {
						responsive: true,
						maintainAspectRatio: false,
						animation: {
							duration: 1000
						},
						plugins: {
							legend: {
								position: 'top',
								labels: {
									font: {
										size: 12
									}
								}
							},
							title: {
								display: true,
								text: chartData.options.plugins.title.text,
								font: {
									size: 16,
									weight: 'bold'
								}
							}
						},
						scales: {
							y: {
								beginAtZero: true,
								ticks: {
									callback: (value) => this.formatCurrency(value),
									font: {
										size: 11
									}
								},
								grid: {
									display: true,
									drawBorder: true,
									drawOnChartArea: true
								}
							},
							x: {
								grid: {
									display: false
								},
								ticks: {
									font: {
										size: 11
									}
								}
							}
						}
					}
				};

				console.log('Final chart configuration:', chartConfig);
				
				// Create new chart instance
				this.chartInstance = new Chart(ctx, chartConfig);

			} catch (error) {
				console.error('Error creating chart:', error);
				console.error('Error details:', error.message);
			}
		},
		formatCurrency(value) {
			return new Intl.NumberFormat('en-IN', {
				style: 'currency',
				currency: 'INR',
				maximumFractionDigits: 0,
			}).format(value);
		},
		downloadData() {
			let dataToDownload;
			let filename = 'transformed_data.csv';

			if (this.processedData.type === 'visualization') {
				// For visualization data, we'll download the raw data
				dataToDownload = this.processedData.visualization.data.datasets[0].data;
				filename = 'visualization_data.csv';
			} else if (this.processedData.type === 'statistical') {
				// For statistical data
				dataToDownload = this.processedData.data;
				filename = 'statistical_analysis.csv';
			} else {
				// For transformed data
				dataToDownload = this.processedData.data;
				filename = 'transformed_data.csv';
			}

			// Convert data to CSV format
			const headers = Object.keys(dataToDownload[0]);
			const csvContent = [
				headers.join(','),
				...dataToDownload.map(row => 
					headers.map(header => 
						JSON.stringify(row[header])
					).join(',')
				)
			].join('\n');

			// Create and trigger download
			const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
			const link = document.createElement('a');
			const url = URL.createObjectURL(blob);
			link.setAttribute('href', url);
			link.setAttribute('download', filename);
			link.style.visibility = 'hidden';
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);
		},
		continueModification() {
			console.log('Continue Modification clicked', this.processedData);
			
			try {
				// Use the direct store import instead of this.dataStore
				const store = useDataStore();
				console.log('Store accessed directly using useDataStore()', store);
				
				// Try setting the data directly using state management
				store.$state.processedData = this.processedData;
				console.log('Data stored directly in Pinia store state');
				
				// Clear the current prompt to allow for new modifications
				this.userPrompt = '';
				
				// Handle different data types
				if (this.processedData.type === 'visualization') {
					// For visualization, extract the data from the chart
					const datasets = this.processedData.visualization.data.datasets;
					const labels = this.processedData.visualization.data.labels;
					
					console.log('Visualization data before conversion:', datasets, labels);
					
					// Create a format that can be displayed in the preview table
					const data = labels.map((label, index) => {
						const row = { Category: label };
						datasets.forEach((dataset, datasetIndex) => {
							row[dataset.label || `Series ${datasetIndex + 1}`] = dataset.data[index];
						});
						return row;
					});
					
					const columns = ['Category', ...datasets.map((d, i) => d.label || `Series ${i + 1}`)];
					
					console.log('Converted visualization data:', data);
					console.log('Columns:', columns);
					
					// Create a single new file representation
					this.files = [new File([], 'visualization_data.csv')];
					
					// Update preview data - replace all existing preview data
					this.previewData = [{
						headers: columns,
						displayedRows: data.slice(0, 5),
						totalRows: data.length
					}];
					
					this.headers = columns;
					this.rows = data;
					
					console.log('Updated preview data for visualization', this.previewData);
				} 
				else if (this.processedData.type === 'statistical') {
					// For statistical data
					const columns = Object.keys(this.processedData.data[0] || {});
					
					console.log('Statistical data before conversion:', this.processedData.data);
					console.log('Columns:', columns);
					
					// Create a single new file representation
					this.files = [new File([], 'statistical_data.csv')];
					
					// Update preview data - replace all existing preview data
					this.previewData = [{
						headers: columns,
						displayedRows: this.processedData.data.slice(0, 5),
						totalRows: this.processedData.data.length
					}];
					
					this.headers = columns;
					this.rows = this.processedData.data;
					
					console.log('Updated preview data for statistical', this.previewData);
				} 
				else {
					// For transformed data
					console.log('Transformed data before conversion:', this.processedData.data);
					console.log('Columns:', this.processedData.columns);
					
					// Create a single new file representation
					this.files = [new File([], 'transformed_data.csv')];
					
					// Update preview data - replace all existing preview data
					this.previewData = [{
						headers: this.processedData.columns,
						displayedRows: this.processedData.data.slice(0, 5),
						totalRows: this.processedData.data.length
					}];
					
					this.headers = this.processedData.columns;
					this.rows = this.processedData.data;
					
					console.log('Updated preview data for transformed', this.previewData);
				}
				
				// Force the reactivity update using nextTick
				this.$nextTick(() => {
					console.log('After nextTick - current previewData:', this.previewData);
				});
				
				// Clear the processed data to hide the results section
				this.processedData = null;
				
				// Scroll to the prompt input section and data preview
				this.$nextTick(() => {
					// First scroll to the data preview section
					const previewSection = document.querySelector('.bg-white.rounded-lg.shadow-md.p-6.mb-6');
					if (previewSection) {
						console.log('Scrolling to preview section');
						previewSection.scrollIntoView({ behavior: 'smooth' });
						
						// Then, after a short delay, scroll to the prompt section
						setTimeout(() => {
							const promptSection = document.querySelector('.textarea');
							if (promptSection) {
								console.log('Scrolling to prompt section');
								promptSection.scrollIntoView({ behavior: 'smooth' });
								promptSection.focus();
							} else {
								console.error('Prompt textarea not found');
							}
						}, 500);
					} else {
						console.error('Preview section not found');
						// Just scroll to prompt if preview not found
						const promptSection = document.querySelector('.textarea');
						if (promptSection) {
							promptSection.scrollIntoView({ behavior: 'smooth' });
							promptSection.focus();
						}
					}
				});
				
			} catch (error) {
				console.error('Error in continueModification:', error);
				console.error('Error stack:', error.stack);
				alert('An error occurred while setting up for continued modifications. Please try again.');
			}
		},
	},

	mounted() {
		console.log('Component mounted');
		
		try {
			// Use direct store import
			const store = useDataStore();
			console.log('Store accessed directly in mounted', store);
			
			// Check if we have processed data in the store
			const storeProcessedData = store.$state.processedData;
			if (storeProcessedData) {
				console.log('Found processed data in store:', storeProcessedData);
				
				// Handle it based on the type
				if (storeProcessedData.type === 'visualization') {
					const datasets = storeProcessedData.visualization.data.datasets;
					const labels = storeProcessedData.visualization.data.labels;
					
					// Create a format that can be displayed in the preview table
					const data = labels.map((label, index) => {
						const row = { Category: label };
						datasets.forEach((dataset, datasetIndex) => {
							row[dataset.label || `Series ${datasetIndex + 1}`] = dataset.data[index];
						});
						return row;
					});
					
					const columns = ['Category', ...datasets.map((d, i) => d.label || `Series ${i + 1}`)];
					
					this.previewData = [{
						headers: columns,
						displayedRows: data.slice(0, 5),
						totalRows: data.length
					}];
					
					this.headers = columns;
					this.rows = data;
					
					// Create dummy File objects
					this.files = [new File([], 'visualization_data.csv')];
					
					console.log('Initialized from visualization data in store');
				} 
				else if (storeProcessedData.type === 'statistical') {
					const columns = Object.keys(storeProcessedData.data[0] || {});
					
					this.previewData = [{
						headers: columns,
						displayedRows: storeProcessedData.data.slice(0, 5),
						totalRows: storeProcessedData.data.length
					}];
					
					this.headers = columns;
					this.rows = storeProcessedData.data;
					
					// Create dummy File objects
					this.files = [new File([], 'statistical_data.csv')];
					
					console.log('Initialized from statistical data in store');
				} 
				else if (storeProcessedData.type === 'transformed') {
					this.previewData = [{
						headers: storeProcessedData.columns,
						displayedRows: storeProcessedData.data.slice(0, 5),
						totalRows: storeProcessedData.data.length
					}];
					
					this.headers = storeProcessedData.columns;
					this.rows = storeProcessedData.data;
					
					// Create dummy File objects
					this.files = [new File([], 'transformed_data.csv')];
					
					console.log('Initialized from transformed data in store');
				}
				
				// Clear the processed data from the store
				store.$state.processedData = null;
			}
		} catch (error) {
			console.error('Error in mounted hook:', error);
		}
		
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
		},
		previewData: {
			handler(newValue) {
				console.log('previewData changed:', newValue);
			},
			deep: true
		}
	}
};
</script>

<style scoped>
.chart-wrapper {
	width: 100%;
	margin: 0 auto;
}

.chart-container {
	position: relative;
	height: 400px;
	width: 100%;
	margin: 0 auto;
}

canvas {
	background-color: white;
}
</style>