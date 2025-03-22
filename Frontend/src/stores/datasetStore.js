import { defineStore } from 'pinia'

export const useDataStore = defineStore('data', {
  state: () => {
    // Try to load initial state from sessionStorage
    const storedData = sessionStorage.getItem('dataStore')
    return storedData ? JSON.parse(storedData) : {
      files: [],
      previewData: [],
      headers: [],
      rows: []
    }
  },
  
  actions: {
    setData(files, previewData, headers, rows) {
      this.files = files
      this.previewData = previewData
      this.headers = headers
      this.rows = rows
      
      // Save to sessionStorage
      sessionStorage.setItem('dataStore', JSON.stringify({
        files: this.files,
        previewData: this.previewData,
        headers: this.headers,
        rows: this.rows
      }))
    },
    
    clearData() {
      this.files = []
      this.previewData = []
      this.headers = []
      this.rows = []
      
      // Clear from sessionStorage
      sessionStorage.removeItem('dataStore')
    }
  }
})