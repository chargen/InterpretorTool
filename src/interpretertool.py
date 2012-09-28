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

	SETACTION ::= [[ACTION] ACTION]

	LOOP ::= {ACTION}

	PATTERN ::= <<variable>>TEXT
				TEXT<<variable>>
				TEXT<<variable>>PATTERN
				PATTERN<<variable>>TEXT

	TEXT ::= ASCII TEXT
	
	Note that output stream redirections are required to be escaped:
	To redirect Input use: \\<
	To redirect Output use: \\>

"""


import argparse
import subprocess
import glob
import re
import sys

class Commands :
	SEQUENCE = 1
	ALTERNATIVE = 2
	
pipe_token = '\\\\|'
append_token = '\\\\>>'
write_token = '\\\\>'

def debug(msg):
	print('DEBUG: ' + msg)
	sys.stdout.flush()

def get_next_partial_command(tokens):
	primitive=[]
	
	for token in tokens :
		if(token == '}' or token == ';' or token == '||') :
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
	tokennames = re.findall("<<([a-zA-Z0-9_]+)>>", pathname_with_pattern)
	paths = []

	for tokenname in tokennames:
		tmp_list+=tokenname
		tmp_list+=" "

	if len(tmp_list) > 0 :
		tmp_list = tmp_list[:-1]

		try :
			matches_list = patterns[tmp_list]

			for match in matches_list :
				path = pathname_with_pattern
				pos = 0

				for tokenname in tokennames:					
					path = path.replace('<<' + tokenname + '>>', match[pos])

					pos+=1

				paths.append(path)
		except KeyError :
			pass

	# Insert Patterns
	return paths

def cross_product(*args):
	ans = [[]]
	for arg in args:
		ans = [x+[y] for x in ans for y in arg]
	return ans
	
def generate_pathnames(command_list, patterns):
	debug ('generate_pathnames: ')
	pattern_list = []
	pathnames = []
	tmp_list = ""
	resolved_pathnames = list()
	
	# Get patterns from pathnames
	for parameter_with_pattern in command_list :
		paths = generate_pathname(parameter_with_pattern, patterns)
		
		tokennames = re.findall("<<([a-zA-Z0-9_]+)>>", parameter_with_pattern)
		
		if len(paths) > 0 :
			resolved_pathnames.append(paths)
		else :
			if len(tokennames) > 0 :
				debug('Could not find any matches for patterns. Stopping command execution.')
				return []
			else :
				resolved_pathnames.append([parameter_with_pattern])
	
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

	debug ("resolved: " + str(resolved_pathnames))

	return cross_product(*resolved_pathnames)
	

def generate_command_list(commands):
	command_list = []
	current_command = []
	file_token = False
	
	for command in commands :
		for parameter in command :
			if file_token == True :
				command_list.append(parameter)
				file_token = False
				continue
			
			if parameter == pipe_token or parameter == write_token or parameter == append_token :
				if current_command != [] :
					command_list.append(current_command)
				command_list.append(parameter)
				current_command = []
				
				if parameter == write_token or parameter == append_token :
					file_token = True				
			else :
				current_command.append(parameter)

		if current_command != [] :
			command_list.append(current_command)
		current_command = []
	
	return command_list

def do_primitive(tokens, patterns):
	debug ('do_primitive')
	primitive = get_next_partial_command(tokens)
	
	split = split_command(tokens)
	
	debug ('split_command: ' + str(split))
	debug ('')
	
	generated_pathnames = generate_pathnames(get_next_partial_command(split),patterns)
	
	debug ('generated_pathnames: ' + str(generated_pathnames))
	debug ('')
	
	generated_commands = generate_command_list(generated_pathnames)
	
	debug ('generated_commands: ' + str(generated_commands))
	debug ('')
	
	''' This needs to be set to return if a pattern could derive any files '''
	pattern_matches = False

	returncode = None
	
	commands_length = len(generated_commands)
	pos = 0
	process_input = None
	process = None
	process_output = None
	file_list = list()
	chained = False
	next_chained = False
	
	while pos < commands_length :
	
		command = generated_commands[pos]
		debug (str(command))
		debug (str(process))
		debug (str(next_chained))

		if process != None and next_chained == True :
			debug ("process")
			process_input = process.stdout
			chained = True 
		
		if pos+1 < commands_length and generated_commands[pos+1] == pipe_token :
			process_output = subprocess.PIPE
			next_chained = True
			pos += 1
		elif pos+2 < commands_length and generated_commands[pos+1] == append_token :
			process_output = open(generated_commands[pos+2], 'a')
			file_list.append(process_output)
			next_chained = False
			pos += 2
		elif pos+2 < commands_length and generated_commands[pos+1] == write_token :
			process_output = open(generated_commands[pos+2], 'w')
			file_list.append(process_output)
			next_chained = False
			pos += 2
		else :
			process_output = None
			next_chained = False
	
		debug("command: " + str(command))
		debug("stdin: " + str(process_input))
		debug("stdout: " + str(process_output))
		process = subprocess.Popen(command, stdin=process_input, stdout=process_output)
		debug (str(process))
	
		if chained == True :
			debug ("asdf")
			process_input.close()
			process_input = None
			process.communicate()

			if next_chained == False :
				chained = False

		pos += 1


		#if process != None :
		process.wait()
		returncode = process.returncode
		if returncode > 0 :
			break
	
	for file in file_list :
		file.close()
	
	debug('do_primitive returning: ' + str((returncode, pattern_matches)))

	return returncode, pattern_matches

def add_pattern(tokens, patterns):
	""" Tokens bis zum Ende scannen und zu patterns Map hinzufuegen """
	""" Patterns map muss Patterns + Matches enthalten damit andere Methoden auf Ergebnis zugreifen koennen """
	""" The following should change file/to/<pattern>.extension into file/to/pattern/*.extension"""
	""" and it should concantenate the tokens. """

	result = False
	
	if patterns is None:
		patterns = {}

	filepatterns = []
	for token in tokens:
		if not token == ";":
			filepatterns.append(token)

	for filepattern in filepatterns:
		filepattern_with_glob = re.sub("<[a-zA-Z0-9_]+>", "*", filepattern)
		split_tokens = filepattern_with_glob.split("*")
		#print split_tokens

		#Files will contain a posibly empty list of filenames
		files = glob.glob(filepattern_with_glob)

		tokennames = re.findall("<([a-zA-Z0-9_]+)>", filepattern)
		composite_tokenname = " ".join(tokennames)

		patterns[composite_tokenname] = []

		for file in files:
			variablenames = {}
			result = file

			for token in split_tokens:
				# check if token is whitespace first!
				if token != '' :
					result = result.replace(token, '\t')
			#result list contains the string for the <...> patterns

			result_list = result.split('\t')
			pattern_list = []
			for result_item in result_list:
				if not result_item == '':
					pattern_list.append(result_item)

			debug('result_list: ' + str(result_list))
			patterns[composite_tokenname].append(pattern_list)

			if len(pattern_list) > 0 :
				result = True

	debug('add_pattern returning: ' + str(result))
	return result

def get_min_token_pos(string):
	'''tokens = [' ', '\t', '\n', '<<', '[', '{', ';', '|', '<', '>>', '}', ']', '>']'''
	tokens = [' ', '\t', '\n', '||' , '[', '{', ';', pipe_token, append_token, write_token, '}', ']']
	
	pos = -1
	final = ' '
	
	for token in tokens :
		tmppos = string.find(token)
		
		if (tmppos < pos or pos == -1) and tmppos > -1:
			pos = tmppos
			final = str(token)
	
	return pos, len(final)

def parse_tokens(string):
	debug ("FUNCTION: parse_tokens")
	tuple = get_min_token_pos(string)
	pos = tuple[0]
	length = tuple[1]
	tokens = []
	
	while pos > -1 :
		if pos > -1 :
			if pos > 0 and len(string[:pos].strip()) != 0:
				tokens.append(string[:pos].strip())
				
			string = string[pos:]
				
			pos = length
				
			token = string[:pos]

			if(len(token.strip()) != 0) :
				tokens.append(token.strip())
				
			string = string[pos:]
		
		tuple = get_min_token_pos(string)
		pos = tuple[0]
		length = tuple[1]
		
	#''' End '''
	token = string[:]
	
	if(len(token.strip()) != 0) :
				tokens.append(token.strip())

	debug ("Current list of tokens:" + str(tokens))

	return tokens

def parse_until_end_of(tokens, sign_open, sign_close):
	token_list = list()
	count = 1
	
	for token in tokens[1:] :
		if token == sign_open :
			count +=1
			
		if token == sign_close :
			count -=1
			
		if count == 0 :
			break
			
		token_list.append(token)
	
	return token_list

def parse_after(tokens, sign_open, sign_close):
	token_list = list()
	count = 1
	
	for token in tokens[1:] :
		if token == sign_open :
			count +=1

		if count == 0 :
			token_list.append(token)
			
		if token == sign_close :
			count -=1
	
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
	return parse_after(tokens, '[',']')

def parse_pattern(tokens):
	return parse_until_end_of(tokens, '[',']')

def parse_after_loop(tokens):
	return parse_after(tokens, '{','}')

def parse_loop(tokens):
	return parse_until_end_of(tokens, '{','}')

def parse_after_command(tokens):
	rest=[]
	found_char = False
	
	for token in tokens :
		if(token == '}' or token == ';' or token == '||') :
			found_char = True
		
		if found_char == True :
			rest.append(token)
		
	return rest

def do_pattern(tokens, patterns):

	pattern = parse_pattern(tokens)

	debug("pattern: " + str(pattern))
	
	pattern_matches = add_pattern(pattern, patterns)
	
	body = parse_after_pattern(tokens)
	
	result = do_actions(body, patterns)

	if result[1] == True or pattern_matches == True :
		pattern_matches = True

	return result[0], pattern_matches

def do_loop(tokens, patterns):
	run = True
	
	while run :
		debug("run loop")
		pattern_matches = do_actions(tokens, patterns)
		

		debug("pattern_matches: " + str(pattern_matches))
		if pattern_matches[1] == False :
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
	
	pos = 0
	length = len(current_tokens)
	
	while pos < length :
		debug ('FUNCTION: do_action')
		debug ('pos: ' + str(pos))
		debug ('length: ' + str(length))
		debug ('tokens: ' + str(current_tokens))
	
		token = current_tokens[pos]
		
		if token == '{' :
			debug("Encountered loop: ")
			loop = parse_loop(current_tokens)
			result = do_loop(loop, patterns)
			
			if result[1] == True :
				pattern_matches = True

			last_return_value = result[0]
				
			current_tokens = parse_after_loop(current_tokens)
		elif token == '[' :
			debug("Encountered pattern: ")
			pattern = parse_pattern(current_tokens)
			
			result = do_pattern(pattern, dict(patterns))

			if result[1] == True :
				pattern_matches = True
				debug('pattern_Matches')
			
			last_return_value = result[0]

			current_tokens = parse_after_pattern(current_tokens)			
		elif token == ';' :
			debug("Encountered sequence: ")
			if last_return_value == 0 :
				debug("   Executing")
				executeNext = True
			else :
				debug("   Not executing")
				executeNext = False
				
			current_tokens = current_tokens[1:]
		elif token == '||' :
			debug("Encountered alternative: ")
			if last_return_value == 0 :
				debug("   Not executing")
				executeNext = False
			else :
				debug("   Executing")
				executeNext = True
				
			current_tokens = current_tokens[1:]
		elif token == '}' :
			break
		else :
			# default action
			debug("Encountered command: ")
			if executeNext == True :
				debug ('asdf')
				return_tuple = do_primitive(current_tokens, patterns)
				last_return_value = return_tuple[0]
			elif executeNext == False :
				executeNext = True
			
			current_tokens = parse_after_command(current_tokens)
				
		pos += 1
		
		if len(current_tokens) < length :
			debug("Length: " + str(length))
			debug("Current Tokenlength: " + str(len(current_tokens)))
			debug("Position: " + str(pos))
			pos-=(length-len(current_tokens))
			
			if pos < 0 :
				pos = 0
			
			length = len(current_tokens)
			
			debug('current_tokens: ' + str(current_tokens))
			debug('length: ' + str(length))
			debug('pos')
			
	return last_return_value, pattern_matches

""" if __name__ == "__main__": <- Auto generiert """

#"Platzhalter, experimentiell"
parser = argparse.ArgumentParser(description='Process and executes configuration files.')
parser.add_argument('files', metavar='filename', type=open, nargs='+', help='The filenames of the configuration files')
args = parser.parse_args()

for file in args.files:
	text = file.read()
	tokens = parse_tokens(text)
	#print('text: ' + text)
	#print('tokens: ' + str(tokens))
	#split_command = split_command(tokens)
	#print('split_command: ' + str(split_command))
	#patterns = dict()
	#patterns['asdf'] = ['asd', 'jklo', 'qwertz']
	#patterns['asdfg'] = ['yxcv', 'vbnm', 'fghj']
	#patterns['users asdf'] = [['phil', 'asd'], ['phil', 'jklo'], ['seb', 'jklo']]
	#patterns['users asdfg'] = [['phil', 'fghj'], ['phil', 'yxcv'], ['seb', 'fghj']]
	#do_primitive(tokens,patterns)
	#print('generate_pathnames: ' + str(generate_pathnames))
	
	patterns = dict()
	#patterns['asdf'] = ['asd', 'jklo', 'qwertz']
	#patterns['asdfg'] = ['yxcv', 'vbnm', 'fghj']
	#patterns['users asdf'] = [['phil', 'asd'], ['phil', 'jklo'], ['seb', 'jklo']]
	#patterns['users asdfg'] = [['phil', 'fghj'], ['phil', 'yxcv'], ['seb', 'fghj']]
	
	do_actions(tokens,patterns)
	
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
