#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
	GRAMAR DEFINITIONS:

	ACTION ::= COMMAND
			   ALTERNATIVE
			   SEQUENCE
			   SETACTION
			   LOOP

	COMMAND ::= Unix Command
				Unix Command with PATTERN

	ALTERNATIVE ::= ACTION <or> ALTERNATIVE
					ACTION <or> ACTION

	SEQUENCE ::= ACTION; SEQUENCE
				 ACTION; ACTION

	SETACTION ::= {[ACTION] ACTION}

	LOOP ::= {ACTION}

	PATTERN ::= <<variable>>TEXT
				TEXT<<variable>>
				TEXT<<variable>>PATTERN
				PATTERN<<variable>>TEXT

	TEXT ::= ASCII TEXT

"""


import argparse
import subprocess
import glob
import re

class Commands :
	SEQUENCE = 1
	ALTERNATIVE = 2

def construct_primitive(tokens):
	primitive=[]
	
	for token in tokens :
		if(token == '}' or token == ';' or token == '|') :
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
	

def split_command(original_command):
	result = []
	without_spaces = []
	
	escape_spaces = False
	
	for part in original_command :
		if escape_spaces == False and part.startswith('"') :
			without_spaces = []
			escape_spaces = True
			
		if escape_spaces == False :
			result.append(part)
			
		elif escape_spaces == True :
			without_spaces.append(part)
			
		if escape_spaces == True and part.endswith('"') :
			result.append(" ".join(without_spaces))
			escape_spaces = False
			
	return result

def generate_pathname(pathname_with_pattern, patterns):
	tmp_list = ""
	tokennames = re.findall("<<([a-z]+)>>", pathname_with_pattern)
	paths = []

	for tokenname in tokennames:
		tmp_list+=tokenname
		tmp_list+=" "

	if len(tmp_list) > 0 :
		tmp_list = tmp_list[:-1]

		matches_list = patterns[tmp_list]

		for match in matches_list :
			path = pathname_with_pattern
			pos = 0

			for tokenname in tokennames:					
				if len(tokennames) > 1 :
					path = path.replace('<<' + tokenname + '>>', match[pos])
				else :
					path = path.replace('<<' + tokenname + '>>', match)

				pos+=1
				
			paths.append(path)

	# Insert Patterns
	return paths

def cross_product(*args):
    ans = [[]]
    for arg in args:
        ans = [x+[y] for x in ans for y in arg]
    return ans
	
def generate_pathnames(command_list, patterns):
	print('generate_pathnames: ')
	pattern_list = []
	pathnames = []
	tmp_list = ""
	resolved_pathnames = list()
	
	# Get patterns from pathnames
	for parameter_with_pattern in command_list :
		paths = generate_pathname(parameter_with_pattern, patterns)
		print(paths)
		
		if len(paths) > 0 :
			resolved_pathnames.append(paths)
		else :
			resolved_pathnames.append([parameter_with_pattern])
	
	print(resolved_pathnames)
	print('cross_product')
	
	print(cross_product(*resolved_pathnames))
	
	'''for file in files:
		variablenames = {}
		result = file
		for token in split_tokens:
			result = result.replace(token, '\t')
		result_list = result.split('\t')
		pattern_list = []
		for result_item in result_list:
			if not result_item == '':
				pattern_list.append(result_item)

		for result_item, key in zip(pattern_list, tokennames):
				patterns[key].append(result_item)'''

	return ''
	

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
	print('do_primitive')
	primitive = construct_primitive(tokens)
	''' This needs to be set if a pattern could derive any files '''
	pattern_matches = False
	
	commands = generate_single_commands(primitive, patterns)
	returncode = 0
	
	for command in commands :
		print(command)
		returncode = subprocess.call(command)
		
		if returncode > 0 :
			break
	
	return returncode, pattern_matches

def add_pattern(tokens, patterns):
	""" Tokens bis zum Ende scannen und zu patterns Map hinzufuegen """
	""" Patterns map muss Patterns + Matches enthalten damit andere Methoden auf Ergebnis zugreifen koennen """
	""" The following should change file/to/<pattern>.extension into file/to/pattern/*.extension"""
	""" and it should concantenate the tokens. """
	
	if patterns is None:
		patterns = {}
	
	filepattern = "".join(tokens)
	filepattern_with_glob = re.sub("<[a-z]+>", "*", filepattern)
	split_tokens = filepattern_with_glob.split("*")
	print(split_tokens)

	#Files will contain a posibly empty list of filenames
	files = glob.glob(filepattern_with_glob)
	
	tokennames = re.findall("<([a-z]+)>", filepattern)

	for tokenname in tokennames:
		patterns[tokenname] = []
	
	for file in files:
		variablenames = {}
		result = file
		for token in split_tokens:
			result = result.replace(token, '\t')
		result_list = result.split('\t')
		pattern_list = []
		for result_item in result_list:
			if not result_item == '':
				pattern_list.append(result_item)

		for result_item, key in zip(pattern_list, tokennames):
				patterns[key].append(result_item)

	return ''

def get_min_token_pos(string):
	'''tokens = [' ', '\t', '\n', '<<', '[', '{', ';', '|', '<', '>>', '}', ']', '>']'''
	tokens = [' ', '\t', '\n', '[', '{', ';', '|', '}', ']']
	
	pos = -1
	
	for token in tokens :
		tmppos = string.find(token)
		
		if (tmppos < pos or pos == -1) and tmppos > -1:
			pos = tmppos
	
	return pos

def parse_tokens(string):
	pos = get_min_token_pos(string)
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
				tokens.append(token.strip())
				
			string = string[pos:]
		
		pos = get_min_token_pos(string)
		
	''' End '''
	token = string[:]
	
	if(len(token.strip()) != 0) :
				tokens.append(token.strip())
	
	for token in tokens :
		print("\""+ token + "\"")
	
	return tokens

def parse_until_end_of(tokens, sign):
	token_list = list()
	
	for token in tokens :
		if token == sign :
			break;
			
		token_list.append(token)
	
	return token_list

def parse_after(tokens, sign):
	token_list = list()
	sign_met = False
	
	for token in tokens :
		if sign_met :
			token_list.append(token)
		
		if token == sign :
			sign_met = True
	
	return token_list

''' def parse_until_last_occurence(tokens, token):
	return

def parse_until_eof_seq(tokens):
	parse_until_last_occurence(tokens,';')
	return

def parse_until_eof_alt(tokens):
	return
	'''

def parse_after_pattern(tokens):
	return parse_after(tokens,']')

def parse_pattern(tokens):
	return parse_until_end_of(tokens,']')

def parse_after_loop(tokens):
	return parse_after(tokens,'}')

def parse_loop(tokens):
	return parse_until_end_of(tokens,'}')

def do_loop(tokens, patterns):
	run = True
	
	while run :
		pattern_matches = do_actions(tokens, patterns)
		
		if pattern_matches == False :
			run = False
	
	return pattern_matches
	
	""" def doSequence(tokens, patterns, lastReturn): """
	""" Sequenz abarbeiten. For und Switch Statement aehnlich wie in doActions! """
	""" Falls lastReturn nicht gesetzt -> Semantischer Fehler in der
		Konfigurationsdatei, da vor einer Sequenz ein Befehl stehen muss """
	"""	return

def doAlternative(tokens, patterns, lastReturn):"""
	""" Alternativen abarbeiten. For und Switch Statement aehnlich wie in doActions! """
	""" Falls lastReturn nicht gesetzt -> Semantischer Fehler in der
		Konfigurationsdatei, da vor einer Alternative ein Befehl stehen muss """
	"""	return"""

def do_actions(tokens, patterns):
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
	last_return_value = None
	pattern_matches = False
	executeNext = True
	
	current_tokens = list(tokens)
	
	for token in tokens:
		if executeNext == False :
			executeNext = True
			continue
		
		if token == '{' :
			loop = parse_loop(current_tokens)
			pattern_matches = do_loop(loop, patterns)
			
			if return_tuple[1] == True :
				pattern_matches = True
		elif token == '[' :
			pattern = parse_pattern(current_tokens)
			add_pattern(pattern, patterns)
		elif token == ';' :
			if last_return_value == 0 :
				executeNext = True
			else :
				executeNext = False
		elif token == '|' :
			if last_return_value != 0 :
				executeNext = True
			else :
				executeNext = False
		elif token == '}' :
			break
		else :
			# default action
			if executeNext == True :
				print('asdf')
				return_tuple = do_primitive(current_tokens, patterns)
				last_return_value = return_tuple[0]
				
				if return_tuple[1] == True :
					pattern_matches = True
				
		del(current_tokens[0])
			
	return pattern_matches

""" if __name__ == "__main__": <- Auto generiert """

"Platzhalter, experimentiell"
parser = argparse.ArgumentParser(description='Process and executes configuration files.')
parser.add_argument('files', metavar='filename', type=open, nargs='+', help='The filenames of the configuration files')
args = parser.parse_args()

for file in args.files:
	text = file.read()
	tokens = parse_tokens(text)
	print('text: ' + text)
	print('tokens: ' + str(tokens))
	split_command = split_command(tokens)
	print('split_command: ' + str(split_command))
	patterns = dict()
	patterns['asdf'] = ['asd', 'jklo', 'qwertz']
	patterns['asdfg'] = ['yxcv', 'vbnm', 'fghj']
	patterns['users asdf'] = [['phil', 'asd'], ['phil', 'jklo'], ['seb', 'jklo']]
	patterns['users asdfg'] = [['phil', 'fghj'], ['phil', 'yxcv'], ['seb', 'fghj']]
	generate_pathnames = generate_pathnames(construct_primitive(split_command),patterns)
	print('generate_pathnames: ' + str(generate_pathnames))
	
	'''do_actions(tokens,[])'''
	
'''test1 = ['ls', '-l', '/directory/', '<<', 'asdf', '>>', '.txt', '/directory/', '<<', 'asdfg', '>>', '.pdf']
testpattern1 = dict()
testpattern1['asdf'] = ['asd', 'jklo', 'qwertz']
testpattern1['asdfg'] = ['yxcv', 'vbnm', 'fghj']

for command in generate_single_commands(test1, testpattern1) :
	print (command)'''
	
'''test2 = ['ls', '-l', '/directory/', '<<', 'asdf', '>>', '.txt', '/directory/', '<<', 'asdfg', '>>', '.pdf', ']', 'ls', '-l', '/directory/', '<<', 'asdf', '>>', '.txt', '/directory/', '<<', 'asdfg', '>>', '.pdf']
test3 = ['ls', '-l', '/directory/', '<<', 'asdf', '>>', '.txt', '/directory/', '<<', 'asdfg', '>>', '.pdf', '}', 'ls', '-l', '/directory/', '<<', 'asdf', '>>', '.txt', '/directory/', '<<', 'asdfg', '>>', '.pdf']

print(parse_after_pattern(test2))
print(parse_after_pattern(test3))'''

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
