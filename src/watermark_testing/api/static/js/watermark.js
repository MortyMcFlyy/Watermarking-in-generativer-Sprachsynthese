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
            // AudioSeal: Zeige Confidence Score
            const confidence = data.confidence.toFixed(2);
            
            resultHTML += `
                <div class="confidence-badge ${detected ? 'bg-success text-white' : 'bg-danger text-white'}">
                    ${confidence}%
                </div>
                
                <div class="progress" style="height: 25px;">
                    <div class="progress-bar ${detected ? 'progress-bar-detected' : 'progress-bar-not-detected'}" 
                         role="progressbar" 
                         style="width: ${confidence}%;" 
                         aria-valuenow="${confidence}" 
                         aria-valuemin="0" 
                         aria-valuemax="100">
                    </div>
                </div>
                
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