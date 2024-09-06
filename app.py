import csv
import datetime
import requests
from flask import Flask, jsonify
import json
import time

app = Flask(__name__)


with open('config.json', 'r') as f:
    config = json.load(f)

primary_service = config['primary_service_url']
backup_service = config['backup_service_url']
retry_count = config['retry_count']
call_counter = 0
current_service = primary_service


def write_log(service_name, status_code, message):
    log_file = 'gateway_logs.csv'
    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow([datetime.datetime.now(), service_name, status_code, message])

def monitor(url):
    for attempt in range(retry_count):
        print(f"Reintentando llamado al servicio {url}")
        write_log(url, "", 'Reintento Api Call')
        response = requests.get(url)
        if response.status_code == 200:
            write_log(url, response.status_code, 'Respuesta exitosa')
            return response
        
        attempt += 1
        time.sleep(0.2)

    write_log(url, response.status_code, 'Fallo Api Call')
    return None


# Ruta del API Gateway
@app.route('/gateway/v2', methods=['GET'])
def gateway2():
    global current_service

    write_log(current_service, 'N/A', 'Api Call')
    response = requests.get(current_service)
    
    if (response.status_code == 200):
        write_log(current_service, response.status_code, 'Respuesta exitosa')
        return jsonify(response.json()), response.status_code
    else: 
        response = monitor(current_service)

        if response is None:
            print("Cambiando al servicio de respaldo...")
            if current_service == primary_service:
                write_log(f'{primary_service} -> {backup_service}', '', 'Cambio de servicio')
                current_service = backup_service
            else:
                write_log(f'{backup_service} -> {primary_service}', '', 'Cambio de servicio')
                current_service = primary_service
                
            response = requests.get(current_service)

            if (response.status_code == 200):
                return jsonify(response.json()), response.status_code
            
        write_log(current_service, "", 'Todos los servicios fallaron')
        return jsonify({"error": "Todos los servicios fallaron"}), 503

if __name__ == '__main__':
    app.run(port=5000)
