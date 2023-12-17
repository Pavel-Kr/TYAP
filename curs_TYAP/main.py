from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, \
    QDialog, QFileDialog
from PyQt6 import uic
import itertools


def deliverErrorMessage(text):
    msg = QMessageBox()
    msg.setWindowTitle("Ошибка!")
    msg.setText(text)
    msg.setIcon(QMessageBox.Icon.Critical)
    button = msg.exec()
    if button == QMessageBox.StandardButton.Ok:
        return


class CustomDialog(QDialog):
    def __init__(self, ui_filepath):
        super(CustomDialog, self).__init__()
        uic.loadUi(ui_filepath, self)


stack = ""


class Group:
    options = []
    symbol = ""
    is_leaf = True
    is_iterative = False
    add_option = False
    current_option_index = [0]
    iteration_count = 0
    iteration_index = 0
    iterative_child_count = 0
    iterative_child_indices = [] # indices of iterative children in options array (outer, inner)
    child_iterations = [[]] # iteration counts for children (unique permutations)
    child_iterations_index = 0 # permutation index

    def __init__(self):
        self.options = [[]]
        self.symbol = ""
        self.is_leaf = True
        self.is_iterative = False
        self.add_option = False
        self.current_option_index = [0]
        self.iteration_count = 0
        self.iteration_index = 0

    def set_iteration_count(self, count):
        if self.is_iterative:
            self.iteration_count = count
            self.current_option_index = [0] * self.iteration_count
            self.iteration_index = 0

    def add_group(self, group):
        if self.add_option:
            self.options.append([group])
        else:
            self.options[-1].append(group)
        self.add_option = False

    def parse_regex(self, regex: str):
        if regex == "":
            return ""
        global stack
        sym = regex[0]
        if sym == "(":
            stack += "("
            gr = Group()
            self.add_group(gr)
            self.is_leaf = False
            regex = regex[1:]
            regex = gr.parse_regex(regex)
            return self.parse_regex(regex)
        elif sym.isalnum():
            gr = Group()
            gr.symbol = sym
            self.add_group(gr)
            self.is_leaf = False
            regex = regex[1:]
            return self.parse_regex(regex)
        elif sym == "+":
            self.add_option = True
            regex = regex[1:]
            return self.parse_regex(regex)
        elif sym == ")":
            if len(stack) == 0:
                deliverErrorMessage("Синтаксическая ошибка в РВ: лишняя ')'")
                return
            stack = stack[1:]
            has_star = False
            if len(regex) > 1 and regex[1] == "*":
                has_star = True
            if has_star:
                self.is_iterative = True
                regex = regex[2:]
            else:
                regex = regex[1:]
            return regex

    def count_iteratives(self):
        for i in range(len(self.options)):
            current_option = self.options[i]
            for j in range(len(current_option)):
                group = current_option[j]
                if group.is_iterative:
                    self.iterative_child_count += 1
                    self.iterative_child_indices.append((i, j))
        counts = [0] * self.iterative_child_count
        self.child_iterations = list(set(list(itertools.permutations(counts))))
        for option in self.options:
            for group in option:
                group.count_iteratives()

    def parse_node(self, switch_option: bool):
        if self.is_leaf:
            return switch_option, self.symbol
        if self.is_iterative:
            return self.parse_node_iterative(switch_option)
        current_option = self.options[self.current_option_index[0]] # Список
        local_switch_option = switch_option
        ret_str = ""
        for group in current_option:
            local_switch_option, string = group.parse_node(local_switch_option)
            ret_str += string
        ret_switch_option = False
        if local_switch_option:
            self.current_option_index[0] += 1
            if self.current_option_index[0] >= len(self.options):
                self.current_option_index[0] = 0
                ret_switch_option = True
        if ret_switch_option:
            if self.iterative_child_count > 0:
                self.child_iterations_index += 1
                if self.child_iterations_index >= len(self.child_iterations):
                    self.child_iterations_index = 0
                    # increase amount of iterations
                    counts = list(self.child_iterations[0])
                    min_iter_count = 100000
                    min_index = 0
                    for i in range(len(counts)):
                        if counts[i] < min_iter_count:
                            min_iter_count = counts[i]
                            min_index = i
                    counts[min_index] += 1
                    self.child_iterations = list(set(list(itertools.permutations(counts))))
                for k in range(len(self.child_iterations)):
                    i, j = self.iterative_child_indices[k]
                    group = self.options[i][j]
                    group.set_iteration_count(self.child_iterations[self.child_iterations_index][k])
        return ret_switch_option, ret_str

    def parse_node_iterative(self, switch_option: bool):
        ret_switch_option = switch_option
        ret_str = ""
        for i in range(self.iteration_count):
            current_option = self.options[self.current_option_index[i]]  # Список
            local_switch_option = ret_switch_option

            for group in current_option:
                local_switch_option, string = group.parse_node(local_switch_option)
                ret_str += string
            ret_switch_option = False
            if local_switch_option:
                self.current_option_index[i] += 1
                if self.current_option_index[i] >= len(self.options):
                    self.current_option_index[i] = 0
                    ret_switch_option = True
        return ret_switch_option, ret_str


class MainWindow(QMainWindow):
    regex = ""

    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("main.ui", self)
        self.genRegexButton.clicked.connect(self.genRegexButtonClicked)
        self.genStringsButton.clicked.connect(self.genStringsButtonClicked)
        self.setRegexButton.clicked.connect(self.setRegexButtonClicked)
        self.authorAction.triggered.connect(self.authorActionTriggered)
        self.themeAction.triggered.connect(self.themeActionTriggered)
        self.fileWriteAction.triggered.connect(self.fileWriteActionTriggered)
        self.fileReadAction.triggered.connect(self.fileReadActionTriggered)
        self.helpAction.triggered.connect(self.helpActionTriggered)
        self.alphabetEdit.setFocus()
        self.fixedSubstr = ""

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
        alphabet = noSpaces.split(",")
        for sym in alphabet:
            if len(sym) > 1:
                deliverErrorMessage("Алфавит должен содержать только одиночные символы!")
                return

        self.fixedSubstr = self.substrEdit.text()
        if self.fixedSubstr == "":
            deliverErrorMessage("Отсутствует фиксированная подцепочка!")
            return

        for sym in self.fixedSubstr:
            if sym not in alphabet:
                deliverErrorMessage(f"Символ {sym} фиксированной подцепочки отсутствует в алфавите")
                return

        multiplier = self.multSpinBox.value()

        self.regex = ""
        self.writeAlphabetToRegex(alphabet, multiplier)
        self.regex += "*"
        self.writeSubstringToRegex(self.fixedSubstr, alphabet, multiplier)
        self.writeAlphabetToRegex(alphabet, multiplier)
        self.regex += "*"

        self.regexEdit.clear()
        self.regexEdit.setText(self.regex)

    def genStringsButtonClicked(self):
        self.regex = self.regexEdit.text()
        if self.regex == "":
            deliverErrorMessage("Регулярное выражение не задано!")
            return
        minLength = self.minLengthSpinBox.value()
        if minLength < len(self.fixedSubstr):
            deliverErrorMessage("Минимальная длина цепочки должна быть не меньше, чем длина фиксированной подцепочки!")
            return

        maxLength = self.maxLengthSpinBox.value()
        if maxLength < minLength:
            deliverErrorMessage("Максимальная длина должна быть больще минимальной!")
            return

        root = Group()
        root.parse_regex(self.regex)
        root.count_iteratives()
        self.genStringsEdit.clear()
        while True:
            switch_option, string = root.parse_node(True)
            if len(string) > maxLength:
                break
            if len(string) >= minLength:
                self.genStringsEdit.appendPlainText(string)

    def setRegexButtonClicked(self):
        self.regexEdit.clear()
        self.regexEdit.setReadOnly(False)
        self.regexEdit.setFocus()

    def authorActionTriggered(self):
        dlg = CustomDialog("author.ui")
        dlg.exec()

    def themeActionTriggered(self):
        dlg = CustomDialog("theme.ui")
        dlg.exec()

    def fileWriteActionTriggered(self):
        path = QFileDialog.getSaveFileName()[0]
        if path != "":
            file = open(path, "w")
            file.write(self.regexEdit.text())
            file.write(self.genStringsEdit.toPlainText())
            file.close()

    def fileReadActionTriggered(self):
        path = QFileDialog.getOpenFileName()[0]
        if path != "":
            with open(path) as file:
                for line in file:
                    if line[-1] == "\n":
                        line = line[:-1]
                    s = line.split()
                    if s[1] != "=":
                        deliverErrorMessage("Некорректный формат файла, см. справку")
                        return
                    if s[0] == "alphabet":
                        alphabet = str.join("", s[2:])
                        self.alphabetEdit.setText(alphabet)
                    elif s[0] == "multiplier":
                        try:
                            multiplier = int(s[2])
                        except ValueError:
                            deliverErrorMessage(f"Кратность должна быть числом, а не {s[2]}")
                            return
                        self.multSpinBox.setValue(multiplier)
                    elif s[0] == "substring":
                        self.substrEdit.setText(s[2])
                    elif s[0] == "minLength":
                        try:
                            minLength = int(s[2])
                        except ValueError:
                            deliverErrorMessage(f"Минимальная длина цепочки должна быть числом, а не {s[2]}")
                            return
                        self.minLengthSpinBox.setValue(minLength)
                    elif s[0] == "maxLength":
                        try:
                            maxLength = int(s[2])
                        except ValueError:
                            deliverErrorMessage(f"Максимальная длина цепочки должна быть числом, а не {s[2]}")
                            return
                        self.maxLengthSpinBox.setValue(maxLength)
                    else:
                        deliverErrorMessage(f"Неизвестный параметр {s[0]}, см. справку")
                        return

    def helpActionTriggered(self):
        dlg = CustomDialog("help.ui")
        dlg.exec()


app = QApplication([])
window = MainWindow()
window.show()
app.exec()