from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6 import uic, QtGui, QtCore


def deliverErrorMessage(text):
    msg = QMessageBox()
    msg.setWindowTitle("Ошибка!")
    msg.setText(text)
    msg.setIcon(QMessageBox.Icon.Critical)
    button = msg.exec()
    if button == QMessageBox.StandardButton.Ok:
        return

class MainWindow(QMainWindow):
    regex = ""

    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("main.ui", self)
        self.genRegexButton.clicked.connect(self.genRegexButtonClicked)
        self.genStringsButton.clicked.connect(self.genStringsButtonClicked)

    def writeAlphabetToRegex(self, alphabet, count, add_par = True):
        if count > 1 and add_par:
            self.regex += "("
        for i in range(count):
            self.regex += "("
            for sym in alphabet:
                self.regex += sym + "+"
            self.regex = self.regex[:-1]
            self.regex += ")"
        if count > 1 and add_par:
            self.regex += ")"

    def writeSubstringToRegex(self, substr, alphabet, multiplier):
        mod = len(substr) % multiplier
        print(mod)
        if mod == 0:
            self.regex += substr
            return
        groupCount = multiplier - len(substr)
        self.regex += "("
        self.regex += "("
        self.writeAlphabetToRegex(alphabet, groupCount, False)
        self.regex += substr
        self.regex += ")+("
        self.regex += substr
        self.writeAlphabetToRegex(alphabet, groupCount, False)
        self.regex += "))"


    def genRegexButtonClicked(self):
        alphabetStr = self.alphabetEdit.text()
        if alphabetStr == "":
            deliverErrorMessage("Алфавит не содержит ни одного символа!")
            return

        noSpaces = str.join("", alphabetStr.split())
        print(noSpaces)
        alphabet = noSpaces.split(",")
        for sym in alphabet:
            if len(sym) > 1:
                deliverErrorMessage("Алфавит должен содержать только одиночные символы!")
                return

        print(alphabet)

        self.fixedSubstr = self.substrEdit.text()
        if self.fixedSubstr == "":
            deliverErrorMessage("Отсутствует фиксированная подцепочка!")
            return

        for sym in self.fixedSubstr:
            if sym not in alphabet:
                deliverErrorMessage(f"Символ {sym} фиксированной подцепочки отсутствует в алфавите")
                return

        print(self.fixedSubstr)

        multiplier = self.multSpinBox.value()
        print(multiplier)

        # 3
        # ab
        # ((a+b+c)(a+b+c)(a+b+c))*
        # (((a+b+c)ab)+(ab(a+b+c)))((a+b+c)(a+b+c)(a+b+c))*

        # root
        # group*
        # group(a+b+c) group(a+b+c) group(a+b+c)

        self.regex = ""
        self.writeAlphabetToRegex(alphabet, multiplier)
        self.regex += "*"
        self.writeSubstringToRegex(self.fixedSubstr, alphabet, multiplier)
        self.writeAlphabetToRegex(alphabet, multiplier)
        self.regex += "*"

        self.regexEdit.clear()
        self.regexEdit.setText(self.regex)

    def genStringsButtonClicked(self):
        if self.regex == "":
            deliverErrorMessage("Регулярное выражение не задано!")
            return
        minLength = self.minLengthSpinBox.value()
        if minLength < len(self.fixedSubstr):
            deliverErrorMessage("Минимальная длина цепочки должна быть не меньше, чем длина фиксированной подцепочки!")
            return

        print(minLength)

        maxLength = self.maxLengthSpinBox.value()
        if maxLength < minLength:
            deliverErrorMessage("Максимальная длина должна быть больще минимальной!")
            return

        print(maxLength)


app = QApplication([])
window = MainWindow()
window.show()
app.exec()