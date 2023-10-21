from iteration_utilities import duplicates
def remove_curly_brackets(string):
    if string[0] != '{' or string[-1] != '}':
        print("Syntax error: no curly brackets")
        return
    return string[1:-1]


def split_set(string):
    no_brackets = remove_curly_brackets(string)
    if no_brackets is not None:
        return no_brackets.split(",")
    return None


def parse_description(description):
    no_spaces = str.join("", description.split())
    desc = str.split(no_spaces, ";")
    if len(desc) != 4:
        return None, "Ошибка описания автомата: не хватает деталей описания"
    res = {}

    states = split_set(desc[0])
    if states is None:
        return None, "Синтаксическая ошибка в описании состояний автомата"
    dups = list(duplicates(states))
    if len(dups) != 0:
        return None, f"Состояния {dups} встречаются больше одного раза"
    res["states"] = states

    alphabet = split_set(desc[1])
    if alphabet is None:
        return None, "Синтаксическая ошибка в описании алфавита"
    dups = list(duplicates(alphabet))
    if len(dups) != 0:
        return None, f"Символы {dups} встречаются в алфавите больше одного раза"
    for a in alphabet:
        if len(a) != 1:
            return None, f"Неправильный символ алфавита {a}, длина символа должна быть равна 1"
    res["alphabet"] = alphabet

    start_state = desc[2]
    if start_state not in states:
        return None, f"Стартовое состояние {start_state} отсутствует в списке состояний"
    res["start state"] = start_state

    final_states = split_set(desc[3])
    if final_states is None:
        return None, "Синтаксическая ошибка в описании конечных состояний автомата"
    dups = list(duplicates(final_states))
    if len(dups) != 0:
        return None, f"Конечные состояния {dups} встречаются больше одного раза"
    for s in final_states:
        if s not in states:
            return None, f"Конечное состояние {s} отсутствует в списке состояний"
    res["final states"] = final_states
    return (res, "")


class Fsm:
    fsm = None
    current_state = ""
    _string = ""

    def load_fsm_from_file(self, file_path):
        with open(file_path) as f:
            description = f.readline()
            m = parse_description(description)
            if m[0] is None:
                return m[1]
            self.fsm = m[0]
            print(self.fsm)
            table = [s for s in list(f) if s != '\n']
            print(table)
            if len(table) != len(self.fsm["states"]):
                return "Количество строк в таблице переходов должно быть равно количеству состояний"
            states = self.fsm["states"]
            trans_dict = {}
            for i in range(len(table)):
                if table[i][-1] == '\n':
                    table[i] = table[i][:-1]
                print(table[i])
                transitions = table[i].split()
                if len(transitions) != len(self.fsm["alphabet"]):
                    return "Количество столбцов в таблице переходов должно быть равно количеству символов алфавита"
                print(transitions)
                alphabet = self.fsm["alphabet"]
                d = {}
                for j in range(len(alphabet)):
                    if transitions[j] not in states:
                        return f"Состояние {transitions[j]} отсутствует в списке состояний"
                    if transitions[j] != '-':
                        d[alphabet[j]] = transitions[j]
                trans_dict[states[i]] = d
            self.fsm["transitions"] = trans_dict
            print(self.fsm)
            return ""

    def init_check(self, string):
        if self.fsm is None:
            return False, "Конечный автомат не инициализирован"
        self._string = string
        self.current_state = self.fsm["start state"]
        print("Current state = ", self.current_state)
        return True, f"({self.current_state}, {self._string})"

    def check_step(self):
        if self._string == "":
            if self.current_state not in self.fsm["final states"]:
                return False, "\nЦепочка не распознана: автомат не в конечном состоянии"
            return False, "\nЦепочка распознана"
        sym = self._string[0]
        if sym not in self.fsm["alphabet"]:
            return False, f"\nЦепочка не распознана: символ {sym} отсутствует в алфавите"
        new_state = self.fsm["transitions"][self.current_state].get(sym)
        if new_state is None:
            return False, f"\nЦепочка не распознана: нет перехода из состояния {self.current_state} по символу {sym}"
        self.current_state = new_state
        self._string = self._string[1:]
        return True, f"({self.current_state}, {self._string})"
