function embedWatermark() {
    const fileInput = document.getElementById('audioFile');
    
    if (!fileInput.files[0]) {
        showResult('❌ Bitte wähle eine Audio-Datei aus!', true, 'embedResult');
        return;
    }

    const formData = new FormData();
    formData.append('audio', fileInput.files[0]);

    showResult('⏳ Watermark wird eingebettet...', false, 'embedResult');

    fetch('/watermark/embed', {
        method: 'POST',
        body: formData
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'watermarked_' + fileInput.files[0].name;
        document.body.appendChild(a);
        a.click();
        a.remove();
        
        showResult('✅ Watermark erfolgreich eingebettet! Download startet...', false, 'embedResult');
    })
    .catch(error => {
        showResult('❌ Fehler: ' + error, true, 'embedResult');
    });
}

function detectWatermark() {
    const fileInput = document.getElementById('detectFile');
    
    if (!fileInput.files[0]) {
        showResult('❌ Bitte wähle eine Audio-Datei aus!', true, 'detectResult');
        return;
    }

    const formData = new FormData();
    formData.append('audio', fileInput.files[0]);

    showResult('⏳ Watermark wird gescannt...', false, 'detectResult');

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

        const confidence = data.confidence.toFixed(2);
        const detected = data.detected;
        
        let resultHTML = `
            <div class="mt-4">
                <h6 class="text-center">📊 Analyse: ${data.filename}</h6>
                
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
            </div>
        `;
        
        document.getElementById('detectResult').innerHTML = resultHTML;
    })
    .catch(error => {
        showResult('❌ Fehler: ' + error, true, 'detectResult');
    });
}