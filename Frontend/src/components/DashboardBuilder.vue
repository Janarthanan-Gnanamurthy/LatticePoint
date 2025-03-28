<template>
	<div class="container mx-auto p-4">
		<div class="flex justify-between items-center mb-4">
			<h1 class="text-3xl font-bold">Dashboard Builder</h1>
			<DeployDashboard 
				v-if="dashboardWidgets.length > 0" 
				:dashboardWidgets="dashboardWidgets" 
				:datasetInfo="{ headers: dataStore.headers, rows: dataStore.rows }"
			/>
		</div>
		
		<!-- Loading State -->
		<div v-if="!dataStore.headers.length" class="text-center py-8">
			<p class="text-gray-500">No data available. Please upload your data first.</p>
			<button 
				@click="router.push({ name: 'DataProcessor' })" 
				class="mt-4 btn btn-primary"
			>
				Go to Data Upload
			</button>
		</div>
		
		<!-- Main Layout -->
		<div v-else class="flex gap-4">
			<!-- Widget Selection Sidebar -->
			<div class="w-1/4 bg-white rounded-lg shadow p-4">
				<h2 class="text-xl font-semibold mb-4">Add Widgets</h2>
				
				<!-- AI Dashboard Generator -->
				<div class="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
					<h3 class="font-semibold text-blue-700 mb-2">AI Dashboard Generator</h3>
					<p class="text-sm text-gray-600 mb-2">Describe what you want to visualize and let AI create widgets for you.</p>
					<div class="space-y-2">
						<input 
							v-model="dashboardPrompt" 
							class="w-full p-2 border rounded"
							placeholder="E.g., Show sales by region and a table of top products"
							@keyup.enter="generateDashboard"
						/>
						<button 
							@click="generateDashboard" 
							class="w-full p-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors flex items-center justify-center"
							:disabled="isGenerating"
						>
							<span v-if="isGenerating">
								<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
									<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
									<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
								</svg>
								Generating...
							</span>
							<span v-else>Generate Dashboard</span>
						</button>
					</div>
				</div>
				
				<div class="my-4 border-t pt-4">
					<h3 class="font-semibold mb-2">Or Add Manually</h3>
				</div>
				
				<div class="space-y-2">
					<button 
						v-for="widget in availableWidgets" 
						:key="widget.type"
						class="flex items-center w-full p-2 rounded hover:bg-gray-100 transition-colors"
						@click="addWidget(widget.type)"
					>
						<component :is="widget.icon" class="w-5 h-5 mr-2" />
						{{ widget.label }}
					</button>
				</div>

				<!-- Widget Configuration -->
				<div v-if="selectedWidget" class="mt-4 border-t pt-4">
					<h3 class="font-semibold mb-2">Widget Settings</h3>
					<div class="space-y-4">
						<!-- Basic Settings -->
						<div>
							<label class="block text-sm font-medium mb-1">Title</label>
							<input 
								v-model="selectedWidget.config.title"
								class="w-full p-2 border rounded"
								@change="updateWidget(selectedWidget)"
							/>
						</div>

						<!-- Chart Specific Settings -->
						<template v-if="selectedWidget.type === 'chart'">
							<!-- Chart Type -->
							<div>
								<label class="block text-sm font-medium mb-1">Chart Type</label>
								<select 
									v-model="selectedWidget.config.chartType"
									class="w-full p-2 border rounded"
									@change="updateWidget(selectedWidget)"
								>
									<option value="bar">Bar Chart</option>
									<option value="line">Line Chart</option>
									<option value="pie">Pie Chart</option>
									<option value="scatter">Scatter Plot</option>
									<option value="radar">Radar Chart</option>
								</select>
							</div>

							<!-- X-Axis Configuration -->
							<div>
								<label class="block text-sm font-medium mb-1">X-Axis Column</label>
								<select 
									v-model="selectedWidget.config.xColumn"
									class="w-full p-2 border rounded"
									@change="updateWidget(selectedWidget)"
								>
									<option 
										v-for="(header, index) in dataStore.headers" 
										:key="index" 
										:value="index"
									>
										{{ header }}
									</option>
								</select>
							</div>

							<!-- Y-Axis Configuration -->
							<div>
								<label class="block text-sm font-medium mb-1">Y-Axis Columns</label>
								<select 
									v-model="selectedWidget.config.yColumns"
									class="w-full p-2 border rounded" 
									multiple
									size="5"
									@change="updateWidget(selectedWidget)"
								>
									<option 
										v-for="(header, index) in dataStore.headers" 
										:key="index" 
										:value="index"
										:disabled="!isNumericColumn(index)"
									>
										{{ header }} {{ !isNumericColumn(index) ? '(non-numeric)' : '' }}
									</option>
								</select>
								<p class="text-sm text-gray-500 mt-1">Hold Ctrl/Cmd to select multiple columns</p>
							</div>
						</template>

						<!-- Widget Size Settings -->
						<div>
							<label class="block text-sm font-medium mb-1">Widget Size</label>
							<select 
								v-model="selectedWidget.config.size"
								class="w-full p-2 border rounded"
								@change="updateWidget(selectedWidget)"
							>
								<option value="1">Small</option>
								<option value="2">Medium</option>
								<option value="3">Large</option>
								<option value="4">Full Width</option>
							</select>
						</div>
					</div>
				</div>
			</div>

			<!-- Dashboard Area -->
			<div class="w-3/4">
				<div v-if="!dashboardWidgets.length" 
					class="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-8 text-center"
				>
					<p class="text-gray-500">Add widgets using the sidebar to build your dashboard</p>
				</div>
				
				<div v-else class="grid grid-cols-4 gap-4">
					<div
						v-for="widget in dashboardWidgets"
						:key="widget.id"
						class="bg-white rounded-lg shadow relative transition-all duration-200"
						:class="[
							getWidgetSizeClass(widget),
							{'ring-2 ring-blue-500': selectedWidget?.id === widget.id}
						]"
						@click="selectWidget(widget)"
					>
						<!-- Widget Header -->
						<div class="p-3 border-b flex justify-between items-center">
							<h3 class="font-semibold">{{ widget.config.title }}</h3>
							<div class="flex gap-2">
								<button 
									@click.stop="removeWidget(widget.id)" 
									class="p-1 text-red-500 hover:text-red-700 rounded"
								>
									<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
									</svg>
								</button>
							</div>
						</div>
						
						<!-- Widget Content -->
						<div class="p-4">
							<component 
								:is="getWidgetComponent(widget)" 
								:widget="widget" 
								:headers="dataStore.headers"
								:rows="dataStore.rows"
								@update:widget="updateWidget"
							/>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { defineComponent } from 'vue';
import { useRouter } from 'vue-router';
import { useDataStore } from '@/stores/datasetStore';
import ChartWidget from './widgets/ChartWidget.vue';
import TableWidget from './widgets/TableWidget.vue';
import InsightWidget from './widgets/InsightWidget.vue';
import StatWidget from './widgets/StatWidget.vue';
import { apiClient } from '@/services/apiService';
import DeployDashboard from './DeployDashboard.vue';

export default defineComponent({
	name: 'DashboardBuilder',

	components: {
		ChartWidget,
		TableWidget,
		InsightWidget,
		StatWidget,
		DeployDashboard
	},

	setup() {
		const dataStore = useDataStore();
		const router = useRouter();
		return { dataStore, router };
	},

	data() {
		return {
			dashboardWidgets: [],
			selectedWidget: null,
			dashboardPrompt: '',
			isGenerating: false,
			availableWidgets: [
				{ type: 'chart', label: 'Chart Widget', icon: 'i-tabler-chart-bar' },
				{ type: 'table', label: 'Data Table', icon: 'i-tabler-table' },
				{ type: 'insight', label: 'Insight Card', icon: 'i-tabler-bulb' },
				{ type: 'stat', label: 'Statistics', icon: 'i-tabler-calculator' }
			]
		};
	},

	created() {
		this.loadDashboard();
	},

	methods: {
		isNumericColumn(columnIndex) {
			return this.dataStore.rows.some(row => 
				!isNaN(parseFloat(row[columnIndex])) && row[columnIndex] !== ''
			);
		},

		loadDashboard() {
			// Check if we have data in the store
			if (!this.dataStore.headers.length) {
				return;
			}

			// Load saved dashboard layout
			const savedLayout = localStorage.getItem('dashboardLayout');
			if (savedLayout) {
				try {
					this.dashboardWidgets = JSON.parse(savedLayout);
				} catch (error) {
					console.error('Error loading dashboard layout:', error);
				}
			}
		},

		addWidget(type) {
			// Find first numeric column for Y-axis if it's a chart
			let yColumns = [];
			if (type === 'chart') {
				const firstNumericColumn = this.dataStore.headers.findIndex((_, index) => 
					this.isNumericColumn(index)
				);
				if (firstNumericColumn !== -1) {
					yColumns = [firstNumericColumn];
				}
			}

			const widget = {
				id: `widget-${Date.now()}`,
				type,
				config: {
					title: `New ${type.charAt(0).toUpperCase() + type.slice(1)} Widget`,
					size: '2',
					chartType: type === 'chart' ? 'bar' : null,
					xColumn: 0,
					yColumns: yColumns,
				}
			};
			
			this.dashboardWidgets.push(widget);
			this.saveDashboard();
			this.selectWidget(widget);
		},

		removeWidget(widgetId) {
			this.dashboardWidgets = this.dashboardWidgets.filter(w => w.id !== widgetId);
			if (this.selectedWidget?.id === widgetId) {
				this.selectedWidget = null;
			}
			this.saveDashboard();
		},

		selectWidget(widget) {
			this.selectedWidget = widget;
		},

		updateWidget(widget) {
			const index = this.dashboardWidgets.findIndex(w => w.id === widget.id);
			if (index !== -1) {
				this.dashboardWidgets[index] = { ...widget };
				this.saveDashboard();
			}
		},

		getWidgetComponent(widget) {
			const componentMap = {
				chart: 'ChartWidget',
				table: 'TableWidget',
				insight: 'InsightWidget',
				stat: 'StatWidget'
			};
			return componentMap[widget.type] || 'div';
		},

		getWidgetSizeClass(widget) {
			const sizeMap = {
				'1': 'col-span-1',
				'2': 'col-span-2',
				'3': 'col-span-3',
				'4': 'col-span-4'
			};
			return sizeMap[widget.config.size || '2'];
		},

		saveDashboard() {
			localStorage.setItem('dashboardLayout', JSON.stringify(this.dashboardWidgets));
		},

		async generateDashboard() {
			if (!this.dashboardPrompt.trim() || this.isGenerating) return;
			
			this.isGenerating = true;
			try {
				// Convert data to the format expected by the backend
				const columns = this.dataStore.headers;
				const data = this.dataStore.rows.map(row => {
					const rowObj = {};
					row.forEach((value, index) => {
						rowObj[columns[index]] = value;
					});
					return rowObj;
				});
				
				const response = await apiClient.post('http://localhost:8000/api/generate-dashboard', {
					prompt: this.dashboardPrompt,
					columns: columns,
					data: data 
				});
				console.log(response);

				if (response.data && response.data.widgets) {
					// Add all generated widgets
					this.dashboardWidgets = response.data.widgets;
					
					// Save to localStorage
					this.saveDashboard();
					
					// Clear prompt
					this.dashboardPrompt = '';
				}
			} catch (error) {
				console.error('Error generating dashboard:', error);
				alert('Failed to generate dashboard. Please try again with a different prompt.');
			} finally {
				this.isGenerating = false;
			}
		}
	}
});
</script>