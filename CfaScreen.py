#!/usr/bin/env python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

import os, subprocess
import signal, time

class CfaScreen:
	def __init__(self, name):
		signal.signal(signal.SIGALRM, self.handler)
		self.dirPath = os.path.dirname(os.path.abspath(__file__))
		self.name = name
		self.half_menu = False
		self.upScreen = None
		self.downScreen = None
		self.nextScreen = None
		self.prevScreen = None
		self.ledLabels = []
		self.ledColors = ['black', 'black', 'black', 'black']
		self.ledMeterBarStatus = 0
		self.isMenuScreen = False
		self.duration = 0
		self.heartbeat = False
		self.widgets = {}
		self.tDelta = 100
		self.t = 0

	def handler(self, signum, frame):
	    raise Exception('Action took too much time')		

	def pushDownScreen(self, downScreen):
		if self.downScreen == None:
			self.downScreen = downScreen
			downScreen.upScreen = self
		else:	
			self.downScreen.pushDownScreen(downScreen)

	def pushNextScreen(self, nextScreen):
		if self.nextScreen == None:
			self.nextScreen = nextScreen
			nextScreen.prevScreen = self
		else:	
			self.nextScreen.pushNextScreen(nextScreen)

	def arrange(self, screen):
	    # If there's vertical neighboring screens, arrange menu-type screen
	    if self.downScreen or self.upScreen:
	        # LED info to show ... half-screen menu
	        if self.ledLabels:
	            self.half_menu = True
	        # No LED info, full screen menu        
	        else:
	            pass
	        # Draw half-screen menu title 
	        self.set_MENU_label(screen)
	        # Set LED labels only if we got half menu
	        if self.half_menu:
	            self.handleLedLabels(screen)

	        if self.upScreen:
	                self.set_MenuUp_label(screen, self.upScreen.name)
	        elif self.prevScreen:
	                self.set_MenuLeft_label(screen, self.prevScreen.name)
	        if self.nextScreen:
	                self.set_MenuRight_label(screen, self.nextScreen.name)
	        if self.downScreen:
	                self.set_MenuDown_label(screen, self.downScreen.name)

	    # Otherwise the screen is just horizontally neighbored            
	    else:
	        if self.nextScreen:    
	            self.set_next_label(screen, self.nextScreen.name)
	        if self.prevScreen:    
	            self.set_prev_label(screen, self.prevScreen.name)

	def handleLedLabels(self, screen):
	    for x in range(0,4):
	        if self.ledLabels[x] != None:
	            if x == 0:
	                self.set_LED1_label(screen, self.ledLabels[x])
	            if x == 1:
	                self.set_LED2_label(screen, self.ledLabels[x])
	            if x == 2:
	                self.set_LED3_label(screen, self.ledLabels[x])
	            if x == 3:
	                self.set_LED4_label(screen, self.ledLabels[x])                                    

	def set_LED1_label(self, screen, labeltext):
	    text = labeltext[:3]
	    screen.add_icon_widget("LED1arrow", 1, 1, "SELECTOR_AT_RIGHT")
	    self.put_text(screen, "LED1_label_widget", text, 2, 1)

	def set_LED2_label(self, screen, labeltext):
	    text = labeltext[:3]    
	    screen.add_icon_widget("LED2arrow", 1, 2, "SELECTOR_AT_RIGHT")    
	    self.put_text(screen, "LED2_label_widget", text, 2, 2)

	def set_LED3_label(self, screen, labeltext):
	    text = labeltext[:3]    
	    screen.add_icon_widget("LED3arrow", 1, 3, "SELECTOR_AT_RIGHT")    
	    self.put_text(screen, "LED3_label_widget", text, 2, 3)

	def set_LED4_label(self, screen, labeltext):
	    text = labeltext[:3]    
	    screen.add_icon_widget("LED4arrow", 1, 4, "SELECTOR_AT_RIGHT")
	    self.put_text(screen, "LED4_label_widget", text, 2, 4)

	def set_MENU_label(self, screen):
	    if self.half_menu:
	        text = self.name[:4]
	        screen.add_icon_widget("menu_icon_widget_1", 13, 1, "BLOCK_FILLED")
	        screen.add_icon_widget("menu_icon_widget_2", 14, 1, "BLOCK_FILLED")    
	        self.put_text(screen, "menu_label_widget", text, 15, 1)
	        screen.add_icon_widget("menu_icon_widget_3", 19, 1, "BLOCK_FILLED")
	        screen.add_icon_widget("menu_icon_widget_4", 20, 1, "BLOCK_FILLED")
	    else:
	        text = self.name[:14]
	        screen.add_icon_widget("menu_icon_widget_1", 1, 1, "BLOCK_FILLED")
	        screen.add_icon_widget("menu_icon_widget_2", 2, 1, "BLOCK_FILLED")
	        screen.add_icon_widget("menu_icon_widget_3", 3, 1, "BLOCK_FILLED")
	        self.put_text(screen, "menu_label_widget", text, 4, 1)
	        screen.add_icon_widget("menu_icon_widget_4", 18, 1, "BLOCK_FILLED")        
	        screen.add_icon_widget("menu_icon_widget_5", 19, 1, "BLOCK_FILLED")
	        screen.add_icon_widget("menu_icon_widget_6", 20, 1, "BLOCK_FILLED")        

	def set_MenuUp_label(self, screen, labeltext):
	    if self.half_menu:
	        text = labeltext[:7]    
	        screen.add_icon_widget("menuup_arrow", 20, 2, "ARROW_UP")
	        self.put_text(screen, "menuup_text", text, 13, 2)
	    else:
	        text = labeltext[:18]    
	        screen.add_icon_widget("menuup_arrow", 20, 2, "ARROW_UP")
	        self.put_text(screen, "menuup_text", text, 1, 2)

	def set_MenuLeft_label(self, screen, labeltext):
	    if self.half_menu:
	        text = labeltext[:7]    
	        screen.add_icon_widget("menuleft_arrow", 20, 2, "ARROW_LEFT")
	        self.put_text(screen, "menuleft_text", text, 13, 2)
	    else:
	        text = labeltext[:18]    
	        screen.add_icon_widget("menuleft_arrow", 20, 2, "ARROW_LEFT")
	        self.put_text(screen, "menuleft_text", text, 1, 2)

	def set_MenuRight_label(self, screen, labeltext):
	    if self.half_menu:    
	        text = labeltext[:7]    
	        screen.add_icon_widget("menuright_arrow", 20, 3, "ARROW_RIGHT")
	        self.put_text(screen, "menuright_text", text, 13, 3)
	    else:
	        text = labeltext[:18]    
	        screen.add_icon_widget("menuright_arrow", 20, 3, "ARROW_RIGHT")
	        self.put_text(screen, "menuright_text", text, 1, 3) 

	def set_MenuDown_label(self, screen, labeltext):
	    if self.half_menu:    
	        text = labeltext[:7]    
	        screen.add_icon_widget("menudown_arrow", 20, 4, "ARROW_DOWN")
	        self.put_text(screen, "menudown_text", text, 13, 4)    
	    else:
	        text = labeltext[:18]    
	        screen.add_icon_widget("menudown_arrow", 20, 4, "ARROW_DOWN")
	        self.put_text(screen, "menudown_text", text, 1, 4)

	def set_next_label(self, screen, labeltext):
		text = labeltext[:7]
		l = len(text)
		self.set_next_icon(screen, 4)
		self.put_text(screen, "nextLabel_text", text, 20 - l, 4)

	def set_prev_label(self, screen, labeltext):
		text = labeltext[:7]
		self.set_prev_icon(screen, 4)
		self.put_text(screen, "prevLabel_text", text, 2, 4)

	def set_next_icon(self, screen, ypos):
	    screen.add_icon_widget("next_arrow", 20, ypos, "ARROW_RIGHT")

	def set_prev_icon(self, screen, ypos):
	    screen.add_icon_widget("prev_arrow", 1, ypos, "ARROW_LEFT")

	def put_text(self, screen, widgetname, text, posx, posy):
	    screen.add_string_widget(widgetname, text, posx, posy)

	def update_LED_meter(self, ledIndex, percent):
		if percent >= 80:
			newLedMeterColor = 'red'
		elif 80 > percent >= 60:
			newLedMeterColor = 'yellow'			
		elif 60 > percent >= 10:
			newLedMeterColor = 'green'
		elif 10 > percent >= 0:
			newLedMeterColor = 'black'
		else:
			newLedMeterColor = 'black'

		if self.ledColors[ledIndex] != newLedMeterColor:
			led = str(ledIndex + 1)
			if newLedMeterColor == 'black':
				cmd = self.dirPath + "/cfont --dev /dev/ttyACM0 --led " + led + " 0 0"
			elif newLedMeterColor == 'red':
				cmd = self.dirPath + "/cfont --dev /dev/ttyACM0 --led " + led + " 100 0"
			elif newLedMeterColor == 'yellow':
				cmd = self.dirPath + "/cfont --dev /dev/ttyACM0 --led " + led + " 100 100"
			elif newLedMeterColor == 'green':
				cmd = self.dirPath + "/cfont --dev /dev/ttyACM0 --led " + led + " 0 100"
			else:
				cmd = self.dirPath + "/cfont --dev /dev/ttyACM0 --led " + led + " 0 0"
			self.ledColors[ledIndex] = newLedMeterColor
			signal.alarm(1)
			try:
				subprocess.call(cmd, shell=True)
			except:
				self.t = 0
			finally:
				signal.alarm(0)

	def update_LED_meter_bar(self, percent):
		if percent >= 80:
			newLedMeterBarStatus = 80
		elif 80 > percent >= 60:
			newLedMeterBarStatus = 60			
		elif 60 > percent >= 40:
			newLedMeterBarStatus = 40
		elif 40 > percent >= 10:
			newLedMeterBarStatus = 10
		else:
			newLedMeterBarStatus = 0

		if newLedMeterBarStatus != self.ledMeterBarStatus:
			if newLedMeterBarStatus >= 80:
				cmd = self.dirPath + "/cfont --dev /dev/ttyACM0 --led 1 100 0 --led 2 100 100 --led 3 0 100 --led 4 0 100"
			elif 80 > newLedMeterBarStatus >= 60:
				cmd = self.dirPath + "/cfont --dev /dev/ttyACM0 --led 1 0 0 --led 2 100 100 --led 3 0 100 --led 4 0 100"
			elif 60 > newLedMeterBarStatus >= 40:
				cmd = self.dirPath + "/cfont --dev /dev/ttyACM0 --led 1 0 0 --led 2 0 0 --led 3 0 100 --led 4 0 100"
			elif 40 > newLedMeterBarStatus >= 10:
				cmd = self.dirPath + "/cfont --dev /dev/ttyACM0 --led 1 0 0 --led 2 0 0 --led 3 0 0 --led 4 0 100"
			else:
				cmd = self.dirPath + "/cfont --dev /dev/ttyACM0 --led 1 0 0 --led 2 0 0 --led 3 0 0 --led 4 0 0"
			self.ledMeterBarStatus = newLedMeterBarStatus
			signal.alarm(1)
			try:
				subprocess.call(cmd, shell=True)
			except:
				self.t = 0
			finally:
				signal.alarm(0)

	def update_widget_text(self, widget, newText):
		signal.alarm(1)
		try:
			widget.set_text(newText)
		except:
			self.t = 0
		finally:
			signal.alarm(0)

	def update_widget_bar(self, widget, newLength):
		signal.alarm(1)
		try:
			widget.set_length(newLength)
		except:
			self.t = 0
		finally:
			signal.alarm(0)

	def ready(self):
		if self.t > self.tDelta * 1000:
			self.t = 0
			return True
		else:
			self.t = self.t + 1			
			return False

	# This methods have to be overwritten with actual code as needed
	# on screen instances...
	
	# This method/function is intended to generate initial screen 
	# labeling and may also initialize and stor widgets whose 
	# values may be updated.
	# It is called once, upon screen creation
	def init(self, func):
		pass

	# This method/function is intended to update the status of any of 
	# widget values on the screen. It is called on every loop.
	def updateWidgets(self, screen):
		pass

	# This method/function is intended to clean/close any stuff needed 
	# before destroying the screen.
	def close(self, screen):
		cmd = self.dirPath + "/cfont --dev /dev/ttyACM0 --led 1 0 0 --led 2 0 0 --led 3 0 0 --led 4 0 0"
		signal.alarm(1)
		try:
			subprocess.call(cmd, shell=True)
		except:
			pass
		finally:
			signal.alarm(0)
		time.sleep(0.500)

	# This method/function is executed if the screen allows to handle a
	# keyUp press event (not a menu-type screen)... it may increase some value. 
	def handleUp(self, screen):
		pass

	# This method/function is executed if the screen allows to handle a
	# keyDown press event (not a menu-type screen)... it may decrease some value. 
	def handleDown(self, screen):
		pass

	# This method/function is executed if keyEnter press event ... 
	# (execute some command)
	def handleEnter(self, screen):
		pass				