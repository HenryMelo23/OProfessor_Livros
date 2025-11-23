from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit
)
from PyQt5.QtCore import Qt


class CurrencyInput(QLineEdit):
    def __init__(self, initial_value_cents=0, parent=None):
        super().__init__(parent)
        self.raw_value = str(initial_value_cents)
        self.update_display()
        
        # Conecta o manipulador de eventos
        self.textChanged.connect(self.handle_text_change)

    def handle_text_change(self, text):
        # Remove todos os caracteres não numéricos e zeros iniciais
        raw = ''.join(filter(str.isdigit, text)).lstrip('0')

        if not raw:
            self.raw_value = '0'
        else:
            self.raw_value = raw
        
        self.update_display()

    def update_display(self):
        # Valor em centavos (mínimo de 0)
        value_cents = int(self.raw_value) if self.raw_value else 0
        
        # Converte para string formatada R$ X,XX
        s = str(value_cents).zfill(3)
        formatted_value = f"{s[:-2]},{s[-2:]}"

        # Evita loops infinitos ou mover o cursor ao atualizar
        if self.text().replace('.', ',') != formatted_value:
            self.setText(formatted_value)


    def get_value_cents(self):
        # Retorna o valor limpo em centavos para o filtro
        return int(self.raw_value) if self.raw_value else 0


class FilterWindow(QWidget):
    def __init__(self, home_ref):
        super().__init__()
        self.home_ref = home_ref
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Filtros")
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.select_disponivel = QComboBox()
        self.select_disponivel.addItems([
            "Não filtrar",
            "Disponível",
            "Indisponível"
        ])
        layout.addWidget(QLabel("Disponibilidade:"))
        layout.addWidget(self.select_disponivel)

        self.input_autor = QLineEdit()
        layout.addWidget(QLabel("Autor contém:"))
        layout.addWidget(self.input_autor)
        # ACIONA FILTRO COM ENTER
        self.input_autor.returnPressed.connect(self.aplicar) 

        self.input_caracteristica = QLineEdit()
        layout.addWidget(QLabel("Característica contém:"))
        layout.addWidget(self.input_caracteristica)
        # ACIONA FILTRO COM ENTER
        self.input_caracteristica.returnPressed.connect(self.aplicar)

        layout.addWidget(QLabel("Preço mínimo / máximo:"))

        price_layout = QHBoxLayout()
        
        self.input_preco_min = CurrencyInput(initial_value_cents=0)
        self.input_preco_max = CurrencyInput(initial_value_cents=3000)
        
        # ACIONA FILTRO COM ENTER
        self.input_preco_min.returnPressed.connect(self.aplicar)
        self.input_preco_max.returnPressed.connect(self.aplicar)

        price_layout.addWidget(QLabel("Min R$"))
        price_layout.addWidget(self.input_preco_min)
        price_layout.addWidget(QLabel("Max R$"))
        price_layout.addWidget(self.input_preco_max)
        layout.addLayout(price_layout)


        btn_filtrar = QPushButton("Aplicar filtros")
        btn_filtrar.clicked.connect(self.aplicar)
        layout.addWidget(btn_filtrar)

        btn_limpar = QPushButton("Limpar filtros")
        btn_limpar.clicked.connect(self.limpar)
        layout.addWidget(btn_limpar)

    def aplicar(self):
        # Obtemos o valor limpo (em centavos) diretamente da nova classe
        min_val_cents = self.input_preco_min.get_value_cents()
        max_val_cents = self.input_preco_max.get_value_cents()

        # Garante que o valor máximo é maior ou igual ao mínimo
        if min_val_cents > max_val_cents:
            min_val_cents, max_val_cents = max_val_cents, min_val_cents
        
        # Se max_val_cents for 0 (campo vazio), define um valor alto para não limitar
        if max_val_cents == 0:
            max_val_cents = 999900 # 9999,00 R$
        
        filtros = {
            "disponivel": self.select_disponivel.currentText(),
            "autor": self.input_autor.text(),
            "caracteristica": self.input_caracteristica.text(),
            "preco_min": min_val_cents,
            "preco_max": max_val_cents,
        }
        
        self.home_ref.aplicar_filtros(filtros)
        self.close()

    def limpar(self):
        # Redefine a UI para o estado inicial
        self.select_disponivel.setCurrentIndex(0)
        self.input_autor.clear()
        self.input_caracteristica.clear()
        
        # Limpar os campos CurrencyInput para 0 e 30.00
        self.input_preco_min.raw_value = '0'
        self.input_preco_min.update_display()
        self.input_preco_max.raw_value = '3000'
        self.input_preco_max.update_display()
        
        self.home_ref.limpar_filtros()
        self.close()