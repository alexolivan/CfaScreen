import Adafruit_DHT as dht
from lcdproc.server import Server
from time import sleep

# Instantiate LCDProc
lcd = Server(debug=False)
lcd.start_session()

# Add screens for temperature and humidity
screenT = lcd.add_screen("TemperatureScreen")
screenT.set_heartbeat("off")
screenT.set_duration(3)
screenH = lcd.add_screen("HumidityScreen")
screenH.set_heartbeat("off")
screenH.set_duration(3)

# Add big digits for both screens
digitsT = [screenT.add_number_widget("DigitT1Widget", x=4, value=10),
           screenT.add_number_widget("DigitT2Widget", x=7, value=10),
           screenT.add_number_widget("DigitT3Widget", x=10, value=10),
           screenT.add_number_widget("DigitT4Widget", x=15, value=10)]
digitsH = [screenH.add_number_widget("DigitH1Widget", x=4, value=10),
           screenH.add_number_widget("DigitH2Widget", x=7, value=10),
           screenH.add_number_widget("DigitH3Widget", x=10, value=10),
           screenH.add_number_widget("DigitH4Widget", x=15, value=10)]
# Add decimal points for both screens
dpT = screenT.add_string_widget("DecimalTWidget", text="o", x=13, y=4)
dpH = screenH.add_string_widget("DecimalHWidget", text="o", x=13, y=4)
# Add minus signs for temperature screen (default off = space)
minus_widget1 = screenT.add_string_widget("Minus1", text="_", x=1, y=2)
minus_widget2 = screenT.add_string_widget("Minus2", text="_", x=2, y=2)
# Add degree symbol to temperature screen
degree_widget1 = screenT.add_string_widget("Degree1", text="(", x=18, y=1)
degree_widget2 = screenT.add_string_widget("Degree2", text=")", x=19, y=1)
# Add percent symbol to humidity screen
percent_widget1 = screenH.add_string_widget("Percent1", text="o", x=18, y=1)
percent_widget2 = screenH.add_string_widget("Percent2", text="o", x=20, y=2)
percent_widget3 = screenH.add_string_widget("Percent3", text="/", x=20, y=1)
percent_widget4 = screenH.add_string_widget("Percent4", text="/", x=18, y=2)

try:
    while True:
		# Poll DHT22 sensor
        h,t = dht.read_retry(dht.DHT22, 4)
        # Confirm valid readings
        if isinstance(h, float) and isinstance(t, float):
            # Convert Celsius to Fahrenheit
            t = (t * 1.8) + 32.0
            print 'Temp={0:0.1f}*F  Humidity={1:0.1f}%'.format(t, h)

            # Check for minus temperature
            if t < 0:
                # Display minus symbol
                minus_widget1.set_text('_')
                minus_widget2.set_text('_')
                t = abs(t)
            else:
                # Hide minus symbol
                minus_widget1.set_text(' ')
                minus_widget2.set_text(' ')
                
            # Convert readings to digit lists
            # Format to 1 decimal, zero padded to 4 digits)
            valueT = list("{:05.1f}".format(t))
            valueH = list("{:05.1f}".format(h))
            # Remove decimal points from value lists
            valueT.pop(3)
            valueH.pop(3)
            # Set temperature and humidity digits
            for i in range(4):
                digitsT[i].set_value(int(valueT[i]))
                digitsH[i].set_value(int(valueH[i]))
        else:
            print('Bad reading!')
        sleep(6)
    
finally:     # clean up on exit
    lcd.del_screen(screenT.ref)
    lcd.del_screen(screenH.ref)
