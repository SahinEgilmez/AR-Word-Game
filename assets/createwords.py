#!/usr/bin/python
'''
    Author: Guido Diepen <gdiepen@deloitte.nl>
'''
from random import shuffle
import os
x = [[i] for i in range(10)]
shuffle(x)

NUMBER = 3
TEMP = "temp.txt"
FILE = "word3.TXT"


def createWords():
    with open("anlamlar.txt", encoding="utf8") as f:
        with open(TEMP, "w", encoding="utf8") as f1:
            for line in f:
                lst = line.split('**')
                if(len(list(lst[0])) == NUMBER and "yok" not in lst[1]):
                    f1.write(line)


def randomlyWords():
    with open(TEMP, encoding="utf8") as f:
        with open(FILE, "w", encoding="utf8") as f1:
            content = f.readlines()
            shuffle(content)
            f1.writelines(content)
    os.remove(TEMP)


if __name__ == '__main__':
    createWords()
    randomlyWords()
