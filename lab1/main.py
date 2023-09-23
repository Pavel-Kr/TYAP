from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QListWidget, QSpinBox, QLineEdit, QLabel
from PyQt6.QtCore import pyqtSignal


class StringTreeNode:
    string = ""
    children = list()

    def __init__(self, string=""):
        self.string = string
        self.children = []

    def generation_step(self, grammar, max_len):
        if len(self.string) < max_len:
            for char in self.string:
                variants = grammar.get(char)
                if variants is not None:
                    for var in variants:
                        new_str = self.string.replace(char, var, 1)
                        node = StringTreeNode(new_str)
                        self.children.append(node)
                for child in self.children:
                    child.generation_step(grammar, max_len)

    def parse_node(self):
        strings = []
        if len(self.children) == 0:
            return [self.string]
        for child in self.children:
            strings_child = child.parse_node()
            for string_child in strings_child:
                string = self.string + "->" + string_child
                strings.append(string)
        return strings

    def get_result_as_string(self):
        strings = self.parse_node()
        str_arr = ""
        for string in strings:
            str_arr = str_arr + string + "\n"
        return str_arr


class StringGenerator:
    def __init__(self, grammar):
        self.grammar = grammar

    def load_grammar(self, grammar):
        self.grammar = grammar

    def generate_strings(self, start, max_len):
        root = StringTreeNode(start)
        root.generation_step(self.grammar, max_len)
        return root.parse_node()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.grammar_window = None
        self.string_len = 0
        self.grammar = {
            'S': ['aA', 'bS'],
            'A': ['aA', 'a']
        }

        self.generator = StringGenerator(self.grammar)

        self.setWindowTitle("Lab 1 TYAP")
        v_layout = QVBoxLayout()
        self.strings_list = QListWidget()
        len_spin_box = QSpinBox()
        len_spin_box.valueChanged.connect(self.on_spin_value_changed)
        generate_button = QPushButton("Generate strings")
        generate_button.clicked.connect(self.on_gen_button_clicked)
        grammar_button = QPushButton("Input grammar")
        grammar_button.clicked.connect(self.on_grammar_button_clicked)
        v_layout.addWidget(self.strings_list)
        v_layout.addWidget(len_spin_box)
        v_layout.addWidget(generate_button)
        v_layout.addWidget(grammar_button)
        container = QWidget()
        container.setLayout(v_layout)
        self.setCentralWidget(container)

    def on_spin_value_changed(self, value):
        self.string_len = value

    def on_gen_button_clicked(self):
        self.strings_list.clear()
        strings = self.generator.generate_strings('S', self.string_len)
        for string in strings:
            self.strings_list.addItem(string)

    def on_grammar_button_clicked(self):
        self.grammar_window = GrammarWindow()
        self.grammar_window.send_grammar.connect(self.update_grammar)
        self.grammar_window.show()

    def update_grammar(self, grammar):
        self.generator.load_grammar(grammar)
        print(grammar)


class GrammarWindow(QWidget):
    send_grammar = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.grammar_parser = GrammarParser()
        v_layout = QVBoxLayout()
        self.rules_layout = QVBoxLayout()
        self.generate_row(self.rules_layout)
        add_rule_button = QPushButton("Add rule")
        add_rule_button.clicked.connect(self.on_add_rule_button_clicked)
        save_grammar_button = QPushButton("Save grammar")
        save_grammar_button.clicked.connect(self.parse_layout)
        v_layout.addLayout(self.rules_layout)
        v_layout.addWidget(add_rule_button)
        v_layout.addWidget(save_grammar_button)
        self.setLayout(v_layout)

    def on_add_rule_button_clicked(self):
        self.generate_row(self.rules_layout)

    def generate_row(self, layout):
        rule_name = QLineEdit()
        arrow_label = QLabel("->")
        rule_desc = QLineEdit()
        h_layout = QHBoxLayout()
        h_layout.addWidget(rule_name)
        h_layout.addWidget(arrow_label)
        h_layout.addWidget(rule_desc)
        layout.addLayout(h_layout)

    def parse_layout(self):
        for i in range(self.rules_layout.count()):
            rule_layout = self.rules_layout.itemAt(i)
            rule_name = rule_layout.itemAt(0).widget().text()
            rule_desc = rule_layout.itemAt(2).widget().text()
            self.grammar_parser.parse_and_maybe_add_rule(rule_name, rule_desc)
        grammar = self.grammar_parser.get_grammar()
        if grammar is not None:
            self.send_grammar.emit(grammar)
            self.close()


class GrammarParser:
    def __init__(self):
        self.terminal = []
        self.non_terminal = []
        self.grammar = {}

    def parse_and_maybe_add_rule(self, name, desc):
        if len(name) != 1:
            print("Error: Grammar is not context free!")
            self.grammar.clear()
            return
        if not str.isupper(name[0]):
            print("Error: Rule name must contain 1 non-terminal (uppercase) symbol")
            self.grammar.clear()
            return
        rule_name = name[0]
        if rule_name not in self.non_terminal:
            self.non_terminal.append(rule_name)
        for char in desc:
            if str.isupper(char) and char not in self.non_terminal:
                self.non_terminal.append(char)
            elif char not in self.terminal:
                self.terminal.append(char)
        transitions = str.split(desc, "|")
        if self.grammar.get(rule_name) is not None:
            print("Error: rule already exists")
            self.grammar.clear()
            return
        self.grammar[rule_name] = transitions

    def get_grammar(self):
        for sym in self.non_terminal:
            if self.grammar.get(sym) is None:
                print(f"Error: {sym} rule doesn't have a description")
                self.grammar.clear()
                return None
        return self.grammar


app = QApplication([])

window = MainWindow()
window.show()

app.exec()
