#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,re,sys,string
import dircache
import re,xml.dom.minidom,codecs

OUT_FILE = "out/"

if __name__ == "__main__":
	print os.system("rm -vf %s"%OUT_FILE)
	print os.system("mkdir -p %s"%OUT_FILE)
	print os.system("rm -v %s/*.1*"%OUT_FILE)
	ret = os.popen('git log --name-only --pretty=format:"%ad" --date=raw')
	ret = ret.read()
	ret = ret.replace(' +0800','')
	commits = ret.split('\n')
	time = 0
	fdict = {}
	for commit in commits:
		if time == 0:
			time = commit
		else:
			if commit == "":
				time = 0
			elif fdict.has_key(commit) == False:
				fdict[commit]=time
				print commit+"."+time
				os.system("cp -vf %s %s/%s.%s"%(commit,OUT_FILE,commit,time))

