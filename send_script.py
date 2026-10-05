def main():
    import nuke

    def crear_grade_node():
        node = nuke.createNode('Grade')
        node['blackpoint'].setValue(0.0)
        node['whitepoint'].setValue(1.2)
        node['multiply'].setValue([1.1, 1.0, 0.95, 1.0])
        node['label'].setValue('Grade - PyCharm')
        print(f"Nodo creado: {node.name()}")
        return node

    def organizar_nodos():
        selected = nuke.selectedNodes()
        if not selected:
            nuke.message("No hay nodos seleccionados.")
            return
        for i, node in enumerate(selected):
            node.setXpos(i * 150)
            node.setYpos(0)
        print(f"{len(selected)} nodos organizados.")

    crear_grade_node()
    #organizar_nodos()