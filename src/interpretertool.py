#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os

def construct_primitive(tokens):
	primitive=[]
	
	for token in tokens :
		if(token == '}' or token == ';' or token == '<or>') :
			break
			
		primitive.append(token)
		
	return primitive

def concat_path(tmp_command, pos):
	if len(tmp_command) > pos and pos-1 >= 0 :
		if tmp_command[pos-1].endswith('/') :
			tmp_command[pos-1] = tmp_command[pos-1] + tmp_command[pos]
			del(tmp_command[pos])
		
def concat_ext(tmp_command, pos):
	if len(tmp_command) > pos+1 and pos >= 0 :
		if tmp_command[pos+1].startswith('.') :
			tmp_command[pos] = tmp_command[pos] + tmp_command[pos+1]
			del(tmp_command[pos+1])
	

def generate_single_commands(original_command, patterns):
	pattern = False
	commands = [list(original_command)]
	tmp_commands = []
	entry = []
	run = True
	
	while run :
		has_matched = False
		for command in commands :
			pos = 0
			tmp_command = list(command)
			tmp_commands.append(tmp_command)
			
			for token in command :
				
				if token == '>>':
					for entry in tmp_commands :
						del(entry[pos])
						concat_ext(entry, pos-1)
						concat_path(entry, pos-1)
					
					pos = pos-3
					
					pattern = False
				
				if pattern == True :
					matches = patterns[token]
					
					new_tmp_commands = []
					
					for entry in tmp_commands :
						for match in matches :
							new_entry = list(entry)
							new_entry[pos] = match
						
							new_tmp_commands.append(new_entry)
							
					tmp_commands = new_tmp_commands
						
					
					has_matched = True
				
				if token == '<<':
					for entry in tmp_commands :
						del(entry[pos])
					
					pos=pos-1
					pattern = True
				
				pos=pos+1
		
		if has_matched == False :
			run = False
		else :	
			commands = list(tmp_commands)
			tmp_commands = list()
	
	return commands

def do_primitive(tokens, patterns):
	primitive = construct_primitive(tokens)
	
	commands = generate_single_commands(primitive, patterns)
	returncode = 0
	
	for command in commands :
		returncode = subprocess.call(command)
		
		if returncode > 0 :
			break
	
	return returncode

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
	tokens = ['<<', '[', '{', ';', '<', '>>', '}', ']', ';', '>']
	
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
	doActions(tokens, patterns)
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
	lastReturn = None
	
	for token in tokens:
		try:
			{ '{': doLoop(tokens, patterns),
			  '[': addPattern(tokens, patterns),
			  ';': doSequence(tokens, patterns, lastReturn),
			  '<or>' : doAlternative(tokens, patterns, lastReturn),
			  '}': 0}[value]()
		except KeyError:
			# default action
			returnValue = do_primitive(tokens, patterns)
			
	return

""" if __name__ == "__main__": <- Auto generiert """

"Platzhalter, experimentiell"
'''parser = argparse.ArgumentParser(description='Process and executes configuration files.')
parser.add_argument('files', metavar='filename', type=open, nargs='+', help='The filenames of the configuration files')
args = parser.parse_args()

for file in args.files:
	text = file.read()
	tokens = parseTokens(text)
	doActions(tokens,[])'''
	
test1 = ['ls', '-l', '/directory/', '<<', 'asdf', '>>', '.txt', '/directory/', '<<', 'asdfg', '>>', '.pdf']
testpattern1 = dict()
testpattern1['asdf'] = ['asd', 'jklo', 'qwertz']
testpattern1['asdfg'] = ['yxcv', 'vbnm', 'fghj']

for command in generate_single_commands(test1, testpattern1) :
	print (command)

'''print(test1)
concat_path(test1,3)
print(test1)
concat_ext(test1,2)
print(test1)'''

''' filename = "asdf"
fileString = readFile(filename)
tokens = getTokensFromString(fileString)
doActions(tokens, [], 0)
'''
