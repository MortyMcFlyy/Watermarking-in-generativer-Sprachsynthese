function embedWatermark() {
    const fileInput = document.getElementById('audioFile');
    const methodSelect = document.getElementById('embedMethod');
    const method = methodSelect.value;
    
    if (!fileInput.files[0]) {
        showResult('❌ Bitte wähle eine Audio-Datei aus!', true, 'embedResult');
        return;
    }

    const formData = new FormData();
    formData.append('audio', fileInput.files[0]);
    formData.append('method', method);

    const methodName = method === 'audioseal' ? 'AudioSeal' : 'PerTh';
    showResult(`⏳ Watermark wird mit ${methodName} eingebettet...`, false, 'embedResult');

    fetch('/watermark/embed', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.error || 'Unbekannter Fehler'); });
        }
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `watermarked_${method}_` + fileInput.files[0].name;
        document.body.appendChild(a);
        a.click();
        a.remove();
        
        showResult(`✅ Watermark erfolgreich mit ${methodName} eingebettet! Download startet...`, false, 'embedResult');
    })
    .catch(error => {
        showResult('❌ Fehler: ' + error.message, true, 'embedResult');
    });
}

function detectWatermark() {
    const fileInput = document.getElementById('detectFile');
    const methodSelect = document.getElementById('detectMethod');
    const method = methodSelect.value;
    
    if (!fileInput.files[0]) {
        showResult('❌ Bitte wähle eine Audio-Datei aus!', true, 'detectResult');
        return;
    }

    const formData = new FormData();
    formData.append('audio', fileInput.files[0]);
    formData.append('method', method);

    const methodName = method === 'audioseal' ? 'AudioSeal' : 'PerTh';
    showResult(`⏳ Watermark wird mit ${methodName} gescannt...`, false, 'detectResult');

    fetch('/watermark/detect', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showResult(`❌ Fehler: ${data.error}`, true, 'detectResult');
            return;
        }

        const detected = data.detected;
        const methodBadgeClass = method === 'audioseal' ? 'badge-audioseal' : 'badge-perth';
        
        let resultHTML = `
            <div class="mt-4">
                <h6 class="text-center">
                    📊 Analyse: ${data.filename}
                    <span class="method-badge ${methodBadgeClass}">${methodName}</span>
                </h6>
        `;

        // Unterschiedliche Anzeige je nach Methode
        if (method === 'audioseal') {
            // AudioSeal: Nur die Alert-Box mit Konfidenz
            const confidence = data.confidence.toFixed(2);
            
            resultHTML += `
                <div class="alert ${detected ? 'alert-success' : 'alert-warning'} mt-3">
                    <strong>${detected ? '✅ Watermark erkannt!' : '⚠️ Kein Watermark erkannt'}</strong><br>
                    Konfidenz: ${confidence}%
                </div>
            `;
        } else {
            // PerTh: Zeige nur Ja/Nein
            resultHTML += `
                <div class="alert ${detected ? 'alert-success' : 'alert-warning'} mt-3 text-center" style="font-size: 1.2rem;">
                    <strong>${detected ? '✅ Watermark erkannt!' : '⚠️ Kein Watermark erkannt'}</strong>
                </div>
            `;
            
            // Zeige extrahiertes Watermark falls vorhanden
            if (detected && data.watermark !== null && data.watermark !== undefined) {
                resultHTML += `
                    <div class="alert alert-info mt-2">
                        <strong>🔐 Extrahiertes Watermark:</strong><br>
                        <code style="white-space: pre-wrap; word-break: break-all;">${JSON.stringify(data.watermark, null, 2)}</code>
                    </div>
                `;
            }
        }

        resultHTML += `</div>`;
        
        document.getElementById('detectResult').innerHTML = resultHTML;
    })
    .catch(error => {
        showResult('❌ Fehler: ' + error, true, 'detectResult');
    });
}

// ==========================================
// FILES MANAGEMENT
// ==========================================

/**
 * Lädt alle Dateien vom Server und zeigt sie an
 */
function loadFiles() {
    const loadingDiv = document.getElementById('filesLoading');
    const containerDiv = document.getElementById('filesContainer');
    const errorDiv = document.getElementById('filesError');
    
    // Loading anzeigen
    loadingDiv.style.display = 'block';
    containerDiv.style.display = 'none';
    errorDiv.style.display = 'none';
    
    fetch('/files', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        
        displayFiles(data.files, data.count);
        
        // Container anzeigen
        loadingDiv.style.display = 'none';
        containerDiv.style.display = 'block';
    })
    .catch(error => {
        loadingDiv.style.display = 'none';
        errorDiv.textContent = '❌ Fehler beim Laden der Dateien: ' + error.message;
        errorDiv.style.display = 'block';
    });
}

/**
 * Zeigt die Dateiliste an
 */
function displayFiles(files, count) {
    const filesList = document.getElementById('filesList');
    const fileCount = document.getElementById('fileCount');
    const noFilesMessage = document.getElementById('noFilesMessage');
    
    // Counter aktualisieren
    fileCount.textContent = `${count} ${count === 1 ? 'File' : 'Files'}`;
    
    // Wenn keine Dateien vorhanden
    if (files.length === 0) {
        filesList.innerHTML = '';
        noFilesMessage.style.display = 'block';
        return;
    }
    
    noFilesMessage.style.display = 'none';
    
    // Dateien anzeigen - WICHTIG: data-* Attribute statt inline onclick mit String-Parametern!
    filesList.innerHTML = files.map(file => {
        const date = new Date(file.created_at);
        const formattedDate = date.toLocaleDateString('de-DE', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        const duration = file.duration ? `${file.duration.toFixed(1)}s` : 'N/A';
        const watermarkBadge = file.has_watermark 
            ? `<span class="badge bg-success">${escapeHtml(file.watermark_type || 'Watermarked')}</span>`
            : '<span class="badge bg-secondary">Original</span>';
        
        const watermarkIndicator = file.has_watermark
            ? '<span class="watermark-indicator has-watermark" title="Has watermark"></span>'
            : '<span class="watermark-indicator no-watermark" title="No watermark"></span>';
        
        return `
            <div class="list-group-item file-item">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <div class="d-flex align-items-center mb-2">
                            ${watermarkIndicator}
                            <strong class="me-2">${escapeHtml(file.filename)}</strong>
                            ${watermarkBadge}
                        </div>
                        <div class="file-metadata">
                            <span>📅 ${formattedDate}</span>
                            <span class="ms-3">⏱️ ${duration}</span>
                        </div>
                    </div>
                    <div class="file-actions">
                        <button class="btn btn-sm btn-outline-primary" data-file-id="${file.id}" data-action="download">
                            ⬇️ Download
                        </button>
                        <button class="btn btn-sm btn-outline-danger" data-file-id="${file.id}" data-filename="${escapeHtml(file.filename)}" data-action="delete">
                            🗑️ Delete
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    // Event Delegation: Alle Button-Klicks in der Liste abfangen
    filesList.addEventListener('click', handleFileAction);
}

/**
 * Event Handler für Download/Delete Aktionen
 */
function handleFileAction(event) {
    const button = event.target.closest('button[data-action]');
    if (!button) return;
    
    const action = button.dataset.action;
    const fileId = parseInt(button.dataset.fileId);
    
    if (action === 'download') {
        downloadFile(fileId);
    } else if (action === 'delete') {
        const filename = button.dataset.filename;
        deleteFile(fileId, filename);
    }
}

/**
 * Lädt eine Datei herunter
 */
function downloadFile(fileId) {
    window.location.href = `/download/${fileId}`;
}

/**
 * Löscht eine Datei
 */
function deleteFile(fileId, filename) {
    if (!confirm(`Möchtest du die Datei "${filename}" wirklich löschen?`)) {
        return;
    }
    
    fetch(`/files/${fileId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Erfolgsmeldung anzeigen
        showAlert('success', `✅ Datei "${filename}" wurde erfolgreich gelöscht!`);
        
        // Liste neu laden
        loadFiles();
    })
    .catch(error => {
        showAlert('danger', '❌ Fehler beim Löschen: ' + error.message);
    });
}

/**
 * Zeigt eine Alert-Nachricht an
 */
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.getElementById('filesContainer');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-remove nach 5 Sekunden
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

/**
 * Escaped HTML für XSS-Schutz
 */
function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

// Event Listener: Dateien laden wenn Files-Tab geöffnet wird
document.getElementById('files-tab').addEventListener('shown.bs.tab', function () {
    loadFiles();
});

function updateManipulationParameters() {
    const type = document.getElementById('manipulationType').value;
    const paramsDiv = document.getElementById('manipulationParameters');
    
    let parametersHTML = '';
    
    switch(type) {
        case 'noise':
            parametersHTML = `
                <div class="param-group">
                    <label for="snrValue" class="form-label">
                        Signal-to-Noise Ratio (SNR): <span class="param-value-display" id="snrDisplay">20 dB</span>
                    </label>
                    <input type="range" class="form-range" id="snrValue" min="0" max="40" value="20" step="5" 
                           oninput="document.getElementById('snrDisplay').textContent = this.value + ' dB'">
                    <small class="text-muted">Higher = less noise</small>
                </div>
            `;
            break;
            
        case 'compression':
            parametersHTML = `
                <div class="param-group">
                    <label for="bitrateValue" class="form-label">
                        MP3 Bitrate: <span class="param-value-display" id="bitrateDisplay">128 kbps</span>
                    </label>
                    <select id="bitrateValue" class="form-select" onchange="document.getElementById('bitrateDisplay').textContent = this.value + ' kbps'">
                        <option value="64">64 kbps</option>
                        <option value="96">96 kbps</option>
                        <option value="128" selected>128 kbps</option>
                        <option value="192">192 kbps</option>
                        <option value="256">256 kbps</option>
                        <option value="320">320 kbps</option>
                    </select>
                </div>
            `;
            break;
            
        case 'gain':
            parametersHTML = `
                <div class="param-group">
                    <label for="gainValue" class="form-label">
                        Gain: <span class="param-value-display" id="gainDisplay">0 dB</span>
                    </label>
                    <input type="range" class="form-range" id="gainValue" min="-20" max="20" value="0" step="1" 
                           oninput="document.getElementById('gainDisplay').textContent = this.value + ' dB'">
                    <small class="text-muted">Negative = quieter, Positive = louder</small>
                </div>
            `;
            break;
            
        case 'resample':
            parametersHTML = `
                <div class="param-group">
                    <label for="sampleRate" class="form-label">Target Sample Rate</label>
                    <select id="sampleRate" class="form-select">
                        <option value="8000">8 kHz (Phone quality)</option>
                        <option value="16000">16 kHz (Wideband)</option>
                        <option value="22050">22.05 kHz</option>
                        <option value="44100" selected>44.1 kHz (CD quality)</option>
                        <option value="48000">48 kHz (Professional)</option>
                    </select>
                </div>
            `;
            break;
            
        case 'lowpass':
            parametersHTML = `
                <div class="param-group">
                    <label for="lowpassCutoff" class="form-label">
                        Cutoff Frequency: <span class="param-value-display" id="lowpassDisplay">3000 Hz</span>
                    </label>
                    <input type="range" class="form-range" id="lowpassCutoff" min="500" max="8000" value="3000" step="100" 
                           oninput="document.getElementById('lowpassDisplay').textContent = this.value + ' Hz'">
                    <small class="text-muted">Removes frequencies above cutoff</small>
                </div>
            `;
            break;
            
        case 'highpass':
            parametersHTML = `
                <div class="param-group">
                    <label for="highpassCutoff" class="form-label">
                        Cutoff Frequency: <span class="param-value-display" id="highpassDisplay">300 Hz</span>
                    </label>
                    <input type="range" class="form-range" id="highpassCutoff" min="50" max="1000" value="300" step="10" 
                           oninput="document.getElementById('highpassDisplay').textContent = this.value + ' Hz'">
                    <small class="text-muted">Removes frequencies below cutoff</small>
                </div>
            `;
            break;
            
        case 'timestretch':
            parametersHTML = `
                <div class="param-group">
                    <label for="timeStretchRate" class="form-label">
                        Stretch Rate: <span class="param-value-display" id="timestretchDisplay">1.0x</span>
                    </label>
                    <input type="range" class="form-range" id="timeStretchRate" min="0.5" max="2.0" value="1.0" step="0.1" 
                           oninput="document.getElementById('timestretchDisplay').textContent = this.value + 'x'">
                    <small class="text-muted">0.5x = half speed, 2.0x = double speed</small>
                </div>
            `;
            break;
            
        case 'pitchshift':
            parametersHTML = `
                <div class="param-group">
                    <label for="pitchSteps" class="form-label">
                        Pitch Shift: <span class="param-value-display" id="pitchDisplay">0 semitones</span>
                    </label>
                    <input type="range" class="form-range" id="pitchSteps" min="-2" max="2" value="0" step="0.125" 
                           oninput="updatePitchDisplay(this.value)">
                    <small class="text-muted">0.125 = 1/8 semitone (12.5 cents) | 0.25 = quarter tone | 0.5 = half semitone</small>
                </div>
            `;
            break;
    }
    
    paramsDiv.innerHTML = parametersHTML;
}

function applyManipulation() {
    const fileInput = document.getElementById('manipulationFile');
    const type = document.getElementById('manipulationType').value;
    
    if (!fileInput.files[0]) {
        showResult('❌ Bitte wähle eine Audio-Datei aus!', true, 'manipulationResult');
        return;
    }

    // Parameter sammeln basierend auf Typ
    const params = getManipulationParameters(type);
    
    const formData = new FormData();
    formData.append('audio', fileInput.files[0]);
    formData.append('manipulation_type', type);
    formData.append('parameters', JSON.stringify(params));

    showResult(`⏳ Manipulation wird angewendet...`, false, 'manipulationResult');

    fetch('/manipulation/apply', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.error || 'Unbekannter Fehler'); });
        }
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `manipulated_${type}_` + fileInput.files[0].name;
        document.body.appendChild(a);
        a.click();
        a.remove();
        
        showResult(`✅ Manipulation erfolgreich angewendet! Download startet...`, false, 'manipulationResult');
    })
    .catch(error => {
        showResult('❌ Fehler: ' + error.message, true, 'manipulationResult');
    });
}

function getManipulationParameters(type) {
    const params = {};
    
    switch(type) {
        case 'noise':
            params.snr = document.getElementById('snrValue')?.value || 20;
            break;
        case 'compression':
            params.bitrate = document.getElementById('bitrateValue')?.value || 128;
            break;
        case 'gain':
            params.gain_db = document.getElementById('gainValue')?.value || 0;
            break;
        case 'resample':
            params.sample_rate = document.getElementById('sampleRate')?.value || 44100;
            break;
        case 'lowpass':
            params.cutoff = document.getElementById('lowpassCutoff')?.value || 3000;
            break;
        case 'highpass':
            params.cutoff = document.getElementById('highpassCutoff')?.value || 300;
            break;
        case 'timestretch':
            params.rate = document.getElementById('timeStretchRate')?.value || 1.0;
            break;
        case 'pitchshift':
            params.steps = parseFloat(document.getElementById('pitchSteps')?.value || 0);
            break;
    }
    
    return params;
}

// Initialize parameters when page loads
document.addEventListener('DOMContentLoaded', function() {
    updateManipulationParameters();
});

function updatePitchDisplay(value) {
    const numValue = parseFloat(value);
    const displayEl = document.getElementById('pitchDisplay');
    
    // Formatierung für schönere Anzeige
    let displayText = '';
    
    if (numValue === 0) {
        displayText = '0 semitones';
    } else if (numValue % 1 === 0) {
        // Ganze Halbtöne
        displayText = `${numValue > 0 ? '+' : ''}${numValue} semitone${Math.abs(numValue) !== 1 ? 's' : ''}`;
    } else if (numValue % 0.5 === 0) {
        // Vierteltöne (0.5)
        displayText = `${numValue > 0 ? '+' : ''}${numValue} semitones (quarter tone)`;
    } else if (numValue % 0.25 === 0) {
        // Achteltöne (0.25, 0.75)
        displayText = `${numValue > 0 ? '+' : ''}${numValue} semitones (eighth tone)`;
    } else {
        // Mikrotöne (0.125, 0.375, etc.)
        const cents = Math.round(numValue * 100); // 1 semitone = 100 cents
        displayText = `${numValue > 0 ? '+' : ''}${numValue} semitones (${cents > 0 ? '+' : ''}${cents} cents)`;
    }
    
    displayEl.textContent = displayText;
}