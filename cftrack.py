#!/usr/local/bin/python
import sys
import sqlite3
import git
import os
import shutil
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


    mainRepo = git.Repo.init(curPref.prefs['dataPath'])

    try:
        parser = argparse.ArgumentParser(description='Track config files/directories and distribute them')
        parser.add_argument('file', help='path to config file to be tracked', type=file)
        args = parser.parse_args()
        path = os.path.abspath(args.file.name)
        cfdir = ensure(curPref.prefs['dataPath'])
        cfdb = sqlite3.connect(ensure(curPref.prefs['dbPath']))
        cur = cfdb.cursor()
    except IOError as io:
        sys.stderr.write('No such file or directory: %s\n' % io.filename)
        exit(1)


    try:
        cur.execute('select count(*) FROM tracked')
    except sqlite3.OperationalError:
        cur.execute('create table tracked (id INTEGER PRIMARY KEY NOT NULL , path CHAR(250) NOT NULL, repoName CHAR(100))')

    for line in cur.execute('SELECT * FROM tracked'):
        scheme = dir(line)
        if not all(x in scheme for x in ['path','id','repoName']): 
            sys.stderr.write('Incorrect format for database\n')
            exit(2)
        if line.path == path:
            print 'Already tracking: '+args.file.name
            exit(0)
    
    cur.execute("INSERT INTO tracked (path) VALUES ('%s')" % path) 
    fid = cur.execute("SELECT id FROM tracked WHERE path = '%s'" % path).fetchone()[0]
    repoName = (str(fid)+'_'+args.file.name).replace('.', '_')
    cur.execute("UPDATE tracked SET repoName = '%s' WHERE path = '%s'" % (repoName, path))

    repoDir = curPref.makeRepoDir(repoName+'/')
    
    subRepo = git.Repo.init(repoDir)

    shutil.copy2(path, repoDir)

           
if __name__ == '__main__':
    main()

