#!/usr/bin/env python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# Imports
from lcdproc.server import Server

import signal, time
import CfaScreen
import home_screen
import sys_screens
import IntelHDA_screens

def handler(signum, frame):
    raise Exception('Action took too much time')

def main():

    signal.signal(signal.SIGALRM, handler)

    # Initialize the LCD object instance
    lcd = Server(debug=False)
    lcd.start_session()
    lcd.add_key("Up")
    lcd.add_key("Down")
    lcd.add_key("Right")
    lcd.add_key("Left")
    lcd.add_key("Enter")

    # Initialize root/initial cfaScreen instance
    cfaScreen = home_screen.get()

    # Append Screens to base cfaInstance
    cfaScreen.pushDownScreen(sys_screens.get())
    cfaScreen.pushDownScreen(IntelHDA_screens.get())    

    # Spawn the initial screen
    screen = genScreen(lcd, cfaScreen)

    # Loop logic... (read events and react)
    try:
        while True:
            signal.alarm(1)
            try:
                event = lcd.poll()
            except:
                event = None
            finally:
                signal.alarm(0)
            if not event == None:
                lines = event.splitlines()
                if lines[0] == 'key Enter':
                    cfaScreen.handleEnter(screen)
                elif lines[0] == 'key Up':
                    if cfaScreen.upScreen == None and cfaScreen.downScreen == None:
                        cfaScreen.handleUp(screen)
                    elif not cfaScreen.upScreen == None:
                        clearScreen(lcd, cfaScreen)                        
                        cfaScreen = cfaScreen.upScreen
                        screen = genScreen(lcd, cfaScreen)
                    else:
                        pass
                elif lines[0] == 'key Down':
                    if cfaScreen.downScreen == None and cfaScreen.upScreen == None:
                        cfaScreen.handleDown(screen)
                    elif not cfaScreen.downScreen == None:
                        clearScreen(lcd, cfaScreen)                        
                        cfaScreen = cfaScreen.downScreen
                        screen = genScreen(lcd, cfaScreen)
                    else:
                        pass
                elif lines[0] == 'key Right':
                    if not cfaScreen.nextScreen == None:
                        clearScreen(lcd, cfaScreen)                        
                        cfaScreen = cfaScreen.nextScreen
                        screen = genScreen(lcd, cfaScreen)
                    else:
                        pass
                elif lines[0] == 'key Left':
                    if not cfaScreen.prevScreen == None:
                        clearScreen(lcd, cfaScreen)                        
                        cfaScreen = cfaScreen.prevScreen
                        screen = genScreen(lcd, cfaScreen)
                    else:
                        pass
            else:
                # Here the update functions are called
                if cfaScreen.ready():
                    cfaScreen.updateWidgets(screen)
        time.sleep(0.100)
    # LCD Cleanup on exit        
    finally:
        # Execute closing code before clearing screen
        clearScreen(lcd, cfaScreen)


def genScreen(lcd, cfaScreen):
    # Spawn screen and setup basic properties
    screen = lcd.add_screen(cfaScreen.name)

    if cfaScreen.heartbeat:
        screen.set_heartbeat('on')
    else:
        screen.set_heartbeat('off')
    screen.set_duration(cfaScreen.duration)

    # Initialization code is executed
    cfaScreen.arrange(screen)
    cfaScreen.init(screen)

    return screen


def clearScreen(lcd, cfaScreen):
    cfaScreen.close(cfaScreen)
    lcd.del_screen(cfaScreen.name)

# Run
if __name__ == "__main__":
    main()