
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
        """
        A deterministic FA is complete if every state has exactly
        one outgoing transition for every symbol in the alphabet.
        Entry : Object of type Automaton
        Exit : Boolean
        """

        for state in range(self.nb_states):
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
# end class




# start functions

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


def standardize(automaton):
    #Check if it's already standard
    is_already_standard = True
    if len(automaton.initial_states) != 1: #case where there is multiple entry state
        is_already_standard = False
    else:
        # Check if any transition points to the single initial state
        initial_state = list(automaton.initial_states)[0]
        for source in automaton.transitions:
            for label in automaton.transitions[source]:
                if initial_state in automaton.transitions[source][label]:
                    is_already_standard = False
                    break

    if is_already_standard:
        return automaton  # No changes needed

    # Create a new unique initial state (e.g., 'S') that regroups every initial states
    new_start = "S"

    # Inherit transitions from all old initial states
    # If old initial states had: q0 --a--> q1, then new state gets: S --a--> q1
    new_transitions = {}
    for init_state in automaton.initial_states:
        if init_state in automaton.transitions:
            for label, targets in automaton.transitions[init_state].items():
                if label not in new_transitions:
                    new_transitions[label] = set()
                new_transitions[label].update(targets)

    # Add these transitions to the automaton for the new state
    automaton.transitions[new_start] = new_transitions

    # Handle terminal status
    # If any original initial state was terminal, the new start state is also terminal
    for init_state in automaton.initial_states:
        if init_state in automaton.terminal_states:
            automaton.terminal_states.add(new_start)
            break

    # Update initial states to ONLY be the new start state
    automaton.initial_states = {new_start}

    return automaton
    




#end functions