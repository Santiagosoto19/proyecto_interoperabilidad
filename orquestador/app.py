import os
import re
import requests
from flask import Flask, jsonify

app = Flask(__name__)
ACADEMICO_URL = os.getenv('ACADEMICO_URL', '').rstrip('/')
BIBLIOTECA_URL = os.getenv('BIBLIOTECA_URL', '').rstrip('/')
FINANZAS_URL = os.getenv('FINANZAS_URL', '').rstrip('/')
TIMEOUT = float(os.getenv('HTTP_TIMEOUT', '20'))


def consultar(base_url, ruta):
    """Llama a un microservicio y traduce cualquier falla a (None, mensaje, código HTTP)."""
    if not base_url.startswith(('https://', 'http://')):
        return None, 'URL del microservicio no configurada', 503
    try:
        r = requests.get(f'{base_url}{ruta}', timeout=TIMEOUT, headers={'Accept': 'application/json'})
    except requests.exceptions.Timeout:
        return None, 'Tiempo de espera agotado', 504
    except requests.exceptions.RequestException:
        return None, 'No se pudo conectar al microservicio', 502
    if r.status_code == 404:
        return None, 'Registro no encontrado', 404
    if not r.ok:
        return None, f'El microservicio devolvió HTTP {r.status_code}', 502
    try:
        return r.json(), None, 200
    except ValueError:
        return None, 'El microservicio no devolvió JSON válido', 502


def pesos(valor):
    return f'${valor:,}'.replace(',', '.')


def error(servicio, mensaje, codigo):
    return jsonify({
        'estado': 'ERROR',
        'servicio': servicio,
        'mensaje': mensaje,
        'paz_y_salvo': 'NO_EMITIDO'
    }), codigo


@app.get('/')
def inicio():
    return jsonify({
        'servicio': 'Orquestador de Paz y Salvo para Grado',
        'ruta': '/paz-y-salvo/<codigo>',
        'orden': ['academico', 'biblioteca', 'finanzas']
    })


@app.get('/paz-y-salvo/<codigo>')
def paz_y_salvo(codigo):
    if not re.fullmatch(r'\d{8}', codigo):
        return jsonify({'estado': 'ERROR', 'mensaje': 'El código estudiantil debe tener 8 dígitos'}), 400

    # Paso 1: Registro Académico
    estudiante, msg, cod = consultar(ACADEMICO_URL, f'/estudiantes/{codigo}')
    if msg:
        return error('academico', msg, cod)

    # Paso 2: Biblioteca
    biblioteca, msg, cod = consultar(BIBLIOTECA_URL, f'/usuarios/{codigo}/prestamos')
    if msg:
        return error('biblioteca', msg, cod)

    # Paso 3: Finanzas
    finanzas, msg, cod = consultar(FINANZAS_URL, f'/estado-cuenta/{codigo}')
    if msg:
        return error('finanzas', msg, cod)

    # Consolidación: el orquestador aplica la regla del proceso con lo que respondió cada sistema
    motivos = []
    faltan = estudiante['creditos_requeridos'] - estudiante['creditos_aprobados']
    if faltan > 0:
        motivos.append(f'Académico: faltan {faltan} créditos por aprobar')
    if biblioteca['prestamos_activos']:
        motivos.append(f'Biblioteca: {len(biblioteca["prestamos_activos"])} préstamo(s) sin devolver')
    if biblioteca['multas_pendientes'] > 0:
        motivos.append(f'Biblioteca: multa pendiente de {pesos(biblioteca["multas_pendientes"])}')
    if finanzas['saldo_pendiente'] > 0:
        motivos.append(f'Finanzas: saldo pendiente de {pesos(finanzas["saldo_pendiente"])}')

    return jsonify({
        'estado': 'CONSULTA_COMPLETADA',
        'paz_y_salvo': 'APROBADO' if not motivos else 'RECHAZADO',
        'estudiante': {'codigo': codigo, 'nombre': estudiante['nombre'], 'programa': estudiante['programa']},
        'motivos': motivos,
        'detalle': {'academico': estudiante, 'biblioteca': biblioteca, 'finanzas': finanzas}
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')))
