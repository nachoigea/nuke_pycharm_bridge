# ============================================================
#  nuke_server_panel.py
#  Se coloca en: C:/Users/TU_USUARIO/.nuke/nuke_server_panel.py
#
#  Define el panel flotante que aparece en Nuke con botones
#  para controlar el servidor sin tocar código.
# ============================================================

import nuke
import nukescripts   # Módulo de Nuke para crear paneles personalizados

# Importamos la instancia del servidor que creamos en nuke_server.py
from nuke_server import nuke_server, HOST, PORT


# ============================================================
#  CLASE: NukeServerPanel
#
#  Hereda de nukescripts.PythonPanel, que es la clase base
#  para crear paneles con widgets en Nuke.
#  Elegimos PythonPanel porque:
#    - Es parte de la API oficial de Nuke (estable en v14)
#    - Permite añadir knobs (controles) de forma declarativa
#    - Se puede anclar o usar como panel flotante
# ============================================================
class NukeServerPanel(nukescripts.PythonPanel):

    def __init__(self):
        # Inicializamos el panel con un título y un ID único.
        # El ID debe ser único en todo el entorno de Nuke
        # para evitar conflictos con otros paneles.
        super().__init__('PyCharm Bridge', 'com.studio.pycharm_bridge')

        # ----------------------------------------------------
        # KNOBS (controles del panel)
        # En Nuke, los "knobs" son los elementos de UI:
        # botones, textos, sliders, etc.
        # ----------------------------------------------------

        # Texto de estado: muestra si el servidor está activo o no
        # EvalString_Knob permite texto dinámico que se actualiza
        self.status_knob = nuke.EvalString_Knob('status', 'Estado')
        self.status_knob.setValue('⬛ Servidor detenido')
        self.addKnob(self.status_knob)

        # Texto informativo del puerto
        self.port_knob = nuke.EvalString_Knob('port_info', 'Puerto')
        self.port_knob.setValue(f'{HOST}:{PORT}')
        self.addKnob(self.port_knob)

        # Separador visual para organizar el panel
        self.addKnob(nuke.Text_Knob('', ''))

        # Botón para INICIAR el servidor
        # PyScript_Knob ejecuta código Python cuando se pulsa
        self.start_knob = nuke.PyScript_Knob(
            'start_server',   # nombre interno
            'Iniciar Servidor',  # texto visible
            ''                # script (lo manejamos en knobChanged)
        )
        self.addKnob(self.start_knob)

        # Botón para DETENER el servidor
        self.stop_knob = nuke.PyScript_Knob(
            'stop_server',
            'Detener Servidor',
            ''
        )
        self.addKnob(self.stop_knob)

        # Separador visual
        self.addKnob(nuke.Text_Knob('', ''))

        # Área de log: muestra los últimos eventos
        # Multiline_Eval_String_Knob es un área de texto de múltiples líneas
        self.log_knob = nuke.Multiline_Eval_String_Knob('log', 'Log')
        self.log_knob.setValue('Esperando acciones...')
        self.addKnob(self.log_knob)

        # Botón para limpiar el log
        self.clear_knob = nuke.PyScript_Knob('clear_log', 'Limpiar Log', '')
        self.addKnob(self.clear_knob)

    # --------------------------------------------------------
    #  knobChanged()
    #  Método especial de PythonPanel que se llama automáticamente
    #  cada vez que el usuario interactúa con un knob.
    #  Es el equivalente a un event listener en UI web.
    # --------------------------------------------------------
    def knobChanged(self, knob):

        if knob is self.start_knob:
            self._on_start()

        elif knob is self.stop_knob:
            self._on_stop()

        elif knob is self.clear_knob:
            self.log_knob.setValue('Log limpiado.')

    # --------------------------------------------------------
    #  _on_start()
    #  Lógica que se ejecuta al pulsar "Iniciar Servidor"
    # --------------------------------------------------------
    def _on_start(self):
        if nuke_server.running:
            self._log('⚠️  El servidor ya estaba corriendo.')
            return

        try:
            nuke_server.start()
            self.status_knob.setValue('🟢 Servidor activo')
            self._log(f'✅ Servidor iniciado en {HOST}:{PORT}')
        except Exception as e:
            self.status_knob.setValue('🔴 Error al iniciar')
            self._log(f'❌ Error: {e}')

    # --------------------------------------------------------
    #  _on_stop()
    #  Lógica que se ejecuta al pulsar "Detener Servidor"
    # --------------------------------------------------------
    def _on_stop(self):
        if not nuke_server.running:
            self._log('⚠️  El servidor ya estaba detenido.')
            return

        nuke_server.stop()
        self.status_knob.setValue('⬛ Servidor detenido')
        self._log('🛑 Servidor detenido correctamente.')

    # --------------------------------------------------------
    #  _log()
    #  Añade una línea al área de log del panel.
    #  Mantiene un máximo de 20 líneas para no saturar la UI.
    # --------------------------------------------------------
    def _log(self, message: str):
        current = self.log_knob.getValue()
        lines = current.split('\n') if current else []
        lines.append(message)
        # Mantenemos solo las últimas 20 líneas
        if len(lines) > 20:
            lines = lines[-20:]
        self.log_knob.setValue('\n'.join(lines))


# ============================================================
#  FUNCIÓN DE REGISTRO DEL PANEL
#  Esta función es llamada desde menu.py para registrar
#  el panel en el sistema de Nuke y añadirlo al menú.
# ============================================================
def add_panel():
    """Registra el panel en Nuke y lo añade al menú Windows."""

    # Registramos el panel con una función fábrica (lambda).
    # Nuke necesita saber cómo crear una nueva instancia del panel
    # cuando el usuario lo abre. Le pasamos una función que devuelve
    # una nueva instancia cada vez que se llama.
    nukescripts.registerPanel(
        'com.studio.pycharm_bridge',
        lambda: NukeServerPanel()
    )

    # Añadimos el panel al menú Windows de Nuke
    # para que el artista pueda abrirlo fácilmente
    nuke.menu('Pane').addCommand(
        'PyCharm Bridge',
        lambda: NukeServerPanel().show()
    )
