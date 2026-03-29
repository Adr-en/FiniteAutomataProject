import Functions as F
from Functions import display_Automatoon


#test
def main():

    while True:
        choice = input("Which FA do you want to use? (or 'exit'): ")
        if choice.lower() == 'exit':
            break

        # Ensure ID format matches the file (e.g., '5' becomes '05')
        formatted_id = choice.zfill(2)
        fa = F.read_automaton_from_file("Automatas.txt", formatted_id)


        print(f"\n--- Analysis of FA #{formatted_id} ---")
        if fa:
            display_Automatoon(fa)
            display_Automatoon(F.minimize(fa.determinize_and_complete()))
            is_det = fa.is_deterministic()
            is_comp = fa.is_complete()
            is_std = fa.is_standard()

        else:
            print("Automaton not found.")


    return


main()