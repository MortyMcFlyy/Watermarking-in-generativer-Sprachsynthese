function embedWatermark() {
    const fileInput = document.getElementById('audioFile');
    const resultDiv = document.getElementById('result');
    
    if (!fileInput.files[0]) {
        resultDiv.innerHTML = 'Bitte wähle eine Audio-Datei aus!';
        resultDiv.className = 'error';
        resultDiv.style.display = 'block';
        return;
    }

    const formData = new FormData();
    formData.append('audio', fileInput.files[0]);

    resultDiv.innerHTML = '⏳ Watermark wird eingebettet...';
    resultDiv.className = '';
    resultDiv.style.display = 'block';

    fetch('/watermark/embed', {
        method: 'POST',
        body: formData
    })
    .then(response => response.blob())
    .then(blob => {
        // Erstelle Download-Link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'watermarked_' + fileInput.files[0].name;
        document.body.appendChild(a);
        a.click();
        a.remove();
        
        resultDiv.innerHTML = '✅ Watermark erfolgreich eingebettet! Download startet...';
    })
    .catch(error => {
        resultDiv.innerHTML = '❌ Fehler: ' + error;
        resultDiv.className = 'error';
    });
}