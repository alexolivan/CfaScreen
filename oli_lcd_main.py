#!/usr/bin/env python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# Imports
import time
import datetime
from lcdproc.server import Server


# Control vars
initialScreenSet = 0
currentScreenSet = 0
currentScreen = 0
screen = None

# 'Config' var
screen_sets = [
    [
        {
            'name': 'System',
            'heartbeat': 'off',
            'duration': 0,
            'led_labels': ['CPU', 'Mem', 'FS', 'Uptime'],
            'test_label': 'screen 00'
        },
        {
            'name': 'Screen01',
            'heartbeat': 'off',
            'duration': 0,    
            'led_labels': [],           
            'test_label': 'screen 01'
        },    
        {
            'name': 'Screen02',
            'heartbeat': 'off',
            'duration': 0,    
            'led_labels': [],           
            'test_label': 'screen 02'
        }
    ],
    [
        {
            'name': 'Sound',
            'heartbeat': 'off',
            'duration': 0,
            'led_labels': ['ugg', 'mmm', None, 'pst'],      
            'test_label': 'screen 10'
        },
        {
            'name': 'Screen11',
            'heartbeat': 'off',
            'duration': 0,    
            'led_labels': [],          
            'test_label': 'screen 11'
        },    
        {
            'name': 'Screen12',
            'heartbeat': 'off',
            'duration': 0,    
            'led_labels': [],           
            'test_label': 'screen 12'
        }
    ],
    [
        {
            'name': 'Network',
            'heartbeat': 'off',
            'duration': 0,
            'led_labels': [None, 'foo ', 'bar ', 'pig '],            
            'test_label': 'screen 20'
        },
        {
            'name': 'Screen21',
            'heartbeat': 'off',
            'duration': 0,    
            'led_labels': [],            
            'test_label': 'screen 21'
        },    
        {
            'name': 'Screen22',
            'heartbeat': 'off',
            'duration': 0,    
            'led_labels': [],            
            'test_label': 'screen 22'
        }
    ],    
]


def main():

    global currentScreenSet
    global currentScreen

    # Initialize the LCD object instance
    lcd = Server(debug=False)
    lcd.start_session()
    lcd.add_key("Up")
    lcd.add_key("Down")
    lcd.add_key("Right")
    lcd.add_key("Left")
    lcd.add_key("Enter")  

    # Generate early set of screens
    genScreen(lcd)

    # Loop logic... (read events and react)
    try:
        while True:
            updateScreenData(lcd)
            event = lcd.poll()
            if not event == None:
                lines = event.splitlines()
                screenName = str(screen_sets[currentScreenSet][currentScreen]['name'])
                if lines[0] == 'key Enter':
                    print "handled key Enter"
                elif lines[0] == 'key Up':
                    if currentScreen == 0:
                        clearScreen(lcd, screenName)
                        currentScreenSet = selectedScreenSetIncrease()
                        genScreen(lcd)
                elif lines[0] == 'key Down':
                    if currentScreen == 0:
                        clearScreen(lcd, screenName)
                        currentScreenSet = selectedScreenSetDecrease()
                        genScreen(lcd)
                elif lines[0] == 'key Right':
                    if not currentScreen + 1 > len(screen_sets[currentScreenSet]) - 1:                    
                        clearScreen(lcd, screenName)
                        currentScreen += 1
                        genScreen(lcd)
                elif lines[0] == 'key Left':
                    if not currentScreen - 1 < 0:
                        clearScreen(lcd, screenName)
                        currentScreen -= 1
                        genScreen(lcd)
                else:
                    print "envent was: '" + lines[0] + "'"

                time.sleep(0.05)

    # LCD Cleanup on exit        
    finally:
        clearScreen(lcd, screen_sets[currentScreenSet][currentScreen])



def genScreen(lcd):
    conf = screen_sets[currentScreenSet][currentScreen]
    screen = lcd.add_screen(conf['name'])
    screen.set_heartbeat(conf['heartbeat'])
    screen.set_duration(conf['duration'])

    # Screen position logic
    if currentScreen == 0:
        #LED Map onf first screen
        if conf['led_labels']:
            handleLedLabels(screen, conf)
        #Draw menu
            set_MENU_label(screen)
            if len(screen_sets) == 1:
                set_MenuRight_label(screen, conf['name'])

            if len(screen_sets) > 1:
                set_MenuUp_label(screen, screen_sets[selectedScreenSetIncrease()][0]['name'])
                set_MenuRight_label(screen, conf['name'])
                set_MenuDown_label(screen, screen_sets[selectedScreenSetDecrease()][0]['name'])

    elif currentScreen == len(screen_sets[currentScreenSet]) -1:    
        set_prev_icon(screen, 4)
    else:
        set_next_icon(screen, 4)
        set_prev_icon(screen, 4)  

    return screen


def updateScreenData(lcd):
    try:
        screen_sets[currentScreenSet][currentScreen]['updateFun']()
        time.sleep(0.750)
    except:
        pass

def selectedScreenSetIncrease():
    if currentScreenSet + 1 > len(screen_sets) - 1:
        return 0
    else:
        return currentScreenSet + 1

def selectedScreenSetDecrease():
    if currentScreenSet - 1 < 0:
        return len(screen_sets) - 1
    else:
        return currentScreenSet - 1

def clearScreen(lcd, screenName):
    lcd.del_screen(screenName)


def handleLedLabels(screen, screenConfDict):
    for x in range(0,4):
        if screenConfDict['led_labels'][x] != None:
            if x == 0:
                set_LED1_label(screen, screenConfDict['led_labels'][x])
            if x == 1:
                set_LED2_label(screen, screenConfDict['led_labels'][x])
            if x == 2:
                set_LED3_label(screen, screenConfDict['led_labels'][x])
            if x == 3:
                set_LED4_label(screen, screenConfDict['led_labels'][x])                                    

def set_LED1_label(screen, labeltext):
    text = labeltext[:3]
    screen.add_icon_widget("LED1arrow", 1, 1, "SELECTOR_AT_RIGHT")
    put_text(screen, "LED1_label_widget", text, 2, 1)

def set_LED2_label(screen, labeltext):
    text = labeltext[:3]    
    screen.add_icon_widget("LED2arrow", 1, 2, "SELECTOR_AT_RIGHT")    
    put_text(screen, "LED2_label_widget", text, 2, 2)

def set_LED3_label(screen, labeltext):
    text = labeltext[:3]    
    screen.add_icon_widget("LED3arrow", 1, 3, "SELECTOR_AT_RIGHT")    
    put_text(screen, "LED3_label_widget", text, 2, 3)

def set_LED4_label(screen, labeltext):
    text = labeltext[:3]    
    screen.add_icon_widget("LED4arrow", 1, 4, "SELECTOR_AT_RIGHT")
    put_text(screen, "LED4_label_widget", text, 2, 4)

def set_MENU_label(screen):
    screen.add_icon_widget("menu_icon_widget_1", 13, 1, "BLOCK_FILLED")
    screen.add_icon_widget("menu_icon_widget_2", 14, 1, "BLOCK_FILLED")    
    put_text(screen, "menu_label_widget", "MENU", 15, 1)
    screen.add_icon_widget("menu_icon_widget_3", 19, 1, "BLOCK_FILLED")
    screen.add_icon_widget("menu_icon_widget_4", 20, 1, "BLOCK_FILLED")

def set_MenuUp_label(screen, labeltext):
    text = labeltext[:7]    
    screen.add_icon_widget("menuup_arrow", 20, 2, "ARROW_UP")
    put_text(screen, "menuup_text", text, 13, 2)

def set_MenuRight_label(screen, labeltext):
    text = labeltext[:7]    
    screen.add_icon_widget("menuright_arrow", 20, 3, "ARROW_RIGHT")
    put_text(screen, "menuright_text", text, 13, 3)

def set_MenuDown_label(screen, labeltext):
    text = labeltext[:7]    
    screen.add_icon_widget("menudown_arrow", 20, 4, "ARROW_DOWN")
    put_text(screen, "menudown_text", text, 13, 4)    


def set_next_icon(screen, ypos):
    screen.add_icon_widget("next_arrow", 20, ypos, "ARROW_RIGHT")

def set_prev_icon(screen, ypos):
    screen.add_icon_widget("prev_arrow", 1, ypos, "ARROW_LEFT")

def set_up_icon(screen, ypos):
    screen.add_icon_widget("up_arrow", 20, ypos, "ARROW_UP")

def set_down_icon(screen, ypos):
    screen.add_icon_widget("down_arrow", 20, ypos, "ARROW_DOWN")

def put_text(screen, widgetname, text, posx, posy):
    screen.add_string_widget(widgetname, text, posx, posy)    

# Run
if __name__ == "__main__":
    main()
