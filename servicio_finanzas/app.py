import os
from flask import Flask, jsonify

app = Flask(__name__)

# Datos ficticios del Sistema Financiero (cartera estudiantil)
cuentas = {
    '20211001': {'saldo_pendiente': 0, 'conceptos': []},
    '20211002': {'saldo_pendiente': 850000, 'conceptos': ['Matrícula 2026-2 (cuota 3)']},
    '20211003': {'saldo_pendiente': 0, 'conceptos': []},
    '20211004': {'saldo_pendiente': 0, 'conceptos': []},
}


@app.get('/')
def inicio():
    return jsonify({'servicio': 'Finanzas', 'estado': 'activo', 'recurso': '/estado-cuenta/<codigo>'})


@app.get('/health')
def health():
    return jsonify({'status': 'ok'}), 200


@app.get('/estado-cuenta/<codigo>')
def obtener(codigo):
    item = cuentas.get(codigo)
    if item is None:
        return jsonify({'error': 'Estudiante sin cuenta financiera'}), 404
    return jsonify({'codigo': codigo, **item}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5003')))
