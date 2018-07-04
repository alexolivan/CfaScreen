#!/usr/bin/env python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# Imports
from lcdproc.server import Server
import CfaScreen
import signal, time


rootScreen = None

# Single/Root screen is returned with all its 
# subtree of screens to the main cfa_screen logic
def get():
	rootScreen = CfaScreen.CfaScreen("Menu1")

	# Attach subscreens as needed before return
	rootScreen.pushNextScreen(defineMenu2())

	# finally, return the screen
	return rootScreen

# Subscreens definitions
def defineMenu2():
	screen = CfaScreen.CfaScreen("Menu2")
	screen.pushNextScreen(defineScreen22())
	screen.pushNextScreen(defineScreen23())
	screen.pushDownScreen(defineMenu3())
	return screen

def defineMenu3():
	return CfaScreen.CfaScreen("Menu3")

def defineScreen22():
	return CfaScreen.CfaScreen("Screen22")

def defineScreen23():
	return CfaScreen.CfaScreen("Screen23")	