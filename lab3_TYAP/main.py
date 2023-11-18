from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, \
    QHBoxLayout, QWidget, QListWidget, QSpinBox, QLineEdit, QLabel, QPlainTextEdit, QFileDialog
from dmp import DMP


class MainWindow(QMainWindow):
    dmp = DMP()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("3 лаба ТЯП")
        v_layout = QVBoxLayout()
        self.string_edit = QLineEdit()
        self.check_field = QPlainTextEdit()
        self.check_field.setReadOnly(True)

        check_button = QPushButton("Проверить цепочку")
        check_button.clicked.connect(self.on_check_button_click)

        load_button = QPushButton("Загрузить автомат")
        load_button.clicked.connect(self.on_load_button_clicked)

        v_layout.addWidget(self.string_edit)
        v_layout.addWidget(self.check_field)
        v_layout.addWidget(check_button)
        v_layout.addWidget(load_button)

        container = QWidget()
        container.setLayout(v_layout)
        self.setCentralWidget(container)

    def on_load_button_clicked(self):
        self.check_field.clear()
        path = QFileDialog.getOpenFileName()[0]
        if path != "":
            error_msg = self.dmp.load_dmp_from_file(path)
            if error_msg != "":
                self.check_field.setPlainText(error_msg)

    def on_check_button_click(self):
        _string = self.string_edit.text()
        progress = ""
        start_config = self.dmp.init_check(_string)
        if start_config[0] is False:
            self.check_field.setPlainText(start_config[1])
            return
        progress += start_config[1]
        self.check_field.setPlainText(progress)
        step = self.dmp.check_step()
        while step[0] is True:
            progress += " |— "
            progress += step[1]
            self.check_field.setPlainText(progress)
            step = self.dmp.check_step()
        if step[1] != "":
            progress += step[1]
            self.check_field.setPlainText(progress)


app = QApplication([])
window = MainWindow()
window.show()

app.exec()