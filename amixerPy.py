#!/usr/bin/env python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# Imports
import subprocess
from operator import itemgetter

def processFirstLine(line, ALSAcontrol):
	values = line.split(',')
	for value in values:
		parts = value.split('=')
		if parts[0] == "access":
			if parts[1].startswith('rw'):
				ALSAcontrol['readOnly'] = False
			else:
				ALSAcontrol['readOnly'] = True
		elif parts[0] == 'values':
			ALSAcontrol['valuesCount'] = parts[1]
		elif parts[0] == 'numid':
			ALSAcontrol['id'] = int(parts[1])
		elif parts[0] == 'name':
			ALSAcontrol['name'] = str(parts[1]).replace("'", "")
		elif parts[0] == 'dBscale-min':
			ALSAcontrol['base'] = getUnitAndValue(parts[1])[0]			 			
			ALSAcontrol['unit'] = getUnitAndValue(parts[1])[1]
		else:
			ALSAcontrol[parts[0]] = parts[1]
	return ALSAcontrol


def processRestOfLines(controlType, semiColonLines, colonLines, pipeLines, ALSAcontrol):
	if controlType == "INTEGER":
		for line in colonLines:
			parts = line.split('=')
			values = parts[1].split(',')
			ALSAcontrol['values'] = []
			for value in values:
				ALSAcontrol['values'].append(value)

		if pipeLines:
			if len(pipeLines) > 1:
				pass
			else:
				ALSAcontrol = processFirstLine(pipeLines[0], ALSAcontrol)		

	elif controlType == "BOOLEAN":
		for line in colonLines:
			parts = line.split('=')
			values = parts[1].split(',')
			ALSAcontrol['values'] = []
			for value in values:
				if value == 'on':
					ALSAcontrol['values'].append(True)
				else:
					ALSAcontrol['values'].append(False)	 

	elif controlType == "ENUMERATED":
		ALSAcontrol['options'] = []
		for line in semiColonLines:
			parts = line.split("'")
			ALSAcontrol['options'].append(parts[1])
		selected = int(colonLines[0].split('=')[1])	
		ALSAcontrol['selectedOption'] = ALSAcontrol['options'][selected]

	return ALSAcontrol


def clearBlankSpaces(ALSAcontrolList):
	for index, line in enumerate(ALSAcontrolList):
		if not index == 0:
			line = line.strip()
			line = line.replace(" ", "")
			ALSAcontrolList[index] = line
	return ALSAcontrolList


def getUnitAndValue(string):
	result = []
	numeric = '0123456789-.'
	for i,c in enumerate(string):
		if c not in numeric:
			break
	result.append(string[:i])			
	result.append(string[i:])
	return result


def getControlDict(ALSAcontrolList):
	ALSAcontrol = {}
	semiColonLines = []
	colonLines = []
	pipeLines = []
	controlType = ""
	for index, line in enumerate(ALSAcontrolList):
		if index == 0:
			ALSAcontrol = processFirstLine(line, ALSAcontrol)
		else:
			if line.startswith(';'):
				if index == 1:
					ALSAcontrol = processFirstLine(line[1:], ALSAcontrol)
					if "INTEGER" in line:
						controlType = "INTEGER"
					elif "BOOLEAN" in line:
						controlType = "BOOLEAN"
					elif "ENUMERATED" in line:
						controlType = "ENUMERATED"
				else:		
					semiColonLines.append(line[1:])
			elif line.startswith(':'):
				colonLines.append(line[1:])
			elif line.startswith('|'):
				pipeLines.append(line[1:])

	if "IEC958" not in ALSAcontrol['name'] and "HDMI" not in ALSAcontrol['name'] and "Map" not in ALSAcontrol['name']:
		ALSAcontrol = processRestOfLines(controlType, semiColonLines, colonLines, pipeLines, ALSAcontrol)
		return ALSAcontrol
	else:
		return None

def getAmixerContents(card):
	ALSAcontrolsList = []
	ALSAcontrolList = []
	ALSAcontrols = []

	amixer = subprocess.Popen(['amixer', '-c', str(card), 'contents'], stdout=subprocess.PIPE)
	content = amixer.stdout.readlines()

	for line in content:
		line = line.replace("\n", "")
		if line.startswith('numid=', 0, 6):
			if ALSAcontrolList:
				ALSAcontrolsList.append(ALSAcontrolList)
				ALSAcontrolList = []
				ALSAcontrolList.append(line)
			else:
				ALSAcontrolList.append(line)
		else:
			ALSAcontrolList.append(line)

	for ALSAcontrolList in ALSAcontrolsList:
		if "IEC958" in ALSAcontrolList[0]:
			ALSAcontrolsList.remove(ALSAcontrolList)
		else:
			if "MIXER" in ALSAcontrolList[0]:
				pass
			elif "CARD" in ALSAcontrolList[0]:
				pass
			elif "PCM" in ALSAcontrolList[0]:
				pass
			else:
				ALSAcontrolsList.remove(ALSAcontrolList)

	for ALSAcontrolList in ALSAcontrolsList:
		if "IEC958" in ALSAcontrolList[1] or "BYTE" in ALSAcontrolList[1]:
			ALSAcontrolsList.remove(ALSAcontrolList)
		else:	
			if "INTEGER" in ALSAcontrolList[1]:
				pass
			elif "BOOLEAN" in ALSAcontrolList[1]:
				if "rw---" not in ALSAcontrolList[1]:
					ALSAcontrolsList.remove(ALSAcontrolList)
				else:
					pass
			elif "ENUMERATED" in ALSAcontrolList[1]:
				pass		
			else:
				ALSAcontrolsList.remove(ALSAcontrolList)

	for ALSAcontrolList in ALSAcontrolsList:
		ALSAcontrolList = clearBlankSpaces(ALSAcontrolList)

	for ALSAcontrolList in ALSAcontrolsList:
		ALSAcontrol = getControlDict(ALSAcontrolList)
		if ALSAcontrol:
			ALSAcontrols.append(ALSAcontrol)

	sortedControls = sorted(ALSAcontrols, key=itemgetter('id'))
	return sortedControls


def amixerCget(card, numid):
	ALSAcontrolList = []

	amixer = subprocess.Popen(['amixer', '-c', str(card), 'cget', "numid=" + str(numid)], stdout=subprocess.PIPE)
	content = amixer.stdout.readlines()

	for line in content:
		line = line.replace("\n", "")
		ALSAcontrolList.append(line)

	ALSAcontrolList = clearBlankSpaces(ALSAcontrolList)
	ALSAcontrol = getControlDict(ALSAcontrolList)

	return ALSAcontrol


def amixerCset(card, numid, value):
	ALSAcontrolList = []

	try: 
		int(value)
		amixer = subprocess.Popen(['amixer', '-c', str(card), 'cset', "numid=" + str(numid), "--", str(value)], stdout=subprocess.PIPE)
	except ValueError:
		amixer = subprocess.Popen(['amixer', '-c', str(card), 'cset', "numid=" + str(numid), value], stdout=subprocess.PIPE)

	
	content = amixer.stdout.readlines()

	for line in content:
		line = line.replace("\n", "")
		ALSAcontrolList.append(line)

	ALSAcontrolList = clearBlankSpaces(ALSAcontrolList)
	ALSAcontrol = getControlDict(ALSAcontrolList)

	return ALSAcontrol