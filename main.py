import Functions as F
from Functions import display_Automatoon


def main():

    while True:
        choice = input("Which FA do you want to use? (or 'exit'): ")
        if choice.lower() == 'exit':
            break

        # Ensure ID format matches the file (e.g., '5' becomes '05')
        formatted_id = choice.zfill(2)
        fa = F.read_automaton_from_file("Automatas.txt", formatted_id)


        print(f"\n--- Analysis of FA #{formatted_id} ---\n")
        if fa:
            print("Displaying Automatoon :")
            display_Automatoon(fa)
            if F.is_automaton(fa):
                cdfa = fa.determinize_and_complete()

            else :
                if fa.is_deterministic():
                    if fa.is_complete():
                        cdfa = fa
                    else :
                        cdfa = fa.complete()
                else:
                    print("The automaton is complete.")
                    cdfa = fa.determinize_and_complete()

            print("Displaying determinized and complete automatoon :")
            cdfa.display_complete_deterministic_automaton()

            print("Displaying minimized automatoon :")
            mcdfa = F.minimize(cdfa)
            mcdfa.display_minimal_automaton()

            #print(f"Test : read word on the minimized automata")
            #F.word_recognition_loop(mcdfa)

            #print("That's all for this automaton\n")




        else:
            print("Automaton not found.")


    return


main()