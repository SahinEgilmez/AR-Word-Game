#!/usr/bin/env python
# coding: utf8
'''
    Author: Şahin Eğilmez <segilmez@outlook.com>
'''

from Library import *  # Import constants, helper functions and using libraries


class Letter:  # Represent to each letter of alphabet. Each letter is represented by a png file. Png files kept assets folder.
    id = -1
    x = 0
    val = 0
    char = ''
    img = ""

    def __init__(self, value, character):
        self.val = value
        self.char = character
        self.img = "./assets/" + str(value) + ".png"


class Question:  # Represent to each question and answer. It contains a letters array and use it.
    question = ""
    answer = []
    trueOrder = []
    letters = [Letter(1, 'a'), Letter(2, 'b'), Letter(3, 'c'), Letter(4, 'ç'), Letter(5, 'd'), Letter(6, 'e'), Letter(7, 'f'), Letter(8, 'g'), Letter(9, 'ğ'), Letter(10, 'h'),
               Letter(11, 'ı'), Letter(12, 'i'), Letter(13, 'j'), Letter(14, 'k'), Letter(15, 'l'), Letter(16, 'm'), Letter(17, 'n'), Letter(18, 'o'), Letter(19, 'ö'), Letter(20, 'p'),
               Letter(21, 'r'), Letter(22, 's'), Letter(23, 'ş'), Letter(24, 't'), Letter(25, 'u'), Letter(26, 'ü'), Letter(27, 'v'), Letter(28, 'y'), Letter(29, 'z')]

    def __init__(self, question, word):
        self.question = question
        self.answer = self.getLetters(word)

    def getLetters(self, word):  # Convert word by string format to program's Letter format.
        lst = []
        a = 0
        for i in range(0, len(word)):
            c = word[i]
            for let in self.letters:
                if(let.char == c):
                    newlet = copy.copy(let)
                    a += 1
                    newlet.id = a
                    lst.append(newlet)
                    break
        self.trueOrder = lst.copy()
        # shuffle(lst)
        return lst


class Alphabet:  # Represent all Turkish Alphabet. Get questions by player number of team.
    QUESTION_NUMBER = -1
    questions = []

    def __init__(self, player_number):
        if player_number is 3:
            QUESTIONS_FILE = "./assets/word3.txt"
        if player_number is 4:
            QUESTIONS_FILE = "./assets/word4.txt"
        if player_number is 5:
            QUESTIONS_FILE = "./assets/word5.txt"
        self.questions = []
        with open(QUESTIONS_FILE, encoding="utf8") as f:
            content = f.readlines()
            for line in content[0:300]:
                lst = line.split('**')
                self.questions.append(Question(lst[1], lst[0]))
        shuffle(self.questions)

    def getQuestion(self):  # get Question object
        self.QUESTION_NUMBER += 1
        a = self.questions[self.QUESTION_NUMBER].answer
        return self.questions[self.QUESTION_NUMBER]
