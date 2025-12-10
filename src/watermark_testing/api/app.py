from flask import Flask, jsonify

# Flask App erstellen
app = Flask(__name__)

# Einfacher Test-Endpoint
@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Hallo! Die API läuft.'}), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

# App starten
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)