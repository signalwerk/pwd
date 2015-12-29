#!/usr/bin/python
# -*- coding: utf-8 -*-

import re  # regex
from libleipzig import Baseform
import json


def getWordList(wordfile=None):

    words = []
    wFile = open(wordfile)

    for line in wFile:
        words.append(line.strip().decode('utf8'))
    wFile.close()

    return words


def removeByWordList(full=None, wordfile=None):
    fWords = getWordList(wordfile)
    return filter(lambda x: x not in set(fWords), full)


def excludeByRegEx(full=None, regEx=''):
    regexp = re.compile(regEx)
    return filter(lambda i: not regexp.search(i), full)


def getBaseformOfList(full=None):

    baseformWords = []

    for word in full:
        base = Baseform(word)
        if base and base[0].Grundform and base[0].Wortart == 'N':
            baseformWords.append(base[0].Grundform)

    return baseformWords


finalWord = []

# we take the german wordlist
finalWord.extend(getWordList('./wordlists/top10000de.txt'))

# we don't wanna have the most common words
del finalWord[0:999]

# kill words with special characters
finalWord = excludeByRegEx(finalWord, ".*[^a-zA-Z].*")

# kill words with  y/z because some keyboard-layouts
# have them on different locations
finalWord = excludeByRegEx(finalWord, "[zy]")

# kill words with only 4 letters and less
finalWord = excludeByRegEx(finalWord, "^.{0,4}$")

# kill uncapitalized words
finalWord = excludeByRegEx(finalWord, "^[a-z].*$")

# kill words with more than one capital (nouns in german)
finalWord = excludeByRegEx(finalWord, ".*[A-Z]{2,}.*")

# kill most common passwords
finalWord = removeByWordList(finalWord, './wordlists/10kMostCommon.txt')

# kill english words
finalWord = removeByWordList(finalWord, './wordlists/top10000en.txt')

# kill all words to baseform and kill all other words than nouns
finalWord = getBaseformOfList(finalWord)

# kill first names
finalWord = removeByWordList(finalWord, './wordlists/firstname_de.txt')

# kill dupplicates in list
finalWord = list(set(finalWord))

print('Number of nouns in file: ' + str(len(finalWord)))

with open('./output/xkcd_de.json', 'w') as outfile:
    json.dump({'words': finalWord}, outfile, indent=4)

# print(finalWord)
