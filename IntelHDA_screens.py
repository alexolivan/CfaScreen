#!/usr/bin/env python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# Imports
from lcdproc.server import Server
import CfaScreen
import amixerPy
import math

rootScreen = None

# Single/Root screen is returned with all its eventual
# subtree of screens to the main cfa_screen logic
def get():
	rootScreen = CfaScreen.CfaScreen("Audio")

	# Get the list of ALSA mixer contents.
	contents = amixerPy.getAmixerContents(0)

	# Attach subscreens as needed before return
	rootScreen.pushNextScreen(defineIntelHDAMenuScreen(contents))	

	# finally, return the screen
	return rootScreen			


def defineIntelHDAMenuScreen(contents):
	# Here I give a basic, early/previous subdivision of ALSA controls
	# using some criteria (in this case the 'name' field), before sending them
	# to the sound screens auto generation.
	# By dividing controls between 'Playback', 'Capture' and 'Others' y spread the whole
	# lot of controls in 3 top level sub-menus.
	# Even so, there are 16 controls only for 'Playback' on my Intel HDA sound card, which
	# will result on 16 consecutive side-to-side screens, which is too much...
	# Since this isn't intended for actual production usage, but just for concept-proof 
	# testing using my Laptop...it is OK.
	# For produtive usage (I think on AudioScience) further, fine-grained, easier to use
	# screens structure tree (so, further contents subdivision) should be taylored. 
	playbackContents = []
	captureContents = []
	otherContents = []

	for content in contents:
		if "layback" in content['name']:
			playbackContents.append(content)

	for content in contents:
		if "apture" in content['name']:
			captureContents.append(content)

	for content in contents:
		if "layback" not in content['name'] and "apture" not in content['name']:
			otherContents.append(content)

	newScreen = CfaScreen.CfaScreen("IntelHDA")
	newScreen.pushNextScreen(processAmixerContents(playbackContents, 'Playback'))
	newScreen.pushDownScreen(processAmixerContents(captureContents, 'Capture'))
	newScreen.pushDownScreen(processAmixerContents(otherContents, 'Other'))

	return newScreen


def processAmixerContents(contents, name):
	newScreen = CfaScreen.CfaScreen(name)
	for content in contents:
		if content['type'] == 'ENUMERATED':
			newScreen.pushNextScreen(defineEnumeratedScreen(content))
		elif content['type'] == 'BOOLEAN':
			newScreen.pushNextScreen(defineBooleanScreen(content))
		elif content['type'] == 'INTEGER':
			newScreen.pushNextScreen(defineIntegerScreen(content))		
		else:
			pass

	# Override init function -> declare widgets/initilialize leds
	def init(screen):
		title = content['name'].replace(" ", "")[:15]
		screen.add_string_widget("title_widget", title, 1, 1)
	newScreen.init = init

	return newScreen


def defineEnumeratedScreen(content):
	newScreen = CfaScreen.CfaScreen(content['name'].replace(" ", ""))
		
	# Override init function -> declare widgets/initilialize leds
	def init(screen):
		title = content['name'].replace(" ", "")[:13]
		newScreen.readOnly = content['readOnly']
		newScreen.options = content['options']
		newScreen.selectedOption = content['selectedOption']
		newScreen.selectedOptionIndex = newScreen.options.index(content['selectedOption'])
		newScreen.numid = content['id']
		screen.add_string_widget("title_widget", title, 1, 1)

		newScreen.widgets['curr_widget'] = screen.add_string_widget("curr_widget", "current:", 1, 2)
		strvalue = newScreen.selectedOption[:11]
		newScreen.widgets['value_widget'] = screen.add_string_widget("value_widget", strvalue, 1, 3)

		if not newScreen.readOnly:
			screen.add_string_widget("next_widget", "Next", 16, 2)
			screen.add_icon_widget("on_arrow", 20, 2, "ARROW_UP")
			screen.add_string_widget("prev_widget", "Prev", 16, 3)
			screen.add_icon_widget("off_arrow", 20, 3, "ARROW_DOWN")
	newScreen.init = init

	# Override updateWidgets -> MAIN LOGIC here (Value updates)
	def updateWidgets(screen):
		updatedContent = amixerPy.amixerCget(0, newScreen.numid)
		if newScreen.selectedOption != updatedContent['selectedOption']:
			newScreen.selectedOption = updatedContent['selectedOption']
			newScreen.selectedOptionIndex = newScreen.options.index(updatedContent['selectedOption'])
			strvalue = newScreen.selectedOption[:11]
			newScreen.update_widget_text(newScreen.widgets['value_widget'], strvalue)
	newScreen.updateWidgets = updateWidgets

	# Override handleUp -> Manage an Up key-press (increase some value?)
	def handleUp(screen):
		if not newScreen.readOnly:		
			if newScreen.selectedOptionIndex + 1 >= len(newScreen.options):
				updatedContent = amixerPy.amixerCset(0, newScreen.numid, newScreen.options[0])			
			else:
				updatedContent = amixerPy.amixerCset(0, newScreen.numid, newScreen.options[newScreen.selectedOptionIndex + 1])
	newScreen.handleUp = handleUp

	# Override handleDown -> Manage a Down key-press (decrease some value?)
	def handleDown(screen):
		if not newScreen.readOnly:		
			if newScreen.selectedOptionIndex - 1 < 0:		
				updatedContent = amixerPy.amixerCset(0, newScreen.numid, newScreen.options[len(newScreen.options) - 1])
			else:			
				updatedContent = amixerPy.amixerCset(0, newScreen.numid, newScreen.options[newScreen.selectedOptionIndex - 1])
	newScreen.handleDown = handleDown

	return newScreen


def defineBooleanScreen(content):
	newScreen = CfaScreen.CfaScreen(content['name'].replace(" ", ""))

	# Override init function -> declare widgets/initilialize leds
	def init(screen):
		title = content['name'].replace(" ", "")[:15]
		newScreen.readOnly = content['readOnly']
		newScreen.value = content['values'][0]
		newScreen.numid = content['id']
		screen.add_string_widget("title_widget", title, 1, 1)
		
		strvalue = "status: ON" if newScreen.value else "status: OFF"
		newScreen.widgets['value_widget'] = screen.add_string_widget("value_widget", strvalue, 1, 2)

		if not newScreen.readOnly:
			screen.add_string_widget("on_widget", "ON", 18, 2)
			screen.add_icon_widget("on_arrow", 20, 2, "ARROW_UP")
			screen.add_string_widget("off_widget", "OFF", 17, 3)
			screen.add_icon_widget("off_arrow", 20, 3, "ARROW_DOWN")
	newScreen.init = init

	# Override updateWidgets -> MAIN LOGIC here (Value updates)
	def updateWidgets(screen):
		updatedContent = amixerPy.amixerCget(0, newScreen.numid)
		if newScreen.value != updatedContent['values'][0]:
			newScreen.value = updatedContent['values'][0]
			strvalue = "status: ON" if newScreen.value else "status: OFF"
			newScreen.update_widget_text(newScreen.widgets['value_widget'], strvalue)
	newScreen.updateWidgets = updateWidgets

	# Override handleUp -> Manage an Up key-press (increase some value?)
	def handleUp(screen):
		if not newScreen.readOnly:
			if not newScreen.value:
				updatedContent = amixerPy.amixerCset(0, newScreen.numid, "on")
	newScreen.handleUp = handleUp

	# Override handleDown -> Manage a Down key-press (decrease some value?)
	def handleDown(screen):
		if not newScreen.readOnly:		
			if newScreen.value:
				updatedContent = amixerPy.amixerCset(0, newScreen.numid, "off")
	newScreen.handleDown = handleDown

	return newScreen


def defineIntegerScreen(content):
	newScreen = CfaScreen.CfaScreen(content['name'].replace(" ", ""))
	newScreen.tDelta = 300

	# Override init function -> declare widgets/initilialize leds
	def init(screen):
		title = content['name'].replace(" ", "")[:15]
		newScreen.readOnly = content['readOnly']		
		newScreen.value = None
		newScreen.numid = content['id']
		newScreen.unit = content['unit']
		newScreen.base = float(content['base'])
		newScreen.step = float(amixerPy.getUnitAndValue(content['step'])[0])
		newScreen.maxi = int(content['max'])
		newScreen.mini = int(content['min'])				
		screen.add_string_widget("title_widget", title, 1, 1)

		if not newScreen.readOnly:
			screen.add_string_widget("inc_widget", "++", 18, 1)
			screen.add_icon_widget("menuup_arrow", 20, 1, "ARROW_UP")
			screen.add_string_widget("dec_widget", "--", 18, 2)
			screen.add_icon_widget("menudown_arrow", 20, 2, "ARROW_DOWN")

		newScreen.widgets['value_widget'] = screen.add_string_widget("value_widget", content['base'] + content['unit'], 1, 2)
		newScreen.widgets['hbar_widget'] = screen.add_hbar_widget("hbar_widget", 1, 3, 0)
		newScreen.update_LED_meter_bar(0)
	newScreen.init = init

	# Override updateWidgets -> MAIN LOGIC here (Value updates)
	def updateWidgets(screen):
		updatedContent = amixerPy.amixerCget(0, newScreen.numid)
		if newScreen.value != updatedContent['values'][0]:
			newScreen.value = int(updatedContent['values'][0])
			newScreen.volume = newScreen.base + newScreen.value * newScreen.step

			strvalue = str(newScreen.volume) + newScreen.unit
			newScreen.update_widget_text(newScreen.widgets['value_widget'], strvalue)

			prcnt = int(float(newScreen.value) / newScreen.maxi * 100)
			if not prcnt == 0:
				barlength = 100 * math.pow((math.log10(prcnt)), 13) / math.pow((math.log10(100)), 13)
			else:
				barlength = 0
			newScreen.update_widget_bar(newScreen.widgets['hbar_widget'], barlength)

			newScreen.update_LED_meter_bar(barlength)
	newScreen.updateWidgets = updateWidgets	

	# Override handleUp -> Manage an Up key-press (increase some value?)
	def handleUp(screen):
		if not newScreen.readOnly:		
			if not newScreen.value + 1 > newScreen.maxi:
				newScreen.value += 1
				updatedContent = amixerPy.amixerCset(0, newScreen.numid, newScreen.value)
	newScreen.handleUp = handleUp

	# Override handleDown -> Manage a Down key-press (decrease some value?)
	def handleDown(screen):
		if not newScreen.readOnly:
			if not newScreen.value - 1 < newScreen.mini:
				newScreen.value -= 1
				updatedContent = amixerPy.amixerCset(0, newScreen.numid, newScreen.value)
	newScreen.handleDown = handleDown		

	return newScreen