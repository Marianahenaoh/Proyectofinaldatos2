import sys
import random
from PyQt5 import QtWidgets, QtGui, QtCore
from grafos_ui import Ui_MainWindow
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem


class Nodo(QGraphicsEllipseItem):
    def __init__(self, x, y, radius, id, app):
        super().__init__(-radius, -radius, 2 * radius, 2 * radius)
        self.setBrush(QtGui.QBrush(QtGui.QColor("lightblue")))
        self.setPen(QtGui.QPen(QtCore.Qt.black))
        self.id = id
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable)
        self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges)
        self.text_item = QGraphicsTextItem(f"Nodo {self.id}", self)
        self.text_item.setPos(-10, -10)
        self.app = app
        self.aristas = []

    def agregar_arista(self, arista):
        self.aristas.append(arista)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for arista in self.aristas:
                arista.actualizar_posiciones()
        return super().itemChange(change, value)


class Arista(QGraphicsLineItem):
    def __init__(self, nodo1, nodo2, peso, scene):
        super().__init__()
        self.nodo1 = nodo1
        self.nodo2 = nodo2
        self.peso = peso
        self.scene = scene
        self.text_item = QGraphicsTextItem(str(self.peso))
        self.scene.addItem(self.text_item)
        self.actualizar_posiciones()
        self.setFlag(QGraphicsLineItem.ItemIsSelectable)
        self.setPen(QtGui.QPen(QtCore.Qt.black))

    def actualizar_posiciones(self):
        x1, y1 = self.nodo1.scenePos().x(), self.nodo1.scenePos().y()
        x2, y2 = self.nodo2.scenePos().x(), self.nodo2.scenePos().y()
        self.setLine(x1, y1, x2, y2)
        self.text_item.setPos((x1 + x2) / 2, (y1 + y2) / 2)


class GrafoApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(GrafoApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.scene = QGraphicsScene()
        self.ui.graphicsView.setScene(self.scene)
        self.ui.btnPintarGrafo.clicked.connect(self.dibujar_grafo)
        self.nodos = []
        self.aristas = []

    def dibujar_grafo(self):
        try:
            self.scene.clear()
            self.nodos.clear()
            self.aristas.clear()
            matriz = self.obtener_matriz()
            self.dibujar_nodos_y_aristas(matriz)
            self.ejecutar_dijkstra(matriz, inicio=0, fin=3)
        except Exception as e:
            print(f"Error al dibujar el grafo: {e}")

    def obtener_matriz(self):
        filas = self.ui.tableWidget.rowCount()
        columnas = self.ui.tableWidget.columnCount()
        matriz = []
        for i in range(filas):
            fila = []
            for j in range(columnas):
                item = self.ui.tableWidget.item(i, j)
                valor = int(item.text()) if item and item.text().isdigit() else 0
                fila.append(valor)
            matriz.append(fila)
        return matriz

    def dibujar_nodos_y_aristas(self, matriz):
        num_nodos = len(matriz)
        radius = 20
        width = self.ui.graphicsView.width() - 100
        height = self.ui.graphicsView.height() - 100

        for i in range(num_nodos):
            x = random.randint(50, width)
            y = random.randint(50, height)
            nodo = Nodo(x, y, radius, i + 1, self)
            nodo.setPos(x, y)
            self.scene.addItem(nodo)
            self.nodos.append(nodo)

        for i in range(num_nodos):
            for j in range(i + 1, num_nodos):
                peso = matriz[i][j]
                if peso > 0:
                    nodo1 = self.nodos[i]
                    nodo2 = self.nodos[j]
                    arista = Arista(nodo1, nodo2, peso, self.scene)
                    self.aristas.append(arista)
                    self.scene.addItem(arista)
                    nodo1.agregar_arista(arista)
                    nodo2.agregar_arista(arista)

    def ejecutar_dijkstra(self, matriz, inicio, fin):
        n = len(matriz)
        distancias = [float('inf')] * n
        visitados = [False] * n
        predecesores = [-1] * n
        distancias[inicio] = 0

        for _ in range(n):
            min_dist = float('inf')
            min_index = -1
            for i in range(n):
                if not visitados[i] and distancias[i] < min_dist:
                    min_dist = distancias[i]
                    min_index = i

            if min_index == -1:
                break

            visitados[min_index] = True
            for vecino in range(n):
                if matriz[min_index][vecino] > 0 and not visitados[vecino]:
                    nueva_dist = distancias[min_index] + matriz[min_index][vecino]
                    if nueva_dist < distancias[vecino]:
                        distancias[vecino] = nueva_dist
                        predecesores[vecino] = min_index

        camino = []
        nodo_actual = fin
        while nodo_actual != -1:
            camino.insert(0, nodo_actual)
            nodo_actual = predecesores[nodo_actual]

        self.resaltar_camino(camino)

    def resaltar_camino(self, camino):
        for i in range(len(camino) - 1):
            nodo1 = self.nodos[camino[i]]
            nodo2 = self.nodos[camino[i + 1]]
            arista = next((a for a in self.aristas if a.nodo1 == nodo1 and a.nodo2 == nodo2), None)
            if arista:
                arista.setPen(QtGui.QPen(QtCore.Qt.red, 3))
            nodo1.setBrush(QtGui.QBrush(QtGui.QColor("yellow")))
            nodo2.setBrush(QtGui.QBrush(QtGui.QColor("yellow")))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = GrafoApp()
    window.show()
    sys.exit(app.exec_())
