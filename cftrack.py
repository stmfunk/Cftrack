#!/usr/local/bin/python
import sys
import re
import sqlite3
import git
import os
import shutil
import argparse
import yaml

def cmdType(cmd, onFile):
    if cmd.lower().strip() == 'rm':
        return Remove(onFile)
    if cmd.lower().strip() == 'update':
        return Update(onFile)
    if cmd.lower().strip() == 'add':
        return Add(onFile)

class allPrefs:
    'Object containing all preferences and files'
    def __init__(self, cftrc=False, withPrefs=False):
        if withPrefs:
            self.prefs = withPrefs
        elif cftrc:
            self.prefs = yaml.load(cftrc)
        else:
            self.prefs = {'dbPath':os.expanduser('~')+'/.cftrack/cftrack.db',
                    'dataPath':os.expanduser('~')+'/.cftrack/'}

    def writeOut(toFile):
        toFile.write(yaml.dump(self.prefs))

    def makeRepoDir(self, name):
        repoDir = self.prefs['dataPath']+name
        if not os.path.exists(repoDir):
            os.mkdir(self.prefs['dataPath']+name)
        return repoDir

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
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    if not os.path.exists(path):
        fl = open(path, 'w')
        fl.close()
    return path



class Command:
    'Command subclass'
    def __init__(self, onFile):
        self.onFile = onFile
        try:
            cftrc = open(os.path.expanduser('~')+'/.cftrc', 'r')
            self.curPref = allPrefs(cftrc)
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

                    self.curPref = allPrefs(withPrefs=prefs)

                    self.curPref.writeOut(cftrc)

                else:
                    self.curPref = allPrefs()


        self.mainRepo = git.Repo.init(self.curPref.prefs['dataPath'])
    
        self.path = os.path.abspath(self.onFile.name)
        self.cfdir = ensure(self.curPref.prefs['dataPath'])
        self.cfdb = sqlite3.connect(ensure(self.curPref.prefs['dbPath']))
        self.cur = self.cfdb.cursor()
    
    def execute(self):
        pass


class Add(Command):
    def execute(self):
	    try:
	        self.cur.execute('select count(*) FROM tracked')
	    except sqlite3.OperationalError:
	        self.cur.execute('create table tracked (id INTEGER PRIMARY KEY NOT NULL , path CHAR(250) NOT NULL, repoName CHAR(100))')
	
	    for line in self.cur.execute('SELECT * FROM tracked'):
	        if line[1] == self.path:
	            print 'Already tracking: '+self.onFile.name
	            exit(0)
	    
	    self.cur.execute("INSERT INTO tracked (path) VALUES ('%s')" % self.path) 
	    self.cfdb.commit()
	    fid = self.cur.execute("SELECT id FROM tracked WHERE path = '%s'" % self.path).fetchone()[0]
	    repoName = (str(fid)+'_'+args.file.name).replace('.', '_')
	
	    self.cur.execute("UPDATE tracked SET repoName = '%s' WHERE path = '%s'" % (repoName, path))
	    self.cfdb.commit()
	
	    repoDir = curPref.makeRepoDir(repoName+'/')
	    
	    subRepo = git.Repo.init(repoDir)
	
	    shutil.copy2(path, repoDir)
	    subIndex = subRepo.index
	    subIndex.add([onFile.name])
	    subIndex.commit('Added configFile %s' % self.path)
	
	    mainRepo.index.commit('Started tracking %s' % repoName)
	    print "Added config file %s" % onFile.name

class Update(Command):
    def execute(self):
        pass

class Remove(Command):
    def execute(self):
        pass


def main():
    try:
        parser = argparse.ArgumentParser(description='Track config files/directories and distribute them')
        parser.add_argument('command', help='pass one of the following commands: add, update, rm', type=str)
        parser.add_argument('file', help='path to config file to be tracked', type=file)
        args = parser.parse_args()
        cmd = cmdType(args.command, args.file)
    except IOError as io:
        sys.stderr.write('No such file or directory: %s\n' % io.filename)
        exit(1)

    cmd.execute()

           
if __name__ == '__main__':
    main()
