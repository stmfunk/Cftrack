#!/usr/local/bin/python
import sys
import sqlite3
import os
import argparse
import yaml

class allPrefs:
    'Object containing all preferences and files'
    def __init__(self, cftrc=False, withPrefs=False):
        if withPrefs:
            self.prefs = withPrefs
        elif cftrc:
            self.prefs = yaml.load(cftrc)
        else:
            self.prefs = {'dbPath':os.expanduser('~')+'/.cftrack/cftrack.db',
                    'dataPath':os.expanduser('~')+'/.cftrack'}

    def writeOut(toFile):
        toFile.write(yaml.dump(self.prefs))
        

def trueFalseInput(promptString):
    isIn= raw_input(promptString)
    while (True):
	    if (isIn[0] == 'y'):
	        return True
	    elif (isIn[0] == 'n'):
	        return False
	    else:
	        isIn = raw_input('Not a valid response: ')

def ensure(path):
    if (not os.path.exists(path)):
        os.makedirs(os.path.dirname(path))
        fl = open(path, 'w')
        fl.close()
    return path

def main():
    try:
        cftrc = open(os.path.expanduser('~')+'/.cftrc', 'r')
        curPref = allPrefs(cftrc)
    except IOError:
        if (trueFalseInput('No configuration file detected: \nCreate one now? y/n: ')):
            print 'Creating conf file at ~/.cftrc'
            cftrc = open(os.path.expanduser('~')+'/.cftrc', 'w')
            if (not trueFalseInput('Use default settings? y/n: ')):
                dbPath = raw_input('Please enter a sqlite3 database path: ')
                dataPath = raw_input('Please enter a repo directory: ')
                prefs = {}
                prefs['dbPath'] = dbPath
                prefs['dataPath'] = dataPath

                curPref = allPrefs(withPrefs=prefs)

                curPref.writeOut(cftrc)
            else:
                curPref = allPrefs()

    try:
        parser = argparse.ArgumentParser(description='Track config files/directories and distribute them')
        parser.add_argument('file', help='path to config file to be tracked', type=file)
        args = parser.parse_args()
        path = os.path.abspath(args.file.name)
        cfdir = ensure(curPref.prefs['dataPath'])
        cfdb = sqlite3.connect(ensure(curPref.prefs['dbPath']))
    except IOError as io:
        sys.stderr.write('No such file or directory: %s\n' % io.filename)
        return

    

if __name__ == '__main__':
    main()
