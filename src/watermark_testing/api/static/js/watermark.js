function embedWatermark() {
    const fileInput = document.getElementById('audioFile');
    
    if (!fileInput.files[0]) {
        showResult('❌ Bitte wähle eine Audio-Datei aus!', true);
        return;
    }

    const formData = new FormData();
    formData.append('audio', fileInput.files[0]);

    showResult('⏳ Watermark wird eingebettet...');

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
        
        showResult('✅ Watermark erfolgreich eingebettet! Download startet...');
    })
    .catch(error => {
        showResult('❌ Fehler: ' + error, true);
    });
}