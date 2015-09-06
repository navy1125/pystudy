#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys
import shutil
import datetime
import re
import os
import string
import re,xml.dom.minidom,codecs
from optparse import OptionParser
changenum = 0
changefilenum = 0
def parsedir(dstdir):
	files = os.listdir(dstdir)
	for file in files:
		if os.path.isdir(dstdir  + "/" +  file):
			parsedir(dstdir + "/" + file)
			continue
		#elif re.search(".lua$",file) != None or re.search(".xml$",file) != None or re.search(".example$",file) != None:
		elif re.search(".go$",file) != None:
			print(file)
			changefile(dstdir,file)

def changefile(dstdir,dstfile):
	global changenum
	global changefilenum
	print(dstfile)
	dst = open(dstdir + "/" + dstfile,"r")
	dstlines = dst.readlines()
	dst.close()
	dst = open(dstdir + "/" + dstfile,"w")
	i = 0
	j = 0
	first = True
	for dstline in dstlines:
		tmp = dstline
		tmp = tmp.replace('SetEncrypt(rev.GetEncrypt()','SetEncrypt(rev.GetEncrypt(),rev.GetEncryptkey()')
		#tmp = tmp.replace('SetEncrypt','SetEncrypt')
		if tmp != dstline:
			changenum = changenum + 1
			dstline = tmp
			if first == True:
				changefilenum = changefilenum + 1
				first = False
		dst.write(dstline)

	dst.close()



def main():
	parsedir("../")
	print("change Total file num:",changefilenum)
	print("change Total num:",changenum)

main()
