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