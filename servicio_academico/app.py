import os
from flask import Flask, jsonify

app = Flask(__name__)

# datos de prueba
estudiantes = [
    {'codigo': '20211001', 'nombre': 'Laura Pérez', 'programa': 'Ingeniería de Sistemas',
     'creditos_aprobados': 160, 'creditos_requeridos': 160},
    {'codigo': '20211002', 'nombre': 'Carlos Martínez', 'programa': 'Ingeniería de Sistemas',
     'creditos_aprobados': 160, 'creditos_requeridos': 160},
    {'codigo': '20211003', 'nombre': 'Ana Gómez', 'programa': 'Administración de Empresas',
     'creditos_aprobados': 148, 'creditos_requeridos': 156},
    {'codigo': '20211004', 'nombre': 'Juan Rodríguez', 'programa': 'Psicología',
     'creditos_aprobados': 150, 'creditos_requeridos': 150},
]


@app.get('/')
def inicio():
    return jsonify({'servicio': 'Registro Académico', 'estado': 'activo', 'recurso': '/estudiantes'})


@app.get('/health')
def health():
    return jsonify({'status': 'ok'}), 200


@app.get('/estudiantes')
def listar():
    return jsonify(estudiantes), 200


@app.get('/estudiantes/<codigo>')
def obtener(codigo):
    item = next((x for x in estudiantes if x['codigo'] == codigo), None)
    if item is None:
        return jsonify({'error': 'Estudiante no encontrado'}), 404
    return jsonify(item), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5001')))
