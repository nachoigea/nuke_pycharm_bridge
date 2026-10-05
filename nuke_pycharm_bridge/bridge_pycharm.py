# ============================================================
# bridge_pycharm.py
#  Este archivo es el "lanzador". Su único trabajo es:
#    1. Saber qué archivo de Nuke quieres ejecutar
#    2. Leerlo y enviarlo al servidor de Nuke
#
#  Para cambiar qué script se ejecuta en Nuke, solo cambia
#  la variable SCRIPT_A_ENVIAR.
# ============================================================

import sys
import os

sys.path.insert(0, r'/')

from nuke_client import send_to_nuke

# ------------------------------------------------------------
# SCRIPT A ENVIAR
# Cambia esta ruta para apuntar al archivo que quieras
# ejecutar en Nuke. Es la única línea que necesitas tocar.
# ------------------------------------------------------------
SCRIPT_A_ENVIAR = r'C:\Users\nacho\.nuke\Nuke-PyCharm_Bridge\send_script.py'

# ------------------------------------------------------------
# ENVÍO
# Lee el archivo, añade la llamada a main() y lo envía.
# Este bloque no necesita modificarse nunca.
# ------------------------------------------------------------
if __name__ == '__main__':

    if not os.path.exists(SCRIPT_A_ENVIAR):
        print(f"[ERROR] No se encontró el archivo: {SCRIPT_A_ENVIAR}")
        sys.exit(1)

    print("=" * 50)
    print(f"Enviando a Nuke: {os.path.basename(SCRIPT_A_ENVIAR)}")
    print("=" * 50)

    with open(SCRIPT_A_ENVIAR, 'r', encoding='utf-8') as f:
        code = f.read()

    code += "\nmain()"

    response = send_to_nuke(code=code)

    print("=" * 50)
    print(f"Resultado: {response}")
    print("=" * 50)