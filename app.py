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
simulate_error_count =  config['simulate_error_count']
call_counter = 0
current_service = primary_service


def monitor(url):
    global call_counter
    print(f"Call counter {call_counter}")

    for attempt in range(retry_count):
        print(f"LLamando servicio {url}")
        try:
            response = requests.get(url)
            if response.status_code == 200:

                call_counter += 1
                if call_counter >= simulate_error_count:
                    print(f"Simulando fallo")
                    print(f"Intento {attempt + 1} fallido")
                else:
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
    global current_service, call_counter

    response = monitor(current_service)

    if response is None:
        print("Cambiando al servicio de respaldo...")
        call_counter = 0
        if current_service == primary_service:
            current_service=backup_service
        else:
            current_service=primary_service
        response = monitor(current_service)


        if response is None:
            return jsonify({"error": "Todos los servicios fallaron"}), 503
    
    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(port=5001)
