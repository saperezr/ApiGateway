import csv
import datetime
import requests
from flask import Flask, jsonify, request
import json
import jwt

app = Flask(__name__)


with open('config.json', 'r') as f:
    config = json.load(f)

users_service = config['users_service_url']
clients_service = config['clients_service_url']
SECRET_KEY = config['SECRET_KEY']

def write_log(service_name, status_code, message):
    log_file = 'gateway_logs.csv'
    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow([datetime.datetime.now(), service_name, status_code, message])



@app.route('/gateway/register', methods=['POST'])
def call_register():
    global users_service

    write_log(users_service , 'N/A', 'POST Registro Nuevo Usuario')
    response = requests.post(users_service+'/register', json=request.json)
    
    if (response.status_code == 200):
        write_log(users_service, response.status_code, 'Registro Exitoso: ' + json.dumps(response.json()))
        return jsonify(response.json()), response.status_code
    else: 
        write_log(users_service, response.status_code, 'Fallo en el registro: '+json.dumps(response.json()))
        return jsonify(response.json()), 503

if __name__ == '__main__':
    app.run(port=5000)

@app.route('/gateway/login', methods=['POST'])
def call_login():
    global users_service

    write_log(users_service, 'N/A', 'POST Inicio de Sesion')
    response = requests.post(users_service+'/login', json=request.json)
    
    if (response.status_code == 200):
        write_log(users_service, response.status_code, 'Inicio de Sesion Exitoso: '+ json.dumps(response.json()))
        return jsonify(response.json()), response.status_code
    else: 
        write_log(users_service, response.status_code, 'Fallo en el inicio de sesion: ' + json.dumps(response.json()))
        return jsonify(response.json()), 503
    

@app.route('/gateway/clients', methods=['GET'])
def call_clients():
    global clients_service

    token = None
    if 'Authorization' in request.headers:
        token = request.headers['Authorization'].split(" ")[1]
    
    if not token:
        return jsonify({"error": "Token no encontrado"}), 401

    try:
       
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_type = decoded_token['sub']['user_type']

        write_log(clients_service, 'N/A', f'GET Clientes - User Type: {user_type}')
        
        if user_type != 1:
            write_log(clients_service, 403, 'No autorizado para consultar clientes')
            return jsonify({"error": "No autorizado para consultar clientes"}), 403
        else:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(clients_service, headers=headers)
            
            if response.status_code == 200:
                write_log(clients_service, response.status_code, 'Consulta de Clientes Exitosa')
                return jsonify(response.json()), response.status_code
            else:
                write_log(clients_service, response.status_code, 'Fallo en la consulta de clientes')
                return jsonify({"error": "Fallo en la consulta de clientes"}), 503

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "El token ha expirado!"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token Invalido!"}), 401