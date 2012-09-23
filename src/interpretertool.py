from optparse import OptionParser

def doPrimitive(tokens, patterns):
	""" tokens nach Kommandozeilenprogramm parsen und ausf�hren und returnValue der Methode zur�ckliefern """
	""" Die Patterns und Matches in der patterns Map m�ssen beachtet werden! """
	return 0

def addPattern(tokens, patterns):
	""" Tokens bis zum Ende ']' scannen und zu patterns Map hinzuf�gen """
	""" Patterns map muss Patterns + Matches enthalten damit andere Methoden auf Ergebnis zugreifen k�nnen """
	return ""

def readFile(filename):
	fileString = ""	
	print "Reading File"
	return ""

def getStringTokens(string):
	""" Split string (whitespaces) """
	splitString = []
	
	return splitString

def doLoop(tokens, patterns):
	""" Schleifenlogik """
	doActions(tokens, patterns, 0)
	""" Schleifenlogik """
	
def doSequence(tokens, patterns, lastReturn):
	""" Sequenz abarbeiten. For und Switch Statement �hnlich wie in doActions! """
	""" Falls lastReturn nicht gesetzt -> Semantischer Fehler in der
	    Konfigurationsdatei, da vor einer Sequenz ein Befehl stehen muss """
	return

def doAlternative(tokens, patterns, lastReturn):
	""" Alternativen abarbeiten. For und Switch Statement �hnlich wie in doActions! """
	""" Falls lastReturn nicht gesetzt -> Semantischer Fehler in der
	    Konfigurationsdatei, da vor einer Alternative ein Befehl stehen muss """
	return

def doActions(tokens, patterns):
	""" TODOS:
	 * um�ndern in begins_with, da nicht unbedingt Whitespace zwischen tokens. getStringTokens notwendig?
	 * return statement ist in diesem Konstrukt nicht m�glich. muss anders gel�st werden
	 * M�glicher Konflikt <or> mit Patterns? Sollte bei korrekter Implementierung
	   von doPrimitive eigentlich nicht auftreten, da Patterns ansonsten nur in Befehlen vorkommen.
	 * Sequenz ';' und '<or>' m�ssten in diesem Konstrukt den Returnwert pr�fen
	   und entscheiden ob n�chstes Kommand ausgef�hrt oder �bersprungen wird!
	   Schwierig, da nicht ganz klar ist wie der Returnwert weiter gehandhabt
	   werden soll, z.B. command1;command2<or>command3. Muss noch besprochen werden.
		M�glicherweise hilft hier folgender Aufrufcode, d.h. z.B.
			doActions("command1; command2<or> command3")
				doPrimitive("command1")
			doActions("; command2<or> command3")
				doSequence("command2<or> command3, returnVal")
					doPrimitive(command2)
			doActions("<or> command3")
				doAlternative("command3", returnVal)
					doPrimitive("command3")
				doAlternative("",returnVal)
			doActions("")
	"""
	lastReturn = null
	
	for token in tokens:
		try:
			{ "{": doLoop(tokens, patterns),
			  "[": addPattern(tokens, patterns),
			  ";": doSequence(tokens, patterns, lastReturn),
			  "<or>" : doAlternative(tokens, patterns, lastReturn),
			  "}": return "from loop"}[value]()
		except KeyError:
			# default action
			returnValue = doPrimitive(tokens, patterns)
			
	return

""" if __name__ == "__main__": <- Auto generiert """

"Platzhalter, experimentiell"
"parser = OptionParser()"
"""parser.add_option("-f", "--filename", "filename")"""
filename = "asdf"
fileString = readFile(filename)
tokens = getTokensFromString(fileString)
doActions(tokens, [], 0)

