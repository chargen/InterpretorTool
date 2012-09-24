#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os

def doPrimitive(tokens, patterns):
	""" tokens nach Kommandozeilenprogramm parsen und ausfuehren und returnValue der Methode zurueckliefern """
	""" Die Patterns und Matches in der patterns Map muessen beachtet werden! """
	return 0

def addPattern(tokens, patterns):
	""" Tokens bis zum Ende ']' scannen und zu patterns Map hinzufuegen """
	""" Patterns map muss Patterns + Matches enthalten damit andere Methoden auf Ergebnis zugreifen koennen """
	""" The following should change file/to/<pattern>.extension into file/to/pattern/*.extension"""
	""" and it should concantenate the tokens. """
	filepattern = ""
	for token in tokens:
		have_tag = false
		if token.equals("<"):
			have_tag = true
			continue
		elif not have_tag:
			filepattern += token
			continue

		# When we reach here, we are in a token
		patterns[token] = None #for now we add a token with empty value
		filepattern += "*"

	#when we are finished, we have a full (relative) pass with shell globs
	#next we need to go into the pathes until we reach a glob (*) and then
	#recursively go into subfolders and identify file that could match the
	#glob. And we need to build a list of matching globs.
	files = os.listdir("something")

	return ''

def getMinTokenPos(string):
	tokens = ['<<', '[', '{', '<', '>>', '}', ']', '>']
	
	pos = -1
	
	for token in tokens :
		tmppos = string.find(token)
		
		if (tmppos < pos or pos == -1) and tmppos > -1:
			pos = tmppos
	
	return pos

def parseTokens(string):
	""" Split string (whitespaces) """
	
	pos = getMinTokenPos(string)
	tokens = []
	
	while pos > -1 :
		if pos > -1 :
			if pos > 0 and len(string[:pos].strip()) != 0:
				tokens.append(string[:pos].strip())
				
			string = string[pos:]
				
			if(string.find('<<') == 0 or string.find('>>') == 0) :
				pos = 2
			else :
				pos = 1
				
			token = string[:pos]

			if(len(token.strip()) != 0) :
				tokens.append(token)
				
			string = string[pos:]
		
		pos = getMinTokenPos(string)
		
	
	for token in tokens :
		print("\""+ token + "\"")
	
	return tokens

def doLoop(tokens, patterns):
	""" Schleifenlogik """
	doActions(tokens, patterns, 0)
	""" Schleifenlogik """
	
def doSequence(tokens, patterns, lastReturn):
	""" Sequenz abarbeiten. For und Switch Statement aehnlich wie in doActions! """
	""" Falls lastReturn nicht gesetzt -> Semantischer Fehler in der
		Konfigurationsdatei, da vor einer Sequenz ein Befehl stehen muss """
	return

def doAlternative(tokens, patterns, lastReturn):
	""" Alternativen abarbeiten. For und Switch Statement aehnlich wie in doActions! """
	""" Falls lastReturn nicht gesetzt -> Semantischer Fehler in der
		Konfigurationsdatei, da vor einer Alternative ein Befehl stehen muss """
	return

def doActions(tokens, patterns):
	""" TODOS:
	 * umaendern in begins_with, da nicht unbedingt Whitespace zwischen tokens. getStringTokens notwendig?
	 * return statement ist in diesem Konstrukt nicht moeglich. muss anders geloest werden
	 * Moeglicher Konflikt <or> mit Patterns? Sollte bei korrekter Implementierung
	   von doPrimitive eigentlich nicht auftreten, da Patterns ansonsten nur in Befehlen vorkommen.
	 * Sequenz ';' und '<or>' muessten in diesem Konstrukt den Returnwert pruefen
	   und entscheiden ob naechstes Kommand ausgefuehrt oder uebersprungen wird!
	   Schwierig, da nicht ganz klar ist wie der Returnwert weiter gehandhabt
	   werden soll, z.B. command1;command2<or>command3. Muss noch besprochen werden.
		Moeglicherweise hilft hier folgender Aufrufcode, d.h. z.B.
			doActions('command1; command2<or> command3')
				doPrimitive('command1')
			doActions('; command2<or> command3')
				doSequence('command2<or> command3, returnVal')
					doPrimitive(command2)
			doActions('<or> command3')
				doAlternative('command3', returnVal)
					doPrimitive('command3')
				doAlternative('',returnVal)
			doActions('')
	"""
	lastReturn = null
	
	for token in tokens:
		try:
			{ '{': doLoop(tokens, patterns),
			  '[': addPattern(tokens, patterns),
			  ';': doSequence(tokens, patterns, lastReturn),
			  '<or>' : doAlternative(tokens, patterns, lastReturn),
			  '}': 0}[value]()
		except KeyError:
			# default action
			returnValue = doPrimitive(tokens, patterns)
			
	return

""" if __name__ == "__main__": <- Auto generiert """

"Platzhalter, experimentiell"
parser = argparse.ArgumentParser(description='Process and executes configuration files.')
parser.add_argument('files', metavar='filename', type=open, nargs='+', help='The filenames of the configuration files')
args = parser.parse_args()

for file in args.files:
	text = file.read()
	parseTokens(text)

''' filename = "asdf"
fileString = readFile(filename)
tokens = getTokensFromString(fileString)
doActions(tokens, [], 0)
'''
