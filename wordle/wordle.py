import numpy as np
from termcolor import colored
import string
import os

PATH = os.getcwd()
SOLUTION_WORDS = np.genfromtxt(PATH+'/wordle/wordle_answers.txt', dtype='str')
GUESS_WORDS = np.genfromtxt(PATH+'/wordle/wordle_guesses.txt', dtype='str')

def get_solution_word():
    """Choose a target word."""
    solution = np.random.choice(SOLUTION_WORDS)
    return solution
    
def compare_words(solution, attempt):
    """Takes solution and attempt and return colour array"""
    solution = np.asarray(list(solution))
    attempt = np.asarray(list(attempt))
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
    
def word_attempt(solution, attempt, letters_left):
    """Prints attempt with appropriate colours"""
    colours = compare_words(solution, attempt)
    
    for i in range(len(attempt)):
        print(colored(attempt[i], colours[i]), end=" ")
    print("\n")
    
    if all(i == 'green' for i in colours):
        return True
    
    return False

def get_letters_left(letters_left, attempt):
    for letter in attempt:
        if letter in letters_left:
            letters_left = np.delete(letters_left, np.where(letters_left==letter))
    return letters_left
    
def play_wordle():
    solution = get_solution_word()
    
    attempts = 1
    letters_left = np.asarray(list(string.ascii_lowercase))
    
    while attempts < 7:
        attempt = input(f"{attempts}. > ")
        #Ensure it's in list of guess words
        if attempt not in GUESS_WORDS:
            print('Not a valid word. Guess again.\n')
            continue
        
        letters_left = get_letters_left(letters_left, attempt)
        is_winner = word_attempt(solution, attempt, letters_left)
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

