import Adafruit_DHT as dht
from lcdproc.server import Server
from time import sleep

# Instantiate LCDProc
lcd = Server(debug=False)
lcd.start_session()

# Add screen for temperature graph
screenG = lcd.add_screen("TempGraphScreen")
screenG.set_heartbeat("off")
screenG.set_duration(3)

# Get screen widths
w = lcd.get_server_info()['screen_width']
cw = lcd.get_server_info()['cell_width']
maxLength = (w * cw)-(2 * cw)

# Add temperature ticks and scale to display
temp_range=[60, 70, 80, 90, 100]
tick_spacing = (w - 12) / 4
ticks = ""
for item in temp_range:
    ticks = ticks + str(item) + " " * tick_spacing
ticks_widget = screenG.add_string_widget("Ticks1", text=ticks, x=1, y=2)

# Add brackets to frame graph
bracket_widgetL = screenG.add_string_widget("BracketL", text="[", x=1, y=1)
bracket_widgetR = screenG.add_string_widget("BracketR", text="]", x=w, y=1)

# Add horizontal bar graph
hbar_widget = screenG.add_hbar_widget("HBarWidget", x=2, y=1, length=maxLength)

try:
    while True:
        h,t = dht.read_retry(dht.DHT22, 4)
        # Confirm valid readings
        if isinstance(h, float) and isinstance(t, float):
            # Convert Celsius to Fahrenheit
            t = (t * 1.8) + 32.0
            print 'Temp={0:0.1f}*F  Humidity={1:0.1f}%'.format(t, h)
            if (t < 60):
                # Temperature out of range low
                hbar_widget.set_length(0)
            elif (t > 100):
                # Temperature out of range high
                hbar_widget.set_length(maxLength)
            else:
                # Scale temperature and update graph
                hbar_widget.set_length(maxLength * (t - 60) / 40)
        else:
            print('Bad reading!')
        sleep(6)
    
finally:     # clean up on exit
    lcd.del_screen(screenG.ref)

