# ============================================================
#  nuke_server.py
#  Se coloca en: C:/Users/TU_USUARIO/.nuke/nuke_server.py
# ============================================================

import socket       # Para crear la conexión de red
import threading    # Para correr el servidor sin bloquear Nuke
import traceback    # Para mostrar errores detallados si algo falla

import nuke         # API de Nuke (solo disponible dentro de Nuke)

# ------------------------------------------------------------
# CONFIGURACIÓN
# Estas dos variables son las únicas que necesitas tocar.
# HOST: '127.0.0.1' significa "esta misma máquina" (localhost).
#       Nunca exponemos el servidor a la red externa por seguridad.
# PORT: Puerto arbitrario. 54321 es poco común, evita conflictos.
# ------------------------------------------------------------
HOST = '127.0.0.1'
PORT = 54321


# ============================================================
#  CLASE PRINCIPAL: NukeServer
#  Encapsula toda la lógica del servidor en un objeto ordenado.
#  Usar una clase (en vez de funciones sueltas) nos permite
#  guardar el estado (si está corriendo, el socket, etc.)
# ============================================================
class NukeServer:

    def __init__(self):
        # Estado interno del servidor
        self.running = False          # ¿Está el servidor activo?
        self.server_socket = None     # El socket principal de escucha
        self.thread = None            # El hilo de fondo

    # --------------------------------------------------------
    #  start()
    #  Arranca el servidor en un hilo separado.
    #  Se llama desde el botón "Iniciar" del panel de Nuke.
    # --------------------------------------------------------
    def start(self):
        if self.running:
            nuke.message("El servidor ya está en marcha.")
            return

        # Creamos el socket del servidor
        # AF_INET = IPv4, SOCK_STREAM = TCP (conexión estable)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # SO_REUSEADDR permite reutilizar el puerto inmediatamente
        # si Nuke se cerró sin cerrar el servidor correctamente.
        # Sin esto, obtendrías error "puerto en uso" al reiniciar.
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Vinculamos el socket a la dirección y puerto
        self.server_socket.bind((HOST, PORT))

        # Ponemos el socket en modo escucha.
        # El '1' es el número máximo de conexiones en cola.
        # Solo esperamos un cliente (PyCharm), así que 1 es suficiente.
        self.server_socket.listen(1)

        self.running = True
        print(f"[NukeServer] Servidor iniciado en {HOST}:{PORT}")

        # Creamos y arrancamos el hilo de fondo.
        # daemon=True significa que el hilo muere automáticamente
        # cuando Nuke se cierra. Sin esto, el hilo podría quedarse
        # huérfano en memoria.
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()

    # --------------------------------------------------------
    #  stop()
    #  Detiene el servidor limpiamente.
    #  Se llama desde el botón "Detener" del panel de Nuke.
    # --------------------------------------------------------
    def stop(self):
        self.running = False
        if self.server_socket:
            # Cerramos el socket para que _listen_loop salga
            # del bloqueo en accept() y termine el hilo.
            self.server_socket.close()
            self.server_socket = None
        print("[NukeServer] Servidor detenido.")

    # --------------------------------------------------------
    #  _listen_loop()
    #  Bucle principal que corre en el hilo de fondo.
    #  El prefijo _ indica que es un método "interno" de la clase.
    #  Espera conexiones y las procesa una a una.
    # --------------------------------------------------------
    def _listen_loop(self):
        while self.running:
            try:
                # accept() bloquea el hilo hasta que llega una conexión.
                # Devuelve un nuevo socket específico para ese cliente
                # y la dirección del cliente.
                client_socket, client_address = self.server_socket.accept()
                print(f"[NukeServer] Conexión recibida de {client_address}")

                # Procesamos la conexión en otro hilo para que el
                # servidor pueda seguir aceptando nuevas conexiones
                # mientras procesa la actual.
                handler = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket,),
                    daemon=True
                )
                handler.start()

            except OSError:
                # OSError se lanza cuando cerramos el socket desde stop().
                # Es la señal para salir del bucle limpiamente.
                break
            except Exception as e:
                print(f"[NukeServer] Error en el bucle de escucha: {e}")

    # --------------------------------------------------------
    #  _handle_client()
    #  Gestiona una conexión individual de PyCharm.
    #  Recibe el código, lo ejecuta en Nuke y devuelve el resultado.
    # --------------------------------------------------------
    def _handle_client(self, client_socket):
        try:
            # Recibimos los datos en chunks de 4096 bytes.
            # Un script puede ser más largo que 4096 bytes,
            # así que acumulamos hasta recibir el marcador de fin.
            data = b""
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                data += chunk
                # Cuando PyCharm termina de enviar, manda "##END##"
                # como señal de fin de mensaje.
                if b"##END##" in data:
                    break

            # Decodificamos los bytes a texto y quitamos el marcador
            code = data.decode('utf-8').replace("##END##", "").strip()

            if not code:
                client_socket.sendall(b"[NukeServer] Codigo vacio recibido.")
                return

            print(f"[NukeServer] Ejecutando codigo:\n{code}\n")

            # PUNTO CRÍTICO: nuke.executeInMainThread()
            # Nuke solo permite modificar su estado (nodos, propiedades)
            # desde el hilo principal. Como estamos en un hilo de fondo,
            # usamos executeInMainThread para enviar el código al hilo
            # principal de Nuke de forma segura.
            result_container = []  # Lista mutable para capturar el resultado

            def run_code():
                try:
                    # exec() ejecuta el código Python arbitrario.
                    # Le pasamos un contexto con el módulo nuke disponible.
                    exec(code, {"nuke": nuke})
                    result_container.append("[OK] Codigo ejecutado correctamente.")
                except Exception:
                    # Capturamos el traceback completo para enviarlo
                    # de vuelta a PyCharm como feedback de error.
                    result_container.append(f"[ERROR]\n{traceback.format_exc()}")

            nuke.executeInMainThread(run_code, (), {})

            # Esperamos brevemente a que el resultado esté listo
            import time
            timeout = 10  # segundos máximo de espera
            elapsed = 0
            while not result_container and elapsed < timeout:
                time.sleep(0.1)
                elapsed += 0.1

            # Enviamos el resultado de vuelta a PyCharm
            result = result_container[0] if result_container else "[ERROR] Timeout esperando resultado."
            client_socket.sendall(result.encode('utf-8'))

        except Exception as e:
            error_msg = f"[NukeServer] Error manejando cliente: {traceback.format_exc()}"
            print(error_msg)
            try:
                client_socket.sendall(error_msg.encode('utf-8'))
            except:
                pass
        finally:
            # Siempre cerramos el socket del cliente al terminar,
            # independientemente de si hubo error o no.
            client_socket.close()


# ============================================================
#  Instancia global del servidor
#  Al importar este módulo, la instancia queda disponible
#  para el panel de Nuke y para menu.py
# ============================================================
nuke_server = NukeServer()
