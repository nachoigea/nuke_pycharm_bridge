# ============================================================
#  nuke_client.py
#  Se coloca en cualquier carpeta de tu proyecto en PyCharm.
#  Este archivo NO va dentro de Nuke.
#
#  USO:
#    1. Abre PyCharm y edita tu script de Nuke normalmente.
#    2. Al final de tu script (o en un archivo separado),
#       llama a:  send_to_nuke(code=open(__file__).read())
#    3. Haz Run en PyCharm y el código se ejecutará en Nuke.
# ============================================================

import socket       # Para crear la conexión con el servidor de Nuke

# ------------------------------------------------------------
# CONFIGURACIÓN — debe coincidir EXACTAMENTE con nuke_server.py
# ------------------------------------------------------------
HOST = '127.0.0.1'
PORT = 54321


# ============================================================
#  send_to_nuke()
#  Función principal del cliente.
#
#  Parámetros:
#    code (str): Código Python a ejecutar en Nuke.
#                Si no se pasa nada, envía el archivo actual.
#
#  Retorna:
#    str: Respuesta de Nuke (OK o mensaje de error).
# ============================================================
def send_to_nuke(code: str) -> str:

    # Añadimos el marcador de fin de mensaje.
    # El servidor necesita saber cuándo terminó de recibir datos.
    # TCP no garantiza que los datos lleguen en un solo paquete,
    # así que necesitamos un delimitador explícito.
    message = code + "##END##"

    try:
        # Creamos un socket cliente (mismo protocolo que el servidor)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            # Intentamos conectar al servidor en Nuke.
            # Si Nuke no está corriendo o el servidor no está iniciado,
            # esto lanzará ConnectionRefusedError con un mensaje claro.
            s.connect((HOST, PORT))
            print(f"[PyCharm → Nuke] Conectado. Enviando código...")

            # Enviamos el código codificado en bytes (UTF-8)
            s.sendall(message.encode('utf-8'))

            # Esperamos la respuesta de Nuke
            # shutdown(SHUT_WR) le dice al servidor que terminamos de enviar.
            # Esto hace que el recv() del servidor devuelva b"" y sepa
            # que el cliente terminó de hablar.
            s.shutdown(socket.SHUT_WR)

            # Recibimos la respuesta completa de Nuke
            response_data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response_data += chunk

            response = response_data.decode('utf-8')
            print(f"[Nuke → PyCharm] Respuesta: {response}")
            return response

    except ConnectionRefusedError:
        msg = (
            "[ERROR] No se pudo conectar con Nuke.\n"
            "Asegúrate de que:\n"
            "  1. Nuke 14 está abierto.\n"
            "  2. El servidor está iniciado (botón 'Iniciar' en el panel).\n"
            f"  3. El puerto {PORT} no está bloqueado."
        )
        print(msg)
        return msg

    except Exception as e:
        msg = f"[ERROR] Error inesperado al enviar a Nuke: {e}"
        print(msg)
        return msg


# ============================================================
#  BLOQUE PRINCIPAL DE USO
#
#  Cuando ejecutas este archivo directamente desde PyCharm,
#  el bloque if __name__ == '__main__' se activa.
#
#  La forma típica de uso es importar send_to_nuke en tu
#  script de Nuke y llamarla al final:
#
#  Ejemplo en tu script_de_nuke.py:
#
#      import nuke
#
#      # Tu código de Nuke aquí
#      node = nuke.createNode('Blur')
#      node['size'].setValue(10)
#
#      # Al final, envíalo a Nuke con una sola línea:
#      if __name__ == '__main__':
#          from nuke_client import send_to_nuke
#          send_to_nuke(code=open(__file__).read())
#
# ============================================================
if __name__ == '__main__':
    # Código de prueba: crea un nodo Blur en Nuke
    test_code = """
import nuke
node = nuke.createNode('Blur')
node['size'].setValue(25)
print('Nodo Blur creado con size=25')
"""
    send_to_nuke(code=test_code)
