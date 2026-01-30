// Preload Script für sichere Kommunikation zwischen Renderer und Main Process
// Wird später für native Funktionen wie Datei-Dialoge verwendet

const { contextBridge, ipcRenderer } = require('electron');

// Sichere API für Renderer-Prozess bereitstellen
contextBridge.exposeInMainWorld('electronAPI', {
    // Platzhalter für zukünftige native Funktionen
    platform: process.platform,

    // Beispiel: Datei-Dialog öffnen (für späteren CSV-Import)
    // openFileDialog: () => ipcRenderer.invoke('open-file-dialog'),

    // App-Info
    getAppVersion: () => ipcRenderer.invoke('get-app-version')
});

console.log('✅ Electron Preload geladen');
