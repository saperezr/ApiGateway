import requests
from flask import Flask, jsonify, request
import json
import time

app = Flask(__name__)


with open('config.json', 'r') as f:
    config = json.load(f)

primary_service = config['primary_service_url']
backup_service = config['backup_service_url']
retry_count = config['retry_count']


def monitor(url):

    for attempt in range(retry_count):
        print(f"LLamando servicio {url}")
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("Respuesta exitosa")
                return response
            else:
                print(f"Intento {attempt + 1} fallido")
        except Exception as e:
            print(f"Intento {attempt + 1} fallido: {e}")
        
        time.sleep(1)

    return None

# Ruta del API Gateway
@app.route('/gateway', methods=['GET'])
def gateway():
    global current_service

    service_url = primary_service
    response = monitor(service_url)

    if response is None:
        print("Cambiando al servicio de respaldo...")
        service_url = backup_service
        response = monitor(service_url)
        
        if response is None:
            return jsonify({"error": "Todos los servicios fallaron"}), 503
    
    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(port=5001)
