


from PyQt6 import QtWidgets

def make_sidebar(items:list[str])->QtWidgets.QListWidget:
    print("Sidebar items:", items)
    w = QtWidgets.QListWidget()
    w.addItems(items)
    w.setMinimumHeight(len(items) * 40)
    w.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Expanding)
    return w
