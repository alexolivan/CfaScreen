#!/usr/bin/env python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# Imports
from lcdproc.server import Server
import CfaScreen
import os
import signal, time

rootScreen = None

# Single/Root screen is returned with all its eventual
# subtree of screens to the main cfa_screen logic
def get():
	rootScreen = CfaScreen.CfaScreen("Home")
	rootScreen.ledLabels = [None, None, None, None]

	# Override init function -> declare widgets/initilialize leds
	def init(screen):
		rootScreen.widgets['home1_value_widget'] = screen.add_string_widget("home1_value_widget", "Banner1", 1, 1)
		rootScreen.widgets['hst_value_widget'] = screen.add_string_widget("hst_value_widget", os.uname()[1][:10], 1, 2)
		rootScreen.widgets['home2_value_widget'] = screen.add_string_widget("home2_value_widget", "Banner2", 1, 3)
		rootScreen.widgets['home3_value_widget'] = screen.add_string_widget("home3_value_widget", "Banner3", 1, 4)
	rootScreen.init = init

	# Override updateWidgets -> MAIN LOGIC here (Value updates)

	# Attach subscreens as needed before return

	# finally, return the screen
	return rootScreen

# Subscreens definitions
