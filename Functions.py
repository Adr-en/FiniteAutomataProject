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
        if any(key[1] == 'e' for key in self.transitions.keys()):
            print("Not deterministic: contains epsilon transitions.")
            return False

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
        all_states = set()
        for state_label, _ in self.transitions.keys():
            all_states.add(state_label)

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

    def complete(self):
        if self.is_complete():
            return self

        new_transitions = self.transitions.copy()
        sink_state = "P"
        sink_needed = False

        all_states = set([k[0] for k in self.transitions.keys()] + self.initial_states + self.terminal_states)
        for state in all_states:
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


    def determinize_and_complete(self):
        """ The goal is to create a deterministic and complete version of a given automaton.
        For this we first check if it is deterministic.
        After this we create the initial state.
        Then we create all new states and transitions necessary for it to be deterinistic.
        We complete it and specify which states are terminal states.
        And finally we create the new Automaton and return it.

        Entry : Automaton
        Exit : Automaton"""

        if self.is_deterministic():
            return self

        # Creation of the new initial state
        initial_labels = self.epsilon_check(self.initial_states)
        initial_labels.sort()           #to prevent 1-3 != 3-1

        start_label = ""
        for i in range(len(initial_labels)):
            start_label += str(initial_labels[i])
            if i < len(initial_labels) - 1:
                start_label += "-"

        # Structure of the new automaton
        new_states_list = [start_label]  # each time we see a new state we put it in this list
        new_states_composition = {start_label: initial_labels} # aggregation of labels to form a unique state : list of the corresponding labels constituing the new state
        new_transitions = {}
        new_terminals = []

        # Main loop to create the transitions
        idx = 0
        while idx < len(new_states_list):
            current_label = new_states_list[idx]
            current_composition = new_states_composition[current_label]
            idx += 1

            for symbol in self.alphabet:
                targets_found = []      #reinitialise the list

                # For each original state we search for their targets and we deduce the new target for the new state
                for state in current_composition:
                    if (state, symbol) in self.transitions:
                        potential_targets = self.transitions[(state, symbol)]

                        for t in potential_targets:
                            for closure_state in self.epsilon_check(t):
                                if closure_state not in targets_found:
                                    targets_found.append(closure_state)

                # Sorting of the new target
                targets_found.sort()

                # Completing the table with the bin state P
                if len(targets_found) == 0:
                    target_label = "P"

                #Creating the new state used as target
                else:
                    target_label = ""
                    for i in range(len(targets_found)):
                        target_label += str(targets_found[i])
                        if i < len(targets_found) - 1:
                            target_label += "-"

                # Saving the new transition
                new_transitions[(current_label, symbol)] = [target_label]

                # If it's a new state we add it in the new state list
                if target_label not in new_states_list:
                    new_states_list.append(target_label)
                    new_states_composition[target_label] = targets_found

        # Identification of a new state
        for label in new_states_list:
            composition = new_states_composition[label]
            is_terminal = False
            for s in composition:
                if s in self.terminal_states:
                    is_terminal = True
                    break
            if is_terminal:
                new_terminals.append(label)

        # Creation of the new automaton
        new_automaton = Automaton(
            len([s for s in self.alphabet if s != 'e']),
            len(new_states_list),
            [start_label],
            new_terminals,
            new_transitions
        )

        return new_automaton


    def display_complete_deterministic_automaton(self):
            display_Automatoon(self)

    def display_minimal_automaton(self):
            display_Automatoon(self)

            if hasattr(self, 'mapping'):
                print("\n")
                print(f"{'Minimal state':<15} | {'Original DFA states'}")
                for i, original_group in enumerate(self.mapping):
                    composition = ", ".join(map(str, original_group))
                    print(f"{i:<15} | {composition}")
                print("=" * 50 + "\n")

    def epsilon_check(self, states):
        """
        Calcule la fermeture-epsilon d'un ensemble d'états.
        'states' peut être un entier unique ou une liste/set d'états.
        """
        if isinstance(states, (int, str)):
            states = [states]

        closure = set(states)
        stack = list(states)

        while stack:
            current = stack.pop()
            # We verify e transistions for this state
            # We use get to bypass errors if no transistions e exist
            for target in self.transitions.get((current, 'e'), []):
                if target not in closure:
                    closure.add(target)
                    stack.append(target)

        return sorted(list(closure))




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

        src, tgt = int(src_str), int(tgt_str)

        if (src, sym) not in transitions:
            transitions[(src, sym)] = []
        transitions[(src, sym)].append(tgt)

    return Automaton(alphabet_size, nb_states, initial_states, terminal_states, transitions)


def standardize(automaton):
    #Check if it's already standard
    is_already_standard = True
    if len(automaton.initial_states) != 1: #case where there is multiple entry state
        is_already_standard = False
    else:
        # Check if any transition points to the single initial state
        initial_state = list(automaton.initial_states)[0]
        for (src, sym), targets in automaton.transitions.items():
            if initial_state in targets:
                is_already_standard = False
                break

    if is_already_standard:
        return automaton  # No changes needed

    # Create a new unique initial state (e.g., 'S') that regroups every initial states
    new_start = "S"

    # Inherit transitions from all old initial states
    # If old initial states had: q0 --a--> q1, then new state gets: S --a--> q1
    for init_state in automaton.initial_states:
        for sym in automaton.alphabet:
            if (init_state, sym) in automaton.transitions:
                # If the transition doesn't exist yet for S we createe the list
                if (new_start, sym) not in automaton.transitions:
                    automaton.transitions[(new_start, sym)] = []

                # We add the targets of the previous initial state to S
                for t in automaton.transitions[(init_state, sym)]:
                    if t not in automaton.transitions[(new_start, sym)]:
                        automaton.transitions[(new_start, sym)].append(t)

    # Handle terminal status
    # If any original initial state was terminal, the new start state is also terminal
    for init_state in automaton.initial_states:
        if init_state in automaton.terminal_states:
            if new_start not in automaton.terminal_states:
                automaton.terminal_states.append(new_start)
            break

    # Update initial states to ONLY be the new start state
    automaton.initial_states = [new_start]

    return automaton

def display_Automatoon(FA):
    used_symbols = sorted(list(set(k[1] for k in FA.transitions.keys())))
    col_width = 10  # We define a width of 10 to align properly the columns

    #We align with < to the left
    print(f"{'':<16}", end="")
    for i in used_symbols:
        print(f"{i:<{col_width}}", end="")
    print()

    all_states = sorted(list(set([k[0] for k in FA.transitions.keys()] + FA.initial_states + FA.terminal_states)))
    for i in all_states:
        prefix = ""
        if i in FA.initial_states: prefix += "->"
        if i in FA.terminal_states: prefix += "<-"


        print(f"{prefix:<8}{str(i):<8}", end="")

        for j in used_symbols:
            targets = FA.transitions.get((i, j), [])
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
    current_states = set(A.epsilon_check(A.initial_states))
    
    # Process the word character by character
    for char in word:
        next_states = set()
        for state in current_states:
            # Checks the tuple to find the next states
            if (state, char) in A.transitions:
                # Add all valid target states to our next step
                next_states.update(A.transitions[(state, char)])
        
        current_states = set(A.epsilon_check(list(next_states)))
        
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



def minimize(FA):
    alphabet = list(string.ascii_lowercase[:FA.alphabet_size])

    #We look in the transistion keys to find the states
    all_states = sorted(list(set([k[0] for k in FA.transitions.keys()] + FA.initial_states + FA.terminal_states)))

    final_states = set(FA.terminal_states)
    non_final_states = set(all_states) - final_states

    p = []
    if final_states: p.append(tuple(sorted(list(final_states))))
    if non_final_states: p.append(tuple(sorted(list(non_final_states))))

    def get_group_index(state, current_partition):
        for idx, group in enumerate(current_partition):
            if state in group:
                return idx
        return -1

    while True:
        new_p = []
        for group in p:
            if len(group) <= 1:
                new_p.append(group)
                continue

            signatures = {}
            for state in group:
                sig = []
                for sym in alphabet:
                    # We search the target : if it is a DFA, targets[0] exists
                    targets = FA.transitions.get((state, sym), [None])
                    target = targets[0] if targets else None
                    sig.append(get_group_index(target, p))

                sig = tuple(sig)
                if sig not in signatures: signatures[sig] = []
                signatures[sig].append(state)

            for sub_group in signatures.values():
                new_p.append(tuple(sorted(sub_group)))

        if len(new_p) == len(p): break
        p = new_p


    # We transform the groups in exploitable datas
    new_nb_states = len(p)
    new_initial_states = []
    new_terminal_states = []
    new_transitions = {}

    state_to_new_idx = {}
    for idx, group in enumerate(p):
        for old_state in group:
            state_to_new_idx[old_state] = idx

        if any(s in FA.initial_states for s in group):
            new_initial_states.append(idx)
        if any(s in FA.terminal_states for s in group):
            new_terminal_states.append(idx)

    for idx, group in enumerate(p):
        rep = group[0]
        for sym in alphabet:
            old_targets = FA.transitions.get((rep, sym), [])
            if old_targets:
                new_target = state_to_new_idx[old_targets[0]]
                new_transitions[(idx, sym)] = [new_target]

    new_auto = Automaton(FA.alphabet_size, new_nb_states, new_initial_states, new_terminal_states, new_transitions)
    new_auto.mapping = p
    return new_auto

#end functions