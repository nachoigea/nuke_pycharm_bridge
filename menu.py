import nuke

try:

    # Importamos la función que registra el panel.
    # Al importar nuke_server_panel, Python también importa
    # nuke_server automáticamente (por la línea 'from nuke_server
    # import nuke_server'), inicializando la instancia global.
    from nuke_server_panel import add_panel

    # Registramos el panel en Nuke
    add_panel()

    # Añadimos una entrada en el menú principal de Nuke
    # para poder abrir el panel desde la barra de menús.
    # Esto crea: Menú "Studio" > "PyCharm Bridge"
    toolbar = nuke.menu('Nuke')
    studio_menu = toolbar.addMenu('Studio')
    studio_menu.addCommand(
        'PyCharm Bridge',
        lambda: __import__('nuke_server_panel').NukeServerPanel().show(),
        # Atajo de teclado opcional (puedes cambiar o quitar)
        'ctrl+shift+p'
    )

    print("[menu.py] PyCharm Bridge cargado correctamente.")

except ImportError as e:
    # Si no encuentra los archivos, informamos al usuario
    nuke.warning(
        f"[PyCharm Bridge] No se pudieron cargar los archivos del servidor.\n"
        f"Asegúrate de que nuke_server.py y nuke_server_panel.py\n"
        f"están en: C:/Users/TU_USUARIO/.nuke/\n\n"
        f"Error técnico: {e}"
    )
except Exception as e:
    nuke.warning(f"[PyCharm Bridge] Error inesperado al cargar: {e}")