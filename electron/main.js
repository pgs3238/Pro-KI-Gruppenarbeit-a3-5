const { app, BrowserWindow, shell, dialog } = require('electron');
const { spawn, execSync } = require('child_process');
const path = require('path');
const http = require('http');
const fs = require('fs');

let mainWindow = null;
let pythonProcess = null;

const SERVER_PORT = 8000;
const SERVER_URL = `http://127.0.0.1:${SERVER_PORT}`;

// Ermittelt den Projekt-Root basierend auf dem Ausführungskontext
function getProjectRoot() {
    if (app.isPackaged) {
        // Bei gepackter App: resources/app.asar oder resources/app
        return path.join(process.resourcesPath, 'app');
    } else {
        // Bei Dev: projektordner
        return path.join(__dirname, '..');
    }
}

// Prüft ob Python verfügbar ist
function checkPython() {
    try {
        execSync('python --version', { stdio: 'ignore' });
        return 'python';
    } catch {
        try {
            execSync('python3 --version', { stdio: 'ignore' });
            return 'python3';
        } catch {
            return null;
        }
    }
}

// Prüft ob der Server bereit ist
function waitForServer(maxAttempts = 30) {
    return new Promise((resolve, reject) => {
        let attempts = 0;

        const checkServer = () => {
            attempts++;
            console.log(`🔄 Warte auf Server... (Versuch ${attempts}/${maxAttempts})`);

            const req = http.get(SERVER_URL, (res) => {
                if (res.statusCode === 200) {
                    console.log('✅ Server ist bereit!');
                    resolve();
                } else {
                    retry();
                }
            });

            req.on('error', () => retry());
            req.setTimeout(1000, () => {
                req.destroy();
                retry();
            });
        };

        const retry = () => {
            if (attempts < maxAttempts) {
                setTimeout(checkServer, 1000);
            } else {
                reject(new Error('Server konnte nicht gestartet werden'));
            }
        };

        checkServer();
    });
}

// Startet den Python Backend-Server
function startPythonServer() {
    const projectRoot = getProjectRoot();
    console.log('📁 Projekt-Root:', projectRoot);
    console.log('📁 App gepackt:', app.isPackaged);
    console.log('📁 Resources:', process.resourcesPath);

    // Prüfe ob Python verfügbar ist
    const pythonCmd = checkPython();
    if (!pythonCmd) {
        dialog.showErrorBox(
            'Python nicht gefunden',
            'FINLY benötigt Python, um zu funktionieren.\n\nBitte installiere Python von https://www.python.org und starte die App erneut.'
        );
        app.quit();
        return false;
    }

    // Prüfe ob src-Ordner existiert
    const srcPath = path.join(projectRoot, 'src');
    if (!fs.existsSync(srcPath)) {
        console.error('❌ src-Ordner nicht gefunden:', srcPath);
        dialog.showErrorBox(
            'Projektdateien fehlen',
            `Der src-Ordner wurde nicht gefunden.\n\nErwartet: ${srcPath}\n\nBitte starte FINLY aus dem Projektordner.`
        );
        app.quit();
        return false;
    }

    const args = [
        '-m', 'uvicorn',
        'src.api.main:app',
        '--host', '127.0.0.1',
        '--port', String(SERVER_PORT)
    ];

    console.log(`🐍 Starte: ${pythonCmd} ${args.join(' ')}`);
    console.log(`📂 CWD: ${projectRoot}`);

    pythonProcess = spawn(pythonCmd, args, {
        cwd: projectRoot,
        env: { ...process.env },
        shell: true
    });

    pythonProcess.stdout.on('data', (data) => {
        console.log(`[Python] ${data.toString().trim()}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.log(`[Python] ${data.toString().trim()}`);
    });

    pythonProcess.on('error', (err) => {
        console.error('❌ Python-Fehler:', err);
        dialog.showErrorBox('Python-Fehler', err.message);
    });

    pythonProcess.on('exit', (code) => {
        console.log(`🛑 Python beendet mit Code: ${code}`);
        pythonProcess = null;
    });

    return true;
}

// Stoppt den Python-Server
function stopPythonServer() {
    if (pythonProcess) {
        console.log('🛑 Beende Python-Server...');

        if (process.platform === 'win32') {
            spawn('taskkill', ['/pid', pythonProcess.pid, '/f', '/t']);
        } else {
            pythonProcess.kill('SIGTERM');
        }

        pythonProcess = null;
    }
}

// Erstellt das Hauptfenster
function createWindow() {
    const projectRoot = getProjectRoot();

    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1000,
        minHeight: 700,
        title: 'FINLY - Persönlicher Ausgabenmanager',
        icon: path.join(projectRoot, 'static', 'img', 'icon.png'),
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        backgroundColor: '#1a1a1a',
        show: false
    });

    // Fenster anzeigen wenn bereit
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
    });

    // Externe Links im System-Browser öffnen
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
        return { action: 'deny' };
    });

    // Server-URL laden
    mainWindow.loadURL(SERVER_URL);

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

// App-Start
app.whenReady().then(async () => {
    console.log('🚀 FINLY startet...');

    // Python-Server starten
    const serverStarted = startPythonServer();
    if (!serverStarted) return;

    try {
        // Warte auf Server
        await waitForServer();

        // Fenster erstellen
        createWindow();
    } catch (error) {
        console.error('❌ Fehler beim Starten:', error);
        dialog.showErrorBox(
            'Server-Fehler',
            'Der Backend-Server konnte nicht gestartet werden.\n\nBitte stelle sicher, dass:\n1. Python installiert ist\n2. Alle Dependencies installiert sind (pip install -r requirements.txt)\n3. Port 8000 nicht belegt ist'
        );
        app.quit();
    }
});

// App beenden wenn alle Fenster geschlossen
app.on('window-all-closed', () => {
    stopPythonServer();
    app.quit();
});

// Cleanup bei App-Beendigung
app.on('before-quit', () => {
    stopPythonServer();
});

// macOS: Fenster neu erstellen wenn auf Dock-Icon geklickt
app.on('activate', () => {
    if (mainWindow === null && pythonProcess) {
        createWindow();
    }
});
