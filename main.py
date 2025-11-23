# main.py
import sys
from PyQt5.QtWidgets import QApplication
from app.app import App # A classe App contém a lógica de transição

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = App() # 💡 AQUI a LoginWindow já é definida como a tela atual
    janela.resize(900, 600)
    janela.show()
    sys.exit(app.exec_())