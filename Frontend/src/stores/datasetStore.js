// stores/dataStore.js
import { defineStore } from 'pinia'

export const useDataStore = defineStore('data', {
  state: () => ({
    files: [],
    previewData: [],
    headers: [],
    rows: []
  }),
  
  actions: {
    setData(files, previewData, headers, rows) {
      this.files = files
      this.previewData = previewData
      this.headers = headers
      this.rows = rows
    },
    
    clearData() {
      this.files = []
      this.previewData = []
      this.headers = []
      this.rows = []
    }
  }
})