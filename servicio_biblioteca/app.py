import os
from flask import Flask, jsonify

app = Flask(__name__)

# datos de prueba
prestamos = {
    '20211001': {'prestamos_activos': [], 'multas_pendientes': 0},
    '20211002': {'prestamos_activos': [], 'multas_pendientes': 0},
    '20211003': {'prestamos_activos': [], 'multas_pendientes': 0},
    '20211004': {'prestamos_activos': [
        {'libro': 'Redes de Computadoras', 'fecha_limite': '2026-11-10'}], 'multas_pendientes': 12000},
}


@app.get('/')
def inicio():
    return jsonify({'servicio': 'Biblioteca', 'estado': 'activo', 'recurso': '/usuarios/<codigo>/prestamos'})


@app.get('/health')
def health():
    return jsonify({'status': 'ok'}), 200


@app.get('/usuarios/<codigo>/prestamos')
def obtener(codigo):
    item = prestamos.get(codigo)
    if item is None:
        return jsonify({'error': 'Usuario no registrado en biblioteca'}), 404
    return jsonify({'codigo': codigo, **item}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5002')))
