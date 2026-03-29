import string
#start class

class Automaton:
    def __init__(self, alphabet_size, nb_states, initial_states, terminal_states, transitions):
        self.alphabet_size = alphabet_size  # Number of symbols in the alphabet
        self.nb_states = nb_states  # Total number of states labeled 0 to n-1
        self.initial_states = initial_states  # List of initial state labels
        self.terminal_states = terminal_states  # List of terminal state labels
        # Transitions stored as a dictionary {(state, symbol): [list of target_states]}
        self.transitions = transitions
        self.alphabet = [chr(97 + i) for i in range(alphabet_size)]  # ['a', 'b'...]


    def is_deterministic(self):
        """
        An FA is deterministic if :
        - it has exactly one initial state ,
        - for every state there is at most one transition for any given symbol.
        Entry : Object of type Automaton
        Exit : Boolean
        """

        if len(self.initial_states) != 1:
            print("Not deterministic: multiple or zero initial states.")
            return False

        # Requirement: Check if any state-symbol pair leads to multiple targets
        for key, targets in self.transitions.items():
            if len(targets) > 1:
                print(f"Not deterministic: state {key[0]} has multiple transitions for '{key[1]}'.")
                return False

        print("The automaton is deterministic.")
        return True

    def is_complete(self):
        # On récupère la liste de tous les états réellement présents dans l'automate
        # (ceux qui ont des transitions sortantes ou qui sont définis à la création)
        all_states = set()
        for state_label, _ in self.transitions.keys():
            all_states.add(state_label)

        # On vérifie aussi les états initiaux et terminaux au cas où ils n'auraient pas de transitions
        all_states.update(self.initial_states)
        all_states.update(self.terminal_states)

        for state in all_states:
            for symbol in self.alphabet:
                if (state, symbol) not in self.transitions or not self.transitions[(state, symbol)]:
                    print(f"Not complete: state {state} lacks a transition for '{symbol}'.")
                    return False

        print("The automaton is complete.")
        return True

    def is_standard(self):
        """
        An FA is standard if :
        - it has exactly one initial state
        - and no transitions lead back into that initial state.
        Entry : Object of type Automaton
        Exit : Boolean
        """

        if len(self.initial_states) != 1:
            print("Not standard: must have exactly one initial state.")
            return False

        target_initial = self.initial_states[0]


        for targets in self.transitions.values():
            if target_initial in targets:
                print(f"Not standard: transition found leading back to initial state {target_initial}.")
                return False

        print("The automaton is standard.")
        return True


    def standardize(self):
        # Check if it's already standard
        is_already_standard = True
        if len(self.initial_states) != 1:  # case where there is multiple entry state
            is_already_standard = False
        else:
            # Check if any transition points to the single initial state
            initial_state = list(self.initial_states)[0]
            for source in self.transitions:
                for label in self.transitions[source]:
                    if initial_state in self.transitions[source][label]:
                        is_already_standard = False
                        break

        if is_already_standard:
            return self  # No changes needed

        # Create a new unique initial state (e.g., 'S') that regroups every initial states
        new_start = "S"

        # Inherit transitions from all old initial states
        # If old initial states had: q0 --a--> q1, then new state gets: S --a--> q1
        new_transitions = {}
        for init_state in self.initial_states:
            if init_state in self.transitions:
                for label, targets in self.transitions[init_state].items():
                    if label not in new_transitions:
                        new_transitions[label] = set()
                    new_transitions[label].update(targets)

        # Add these transitions to the automaton for the new state
        self.transitions[new_start] = new_transitions

        # Handle terminal status
        # If any original initial state was terminal, the new start state is also terminal
        for init_state in self.initial_states:
            if init_state in self.terminal_states:
                self.terminal_states.add(new_start)
                break

        # Update initial states to ONLY be the new start state
        self.initial_states = {new_start}

        return self


    def complete(self):
        if self.is_complete():
            return self

        new_transitions = self.transitions.copy()
        sink_state = "P"
        sink_needed = False

        for state in range(self.nb_states):
            for symbol in self.alphabet:
                if (state, symbol) not in new_transitions or not new_transitions[(state, symbol)]:
                    new_transitions[(state, symbol)] = [sink_state]
                    sink_needed = True

        if sink_needed:
            for symbol in self.alphabet:
                new_transitions[(sink_state, symbol)] = [sink_state]

            return Automaton(self.alphabet_size, self.nb_states + 1, self.initial_states, self.terminal_states,
                             new_transitions)
        return self


    def determinize(self):
        if self.is_deterministic():
            return self

        initial_labels = sorted(self.initial_states)
        start_label = "-".join(map(str, initial_labels)) if initial_labels else "P"

        new_states_list = [start_label]
        new_states_composition = {start_label: initial_labels}
        new_transitions = {}
        new_terminals = []

        idx = 0
        while idx < len(new_states_list):
            current_label = new_states_list[idx]
            current_composition = new_states_composition[current_label]
            idx += 1

            if any(s in self.terminal_states for s in current_composition):
                if current_label not in new_terminals:
                    new_terminals.append(current_label)

            for symbol in self.alphabet:
                targets_found = set()
                for state in current_composition:
                    if (state, symbol) in self.transitions:
                        targets_found.update(self.transitions[(state, symbol)])

                sorted_targets = sorted(list(targets_found))
                if not sorted_targets:
                    target_label = "P"
                else:
                    target_label = "-".join(map(str, sorted_targets))

                new_transitions[(current_label, symbol)] = [target_label]

                if target_label not in new_states_list:
                    new_states_list.append(target_label)
                    new_states_composition[target_label] = sorted_targets

        return Automaton(self.alphabet_size, len(new_states_list), [start_label], new_terminals, new_transitions)



    def determinize_and_complete(self):
        """
        Implementation according to the project PDF's pseudo-code logic.
        """
        if is_automaton(self):
            if self.is_deterministic():
                print("Automaton is already deterministic.")
                if self.is_complete():
                    print("Automaton is already complete.")
                    cdfa = self
                else:
                    print("Automaton is not complete. Completing...")
                    cdfa = self.complete()
            else:
                print("Automaton is not deterministic. Determinizing and completing...")
                # Note: determinize() handles the creation of the P state if targets are empty,
                # which technically completes it during the process.
                cdfa = self.determinize()
                if not cdfa.is_complete():
                    cdfa = cdfa.complete()

            return cdfa
        else:
            print("The object is not an automaton.")
            return None


    def display_complete_deterministic_automaton(self):
            """
            Displays the CDFA and explicitly shows the composition of the states
            in terms of the original automaton states.
            Entry : Automaton
            Exit : None
            """
            col_width = 15

            print("\n--- Complete Deterministic Automaton (CDFA) ---")

            # Header for symbols [cite: 32, 160]
            header = f"{'State (Composition)':<{col_width * 1.5}}"
            for sym in self.alphabet:
                header += f"{sym:<{col_width}}"
            print(header)
            print("-" * len(header))

            # We iterate through all states present in the transitions or labels
            all_states = sorted(
                list(set([k[0] for k in self.transitions.keys()] + self.initial_states + self.terminal_states)))

            for state in all_states:
                # Mark Initial (->) and Terminal (<-)
                prefix = ""
                if state in self.initial_states: prefix += "->"
                if state in self.terminal_states: prefix += "<-"

                state_display = f"{prefix}{state}"
                row = f"{state_display:<{col_width * 1.5}}"

                for sym in self.alphabet:
                    targets = self.transitions.get((state, sym), [])
                    cell = ", ".join(map(str, targets)) if targets else "--"
                    row += f"{cell:<{col_width}}"

                print(row)

            print("-" * len(header))
            print("Note: State names (e.g., '0-1') indicate the set of original states they represent.\n")










# end class




# start functions

def is_automaton(object):
    if type(object) == Automaton:
        return True
    return False


def read_automaton_from_file(filename, target_id):
    """
    Reads a FA from a text file and saves it in memory according to chosen data structures.
    The target_id should be a string like '05'.
    """

    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]


    # find the Automaton with the index
    start_index = -1
    for i, line in enumerate(lines):
        if line == f"#{target_id}":
            start_index = i + 1
            break

    if start_index == -1:
        return None


    alphabet_size = int(lines[start_index])  # 1. Number of symbols in the alphabet
    nb_states = int(lines[start_index + 1])  # 2. Number of states

    init_data = list(map(int, lines[start_index + 2].split())) # 3. Initial states: count followed by labels
    initial_states = init_data[1:]  # Skip the count
    final_data = list(map(int, lines[start_index + 3].split())) # 4. Final states: count followed by labels
    terminal_states = final_data[1:]  # Skip the count

    nb_transitions = int(lines[start_index + 4]) # 5. Number of transitions

    # 6. Transitions in form <source><symbol><target>
    transitions = {}
    for i in range(nb_transitions):
        line = lines[start_index + 5 + i]

        src_str = ""
        sym = ""
        tgt_str = ""
        found_sym = False

        for char in line:
            if char.isdigit():
                if not found_sym:
                    src_str += char  # Chiffres avant la lettre
                else:
                    tgt_str += char  # Chiffres après la lettre
            else:
                sym = char  # C'est notre 'a', 'b', etc.
                found_sym = True

        # Conversion en entiers et stockage
        src, tgt = int(src_str), int(tgt_str)

        if (src, sym) not in transitions:
            transitions[(src, sym)] = []
        transitions[(src, sym)].append(tgt)

    return Automaton(alphabet_size, nb_states, initial_states, terminal_states, transitions)



def display_Automatoon(FA):
    alphabet_liste = list(string.ascii_lowercase)
    col_width = 10  # We define a width of 10 to align properly the columns

    #We align with < to the left
    print(f"{'':<16}", end="")
    for i in range(FA.alphabet_size):
        print(f"{alphabet_liste[i]:<{col_width}}", end="")
    print()

    for i in range(FA.nb_states):
        prefix = ""
        if i in FA.initial_states: prefix += "->"
        if i in FA.terminal_states: prefix += "<-"


        print(f"{prefix:<8}", end="")
        print(f"{str(i):<8}", end="")

        for j in range(FA.alphabet_size):
            sym = alphabet_liste[j]
            targets = FA.transitions.get((i, sym), [])

            #We prepare the text of the cell
            cell = ", ".join(map(str, targets)) if targets else "--"

            # We print it
            print(f"{cell:<{col_width}}", end="")

        print()
    return


#part 6 : word recognition 
def read_word():
    #Asks user to enter a word and stores the string in memory
    word = input("Enter a word to test or 'end' to stop: ")
    return word

def recognize_word(word, A):
    #Verifies if the automaton A recognizes the input word.
    #Uses a tuple (state, symbol) defined in the Automaton class
   
    # Initialize the current states with the automaton's initial states
    current_states = set(A.initial_states)
    
    # Process the word character by character
    for char in word:
        next_states = set()
        for state in current_states:
            # Checks the tuple to find the next states
            if (state, char) in A.transitions:
                # Add all valid target states to our next step
                next_states.update(A.transitions[(state, char)])
        
        current_states = next_states
        
        # Optimization: If no states are active, the word cannot be recognized
        if not current_states:
            break

    # Determine if any of the active states are in the terminal_states list
    is_recognized = any(state in A.terminal_states for state in current_states)
    
    if is_recognized:
        print("Yes")
    else:
        print("No")

def word_recognition_loop(A):
    #creates a loop to enter multiple words and test them on the automaton A until the user types "end".

    word = read_word() 
    
    while word != "end": 
        recognize_word(word, A) 
        word = read_word()


#end functions







