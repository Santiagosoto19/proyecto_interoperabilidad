"""Levanta los 4 servicios en local, ejecuta las pruebas y los apaga.

Uso:  python pruebas.py
Requiere: pip install -r orquestador/requirements.txt
"""
import os
import subprocess
import sys
import time

import requests

RAIZ = os.path.dirname(os.path.abspath(__file__))
ORQ = 'http://127.0.0.1:5000'
SERVICIOS = {
    'academico': ('servicio_academico', 5001),
    'biblioteca': ('servicio_biblioteca', 5002),
    'finanzas': ('servicio_finanzas', 5003),
    'orquestador': ('orquestador', 5000),
}


def levantar(nombre):
    carpeta, puerto = SERVICIOS[nombre]
    env = {**os.environ, 'PORT': str(puerto),
           'ACADEMICO_URL': 'http://127.0.0.1:5001',
           'BIBLIOTECA_URL': 'http://127.0.0.1:5002',
           'FINANZAS_URL': 'http://127.0.0.1:5003',
           'HTTP_TIMEOUT': '3'}
    p = subprocess.Popen([sys.executable, 'app.py'], cwd=os.path.join(RAIZ, carpeta), env=env,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        try:
            requests.get(f'http://127.0.0.1:{puerto}/', timeout=0.5)
            return p
        except requests.exceptions.RequestException:
            time.sleep(0.1)
    raise RuntimeError(f'No arrancó {nombre}')


def caso(titulo, ruta, codigo_esperado, campo=None, valor=None):
    r = requests.get(f'{ORQ}{ruta}', timeout=10)
    cuerpo = r.json()
    ok = r.status_code == codigo_esperado and (campo is None or cuerpo.get(campo) == valor)
    print(f'[{"OK " if ok else "FALLA"}] {titulo}')
    print(f'       GET {ruta} -> HTTP {r.status_code}  {cuerpo.get("paz_y_salvo", "")} '
          f'{cuerpo.get("motivos") or cuerpo.get("mensaje", "")}'
          f'{"  (servicio: " + cuerpo["servicio"] + ")" if "servicio" in cuerpo else ""}')
    return ok


def main():
    procesos = {n: levantar(n) for n in SERVICIOS}
    resultados = []
    try:
        resultados += [
            caso('1. Exitosa: estudiante al día', '/paz-y-salvo/20211001', 200, 'paz_y_salvo', 'APROBADO'),
            caso('2. Rechazo: deuda en Finanzas', '/paz-y-salvo/20211002', 200, 'paz_y_salvo', 'RECHAZADO'),
            caso('3. Rechazo: créditos incompletos', '/paz-y-salvo/20211003', 200, 'paz_y_salvo', 'RECHAZADO'),
            caso('4. Rechazo: préstamo y multa en Biblioteca', '/paz-y-salvo/20211004', 200, 'paz_y_salvo', 'RECHAZADO'),
            caso('5. Inválido: código mal formado', '/paz-y-salvo/abc', 400),
            caso('6. Inválido: estudiante inexistente', '/paz-y-salvo/20999999', 404, 'servicio', 'academico'),
        ]
        procesos.pop('biblioteca').terminate()
        time.sleep(0.5)
        resultados.append(caso('7. Falla: servicio Biblioteca caído', '/paz-y-salvo/20211001', 502, 'servicio', 'biblioteca'))
    finally:
        for p in procesos.values():
            p.terminate()
    print(f'\n{sum(resultados)}/{len(resultados)} pruebas correctas')
    sys.exit(0 if all(resultados) else 1)


if __name__ == '__main__':
    main()
