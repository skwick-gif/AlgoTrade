
from PyQt6 import QtWidgets

def make_sidebar(items:list[str])->QtWidgets.QListWidget:
    w = QtWidgets.QListWidget()
    w.addItems(items)
    return w
