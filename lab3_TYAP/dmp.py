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
    if len(desc) != 6:
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

    stack_alphabet = split_set(desc[2])
    if stack_alphabet is None:
        return None, "Синтаксическая ошибка в описании алфавита стека"
    dups = list(duplicates(stack_alphabet))
    if len(dups) != 0:
        return None, f"Символы {dups} встречаются в алфавите стека больше одного раза"
    for a in stack_alphabet:
        if len(a) != 1:
            return None, f"Неправильный символ алфавита стека {a}, длина символа должна быть равна 1"
    res["stack alphabet"] = stack_alphabet

    start_state = desc[3]
    if start_state not in states:
        return None, f"Стартовое состояние {start_state} отсутствует в списке состояний"
    res["start state"] = start_state

    start_stack = desc[4]
    if start_stack not in stack_alphabet:
        return None, f"Стартовый символ стека {start_stack} отсутствует в алфавите стека"
    res["start stack"] = start_stack

    final_states = split_set(desc[5])
    if final_states is None:
        return None, "Синтаксическая ошибка в описании конечных состояний автомата"
    dups = list(duplicates(final_states))
    if len(dups) != 0:
        return None, f"Конечные состояния {dups} встречаются больше одного раза"
    for s in final_states:
        if s not in states:
            return None, f"Конечное состояние {s} отсутствует в списке состояний"
    res["final states"] = final_states
    return res, ""


def remove_brackets(string):
    if string[0] != '(' or string[-1] != ')':
        print("Syntax error: no brackets")
        return
    return string[1:-1]


def parse_transition(transition):
    no_spaces = str.join("", transition.split())
    transition_spilt = str.split(no_spaces, "=")
    if len(transition_spilt) != 2:
        return None

    state = remove_brackets(transition_spilt[0])
    action = remove_brackets(transition_spilt[1])
    state_split = str.split(state, ",")
    if len(state_split) != 3:
        return None
    action_split = str.split(action, ",")
    if len(action_split) != 2:
        return None

    for s in state_split:
        if s == "":
            return None

    for s in action_split:
        if s == "":
            return None

    if state_split[1] == "E":
        state_split[1] = ""

    if state_split[2] == "E":
        state_split[2] = ""

    if action_split[1] == "E":
        action_split[1] = ""

    return state_split, action_split


class DMP:
    dmp = None
    current_state = ""
    stack = ""
    _string = ""

    def load_dmp_from_file(self, file_path):
        with open(file_path) as f:
            description = f.readline()
            m = parse_description(description)
            if m[0] is None:
                return m[1]
            self.dmp = m[0]
            table = [s for s in list(f) if s != '\n']
            states = self.dmp["states"]
            trans_dict = {}
            for i in range(len(table)):
                if table[i][-1] == '\n':
                    table[i] = table[i][:-1]
                transitions = parse_transition(table[i])
                if transitions is None:
                    return f"Синтаксическая ошибка в {i + 1}-м правиле: ошибка чтения перехода"
                alphabet = self.dmp["alphabet"]
                stack_alphabet = self.dmp["stack alphabet"]
                d = {}
                state = transitions[0]
                action = transitions[1]
                if state[0] not in states:
                    return f"Синтаксическая ошибка в {i + 1}-м правиле: состояние {state[0]} отсутствует в списке состояний"
                if state[1] != "" and state[1] not in alphabet:
                    return f"Синтаксическая ошибка в {i + 1}-м правиле: символ {state[1]} отсутствует в алфавите"
                if state[2] != "" and state[2] not in stack_alphabet:
                    return f"Синтаксическая ошибка в {i + 1}-м правиле: символ {state[2]} отсутствует в алфавите стека"
                if action[0] not in states:
                    return f"Синтаксическая ошибка в {i + 1}-м правиле: состояние {action[0]} отсутствует в списке состояний"
                for sym in action[1]:
                    if sym not in stack_alphabet:
                        return f"Синтаксическая ошибка в {i + 1}-м правиле: символ {sym} отсутствует в алфавите стека"
                state_tr = trans_dict.get(state[0])
                if state_tr is None:
                    d1 = {state[2]: (action[0], action[1])}
                    d[state[1]] = d1
                    trans_dict[state[0]] = d
                    continue

                str_sym_tr = state_tr.get(state[1])
                if str_sym_tr is None:
                    d[state[2]] = (action[0], action[1])
                    state_tr[state[1]] = d
                    continue

                stack_sym_tr = str_sym_tr.get(state[2])
                if stack_sym_tr is not None:
                    return f"Синтаксическая ошибка в {i + 1}-м правиле: переход по состоянию {state} уже существует"

                str_sym_tr[state[2]] = (action[0], action[1])
            self.dmp["transitions"] = trans_dict
            print(self.dmp)
            return ""

    def init_check(self, string):
        if self.dmp is None:
            return False, "Конечный автомат не инициализирован"
        self._string = string
        self.current_state = self.dmp["start state"]
        self.stack = self.dmp["start stack"]
        return True, f"({self.current_state}, {self._string}, {self.stack})"

    def check_step(self):
        if self._string == "" and self.stack == "":
            if self.current_state not in self.dmp["final states"]:
                return False, "\nЦепочка не распознана: автомат не в конечном состоянии"
            return False, "\nЦепочка распознана"

        if self.stack == "":
            return False, "\nЦепочка не распознана: стек пуст, но на ленте еще остались символы"

        sym = ""
        if self._string != "":
            sym = self._string[0]
            if sym not in self.dmp["alphabet"]:
                return False, f"\nЦепочка не распознана: символ {sym} отсутствует в алфавите"

        sym_tr = self.dmp["transitions"][self.current_state].get(sym)
        if sym_tr is None:
            return False, f"\nЦепочка не распознана: нет перехода из состояния {self.current_state} по символу {sym}"

        stack_top = self.stack[0]
        self.stack = self.stack[1:]
        action = sym_tr.get(stack_top)
        if action is None:
            return False, f"\nЦепочка не распознана: нет перехода из состояния ({self.current_state}, {sym}, {stack_top})"

        self.current_state = action[0]
        self._string = self._string[1:]
        self.stack = action[1] + self.stack
        return True, f"({self.current_state}, {self._string}, {self.stack})"
