import os
import glob
import xml.dom
import collections

from xml.dom.minidom import parse, parseString, Node
from xml.dom import pulldom

currentFile = None
currentTarget = None

targets = []
properties = []

## tags is a dictonary the structure of which is a key=tagName value=list of (tuple { filename, parent target, attributes}
tags = dict()


def resetCurrent():
	global currentFile
	global currentTarget
	currentFile = None
	currentTarget = None


## scan for all potential build files (eg. build.xml, deploy.xml, vis_build.xml, test.xml)
def allAntProjectFiles() :
	antProjectFiles = []
	for root, dirs, files in os.walk('.'):
		for filename in glob.glob(root + '/build.xml'):
			if len(filename) < 40 and filename.find('test.xml') == -1:
				try :
					dom = parse(filename)
					
					project = dom.getElementsByTagName("project")[0]
					
					if(project is not None):
						antProjectFiles.append(filename)
				except:
					continue
	return antProjectFiles
		

def processAntFile(filename):
	global currentFile
	handle = open(filename)
	doc = pulldom.parse(handle)
	resetCurrent()
	currentFile = filename
	for event, node in doc:
		if event == pulldom.START_ELEMENT:
			printNode(node)
			processNode(node)

def printNode(node):
	if node.nodeType == Node.ELEMENT_NODE: 
		if node.tagName != 'property':
			print(node.tagName + ' ' + printAttributes(node))

def printAttributes(node):
	attributes = '';
	for i in range(node.attributes.length):
		attributes = attributes + printAttribute(node.attributes.item(i)) + ' ' 
	return attributes

def printAttribute(attr):
	if attr.name != 'None': 
		return attr.name + "='" + attr.value +"'"


def processNode(node):
	global currentTarget
	if node.nodeType == Node.ELEMENT_NODE: 
		props = ''
		attrMap = processAttributes(node)
		if node.tagName == 'target' :
			targets.append(attrMap['name'])
			currentTarget = attrMap['name']
		elif node.tagName == 'property':
			
			if 'name' in attrMap:
				props = props + ' ' + "name='"+ attrMap.pop('name') +"'" 
			for key in attrMap.keys():
				props = props + ' ' + key+"='"+ attrMap[key] +"'"
			properties.append(props)
		else:
			for key in attrMap.keys():
				props = props + ' ' + key+"='"+ attrMap[key] +"'"
		if node.tagName not in tags:
			tags[node.tagName] = []
		tags[node.tagName].append([currentFile, currentTarget, props])

def processAttributes(node):
	attrMap = dict()
	for i in range(node.attributes.length):
		processAttribute(attrMap, node.attributes.item(i))
	return attrMap

def processAttribute(map, attr):
	if attr.name != 'None': 
		map[attr.name] = attr.value

def count(p):
	cnt = dict()
	for word in p:
		try: 
			cnt[word]
			cnt[word] += 1
		except:
			cnt[word] = 1
	return cnt

def printDictionarySortedByValue(aDict):
	for key, value in sorted(aDict.items(), key=lambda t: t[1], reverse=True):
		print("%s:  %s" % (value, key))

def printTagsSortedByBuildFile(aDict):
	for key, value in sorted(aDict.items(), key=lambda t: t[0]):
		print("\n%s:\n" % (key))
		for i in value:
			fileName, target, attr = i
			print("\t%s  %s  %s" % (fileName, target, attr))


for projectFiles in allAntProjectFiles():
	print('---------- ' + projectFiles + ' ----------------------------------------------')
	processAntFile(projectFiles)

print("\n---------------targets  ")
printDictionarySortedByValue(count(targets))
print("\n---------------properties  ")
printDictionarySortedByValue(count(properties))

printTagsSortedByBuildFile(tags)

## scan for all potential build files (eg. build.xml, deploy.xml, vis_build.xml, test.xml)
## for each file
## parse it
## count each target name
## count each task used
## count each property defined
## count each 
