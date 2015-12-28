#!/usr/bin/python
# -*- coding: utf-8 -*-


# run it like:
# for i in {1..200}; do python xkcd-password.py -wgerman_sh.txt; done > sh_passwords.txt

# based on work of
# https://github.com/redacted/XKCD-password-generator

import sqlite3
import re #regex
# import os
import datetime
import codecs
import random

def generateWordlist(wordfile=None):

    words = []
    wFile = open(wordfile)

    for line in wFile:
        words.append(line.strip().decode('utf8'))
    wFile.close()

    return words


def importWordlist(connection = None, wordfile=None, comment=''):
	words = []
	words = generateWordlist(wordfile)
	insert = []

	for i in range(len(words)):
		insert.append((words[i], i+1, comment, 0));

	# Insert the data
	connection.executemany('''INSERT INTO words ('word', 'rank', 'source', 'status') VALUES (?,?,?,?)''', insert)



def excludeByRegEx(connection = None, regEx='',status=-1):
	connection.execute('''SELECT id, word FROM words where status = 0 and source = 'Top 10000 DE Uni Leipzig';''')
	currentWords = connection.fetchall()
	killID = []

	regexp = re.compile(regEx)
	for i in range(len(currentWords)):

	    if regexp.match(currentWords[i][1]) is not None:
	        killID.append((str(currentWords[i][0]),));

	c.executemany('Update words set status = '+str(status)+' where ID =?;', killID)



def printCount (connection = None):
	connection.execute('''SELECT COUNT(*) from words where status = 0 and source = 'Top 10000 DE Uni Leipzig';''')
	result=connection.fetchone()
	print ("Current Wordlist: " + str(result[0]))



#timestamp of now  (used to set in filename)
now = datetime.datetime.now()
nowStr = now.strftime("%Y%m%d-%H%M")




# why we kill these words:
# Status    Reason
#      1    Word is too common (rank 1-1000)
#      2    Word is too short (min 3 chars)
#      3    Word has spaces in it like 'in der Regel'
#      4    Words with umlauds ÄÖÜäöüß
#      5    Belongs to the top 10000 passwords
#      6    Belongs to the top 10000 in english
#      7    Words with special-characters [^a-zA-Z]
#      8    Words with more than one capital in a row [A-Z]{2,}


conn = sqlite3.connect(nowStr + '_wordlist.sqlite3')


c = conn.cursor()

# Create table for the words 
c.execute('''CREATE TABLE words (id INTEGER PRIMARY KEY, word TEXT, rank NUMERIC, source TEXT, status NUMERIC);''')


# import top 10k german words
# http://wortschatz.uni-leipzig.de/html/wliste.html
importWordlist(c, './lib/top10000de.txt', 'Top 10000 DE Uni Leipzig')

# import top 10k passwords 
# 10k most common.txt
# http://xato.net/passwords/more-top-worst-passwords/
importWordlist(c, './lib/10k most common.txt', 'Top 10000 common passwords')

# import top 10k english words
# http://wortschatz.uni-leipzig.de/html/wliste.html
importWordlist(c, './lib/top10000en.txt', 'Top 10000 EN Uni Leipzig')


printCount(c)


print ('kill to common words')
c.execute('''Update words set status = 1 where status = 0 and rank <= 1000 and source = 'Top 10000 DE Uni Leipzig';''')
printCount(c)

print('kill too short words')
c.execute('''Update words set status = 2 where status = 0 and length(word) < 3 and source = 'Top 10000 DE Uni Leipzig';''')
printCount(c)

print('kill spaced words')
c.execute('''Update words set status = 3 where status = 0 and word like '% %' and source = 'Top 10000 DE Uni Leipzig';''')
printCount(c)

print('kill words with umlauds')
c.execute('''Update words set status = 4 where status = 0 and lower(word) like '%ä%' and source = 'Top 10000 DE Uni Leipzig';''')
c.execute('''Update words set status = 4 where status = 0 and lower(word) like '%ö%' and source = 'Top 10000 DE Uni Leipzig';''')
c.execute('''Update words set status = 4 where status = 0 and lower(word) like '%ü%' and source = 'Top 10000 DE Uni Leipzig';''')
c.execute('''Update words set status = 4 where status = 0 and lower(word) like '%ß%' and source = 'Top 10000 DE Uni Leipzig';''')
printCount(c)

print('kill words with [^a-zA-Z]')
excludeByRegEx(c, ".*[^a-zA-Z].*",status=7)
printCount(c)

print('kill CAPITAL Words')
excludeByRegEx(c, ".*[A-Z]{2,}.*",status=8)
printCount(c)

print('kill most common passwords')
c.execute('''Update words set status = 5 where status = 0 and word in (SELECT word FROM words WHERE source = 'Top 10000 common passwords') and source = 'Top 10000 DE Uni Leipzig';''')
printCount(c)

print('kill top 10k in english')
c.execute('''Update words set status = 6 where status = 0 and word in (SELECT word FROM words WHERE source = 'Top 10000 EN Uni Leipzig') and source = 'Top 10000 DE Uni Leipzig';''')
printCount(c)


c.execute('''SELECT word FROM words where status = 0 and source = 'Top 10000 DE Uni Leipzig';''')
finalData = c.fetchall()

wordlist = []

f = codecs.open(nowStr+'_wordlist.txt', "w", "utf-8")
for line in finalData:
	f.write('%s\n' % line[0])
	wordlist.append(line[0])


f2 = codecs.open(nowStr+'_passwords.txt', "w", "utf-8")

for x in range(0, 1000):
	f2.write('%s\n' % "_".join(random.SystemRandom().sample(wordlist, 4)) )


# Save (commit) the changes
conn.commit()

# We can also close the cursor if we are done with it
c.close()