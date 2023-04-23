import numpy as np
from termcolor import colored
import string
import os

PATH = os.getcwd()
SOLUTION_WORDS = np.genfromtxt(PATH+'/wordle/wordle_answers.txt', dtype='str')
GUESS_WORDS = np.genfromtxt(PATH+'/wordle/wordle_guesses.txt', dtype='str')

def get_solution_word():
    """Choose and return a target word as array of letters."""
    solution = np.random.choice(SOLUTION_WORDS)
    return np.asarray(list(solution))
    
def compare_words(solution, attempt):
    """
    Takes solution and attempt and return colour array indicating
       whether attempt letters are black, yellow or green
    """
    correct = solution==attempt
    colours = np.asarray(['black']*5, dtype = '<U6')

    #Turn correct ones green and nearly correct yellow
    for i in range(len(attempt)):
        if correct[i] == True:
            colours[i] = 'green'
    
    #This section ensure that if there's more than one of a letter
    #and one is in the right place and one isn't, the other is yellow.
    not_greens = solution[np.where(colours!='green')[0]]
    for i in range(len(attempt)):
        if correct[i] == False and attempt[i] in not_greens:
            colours[i] = 'yellow'

    return colours
    
def word_attempt(solution, attempt, yellows):
    """
    Determines whether a word attempt is a winner
    
    Inputs:  solution - i.e. the answer
             attempt  - the inputted attempted
             yellows  - dict having indices of previous yellows
                       for each letter which has been yellow

    Outputs: bool     - whether the attempt is a winner or not
             yellows  - updated yellows dict
             colours  - colour array for present attempt
    """
    colours = compare_words(solution, attempt)
    
    for i in range(len(attempt)):
        print(colored(attempt[i], colours[i]), end=" ")
    print("\n")
    
    if all(i == 'green' for i in colours):
        return True, None, None

    #Append indices of yellows in attempt to yellows dict
    yellow_locs = np.where(colours == 'yellow')[0]
    yellow_letters = attempt[yellow_locs]
    for i in range(len(yellow_letters)):
        if yellow_letters[i] not in yellows:
            yellows[yellow_letters[i]] = np.asarray([yellow_locs[i]])
        else:
            yellows[yellow_letters[i]] = np.unique(np.append(yellows[yellow_letters[i]], yellow_locs[i]))

    return False, yellows, colours

def is_valid_attempt(solution, attempt, yellows, colours, letters_left, hard_mode):
    """
    Establishes when an attempt is valid
    
    Inputs:  solution     - i.e. the answer
             attempt      - the inputted attempt
             yellows      - dict having indices of previous yellows
                           for each letter which has been yellow
             colours      - colour array for previous attempt
             letters_left - letters not yet guessed
             hard_mode    - whether it's being played in hard mode

    Outputs: bool         - whether the attempt is valid or not
    """
    #Must be in the guess word list
    if "".join(attempt) not in GUESS_WORDS:
        return False

    if hard_mode==False:
        return True

    #Hard mode - requires greens to be repeated
    if (attempt[np.where(colours=='green')[0]]==solution[np.where(colours=='green')[0]]).sum() != len(np.where(colours=='green')[0]):
       return False

    #Hard mode - requiring yellows to be guessed
    for letter in yellows:
        if letter not in attempt:
            return False
    
    #Hard mode - yellows requiring to be in different position
    for i in range(len(attempt)):
        if attempt[i] in yellows:
            if i in yellows[attempt[i]]:
                return False

    #Hard mode - requires that previously guessed wrong letters not guessed again
    colours = compare_words(solution, attempt)
    if len(np.setdiff1d(np.setdiff1d(attempt[np.where(colours=='black')[0]], solution), letters_left)) > 0:
        return False
    
    return True

def get_letters_left(letters_left, attempt):
    """Get list of letters not guessed"""
    for letter in attempt:
        if letter in letters_left:
            letters_left = np.delete(letters_left, np.where(letters_left==letter))
    return letters_left 
    
def play_wordle(hard_mode=False):
    """
    Play the wordle game.

    Inputs: hard_mode - set to True to play in hard mode.
    """
    solution = get_solution_word()
    
    print('WELCOME TO WORDLE. TYPE xxx TO REVEAL ANSWER')
    print('TYPE rrr TO REVEAL LETTER. TYPE ddd to rule out letter.\n')
    attempts = 1
    letters_left = np.asarray(list(string.ascii_lowercase))
    colours = np.asarray(['black']*5, dtype = '<U6')
    yellows = dict() #for remembering all the disallowed yellow places
    previous_attempt = np.asarray(list('-----'))
                                 
    while attempts < 7:
        attempt_word = input(f"{attempts}. > ")

        #Abort condition
        if attempt_word == 'xxx':
            attempts = 7
            break
        
        #Reveal letter condition
        if attempt_word == 'rrr':
            reveal_index = np.random.choice(np.where(colours=='black')[0])
            colours[reveal_index] = 'green'
            if np.count_nonzero(solution[np.where(colours!='green')[0]] == solution[reveal_index]) == 0 \
               and solution[reveal_index] in previous_attempt[np.where(colours=='yellow')[0]]:
                colours[np.where(previous_attempt==solution[reveal_index])[0]] = 'black'
            previous_attempt[reveal_index] = solution[reveal_index]
              
            for i in range(len(previous_attempt)):
                print(colored(previous_attempt[i], colours[i]), end=" ")
            print("\n")

            if np.all(colours=='green'):
                attempts = 7
                break
            
            continue
        
        #Delete letter left condition
        if attempt_word == 'ddd':
            remove_letter = np.random.choice(np.setdiff1d(letters_left, solution))
            letters_left = np.delete(letters_left, np.where(letters_left==remove_letter))
            print(f"Removed incorrect letter {remove_letter}.\n")
            print("REMAINING LETTERS: ", end="")  
            for i in range(len(letters_left)):
                print(letters_left[i], end=" ")
            print("\n")
            continue

        attempt = np.asarray(list(attempt_word))
        #Ensure it's in list of valid guess words
        if not is_valid_attempt(solution, attempt, yellows, colours, letters_left, hard_mode):
            print('Not a valid word. Guess again.\n')
            continue
        previous_attempt = attempt
        
        letters_left = get_letters_left(letters_left, attempt)
        is_winner, yellows, colours = word_attempt(solution, attempt, yellows)
        if is_winner:
            print("YOU HAVE WON!")
            break
        
        print("REMAINING LETTERS: ", end="")  
        for i in range(len(letters_left)):
            print(letters_left[i], end=" ")
        print("\n")
        
        attempts+=1
            
    if attempts == 7:
        print(f"The word was {''.join(solution)}")

