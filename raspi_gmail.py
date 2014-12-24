#!/usr/bin/env python
# Gmail checker, update GPIO leds,display on serial VF Display
# 2/15/13 - Bob S.
# 2/25/13 - Added subject awareness, gmail auth file, flush stdout
# 12/3/14 - Added suport for wireless moteino gateway and ISY 

# Python setup
# sudo apt-get install python-pip
# sudo pip install feedparser
 
import RPi.GPIO as GPIO, feedparser, time, datetime, serial, sys, os, pty
import ISY
import urllib2
from Resetable_timer import TimerReset
from Resetable_timer import vfdClear
from Resetable_timer import vfdOut
import gmail_vfd_include; # Support methods
import gmail_vfd_auth; # Gmail credentials
import re; #regexp

# Constants
DEBUG = 1

NEWMAIL_OFFSET = 0        # If your unread count never goes to zero, set this
MAIL_CHECK_FREQ = 60
GREEN_LED = 9
RED_LED = 4
YELLOW_LED = 22
YELLOW2_LED = 10
BUZZER = 8
BRAVIATV = '192.168.0.3'

# Setup GPIO 
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# List of GPIO numbers for leds, buzzer
LedSeq = [4,17,22,10,9,11,8]

# Set up the GPIO pins as outputs and set False
print "Setup LED an buzzer outputs"
for x in range(7):
  GPIO.setup(LedSeq[x], GPIO.OUT)
  GPIO.output(LedSeq[x], False)     

# Open serial ports
try:
  vfdPort = serial.Serial("/dev/ttyUSB1", 19200, timeout=0.5)
except serial.SerialException:
  print "ERROR: Couldn't open VFD serial port"
  # This will keep program from crashing if serial port doesnt open
  vfdPort = serial.Serial("/dev/tty1", 19200, timeout=0.5)

try:
  wgPort = serial.Serial("/dev/ttyUSB0", 115200, timeout=0.5)
except serial.SerialException:
  print "ERROR: Couldn't open Gateway serial port"
  # This will keep program from crashing if serial port doesnt open
  wgPort = serial.Serial("/dev/tty0", 115200, timeout=0.5)

print "VFD Port name: " + vfdPort.name    
print "WG  Port name: " + wgPort.name    

# Open connection to ISY
myisy = ISY.Isy(addr="192.168.0.10", eventupdates=0)
# Init the ISY var
myisy.var_set_value('Gmail', 0)

# Init vfd clear timer
gmail_vfd_include.clrTimer = TimerReset(1, vfdClear, args=[vfdPort])

# Create http basic auth handler
auth_handler = urllib2.HTTPBasicAuthHandler()
auth_handler.add_password('New mail feed', 'https://mail.google.com/',
                          gmail_vfd_auth.USERNAME, gmail_vfd_auth.PASSWORD)
t = time.time()
ts = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
print "Starting at: ",ts 

lastCnt = 0
newmails = 0
last_tv_state = False

while True:
  t = time.time()
  ts = datetime.datetime.fromtimestamp(t).strftime('%m/%d-%H:%M')
  #print ts, "Init-New: ", newmails, " Last: ", lastCnt

  GPIO.output(YELLOW2_LED, True)
  try:
    # Open url using the auth handler
    opener = urllib2.build_opener(auth_handler)
    feed_file = opener.open('https://mail.google.com/mail/feed/atom/')
  except Exception:
    print ts + ": URL Open Exception!"
    time.sleep(5)

  try:
    # Parse feed using feedparser
    emails = feedparser.parse(feed_file)
    newmails = int(emails.feed.fullcount)
  except Exception:
    print ts + ": Feed Parse Exception!"
    time.sleep(5)
  GPIO.output(YELLOW2_LED, False)

  if newmails > NEWMAIL_OFFSET:          
    if newmails > lastCnt:
      GPIO.output(BUZZER, True)
      time.sleep(0.1)
      GPIO.output(BUZZER, False)
      print ts, ": You have", newmails, "new emails! Last: ", lastCnt
      lastCnt = newmails                
      GPIO.output(GREEN_LED, True)
      GPIO.output(RED_LED, False)
      cnt = 1

      # Print only the latest unread message, not all unread messages      
      #for entry in emails.entries:
      entry = emails.entries[0]
      # Write leading spaces so text starts on right before first entry
      if cnt == 1:
        vfdPort.write(" " * 25)          

      vfdOut (vfdPort, "Subj: " + entry.title, 30)

      # # Write some spaces between entries
      # if (cnt > 0) and (cnt < len(emails.entries)):
      #   vfdPort.write(" " * 5)                    
      # # Write trailing spaces so text scrolls all the way to left after last
      # #elif cnt == len(emails.entries):
      # else:
      #   vfdPort.write(" " * 25)
      # cnt += 1

  else:
    GPIO.output(GREEN_LED, False)
    GPIO.output(RED_LED, True)

  if newmails == 0:
    lastCnt = 0

  for t in range(1, MAIL_CHECK_FREQ / 2):
    GPIO.output(YELLOW_LED, True) 
    time.sleep(1)
    GPIO.output(YELLOW_LED, False)
    #time.sleep(1)

    # Check for message from wireless gateway
    line = wgPort.readline()
    if len(line) >= 2:
      # See if it is a motion detected message
      if re.search('MOTION', line):
        vfdOut (vfdPort, str(unichr(0x0c)) + ts + " Motion!", 5)
        myisy.var_set_value('Gmail', 100)
        myisy.var_set_value('Gmail', 0)

    # Check if the TV changes state, update an ISY var if it does
    new_tv_state = gmail_vfd_include.pinger(BRAVIATV, 1)
    if new_tv_state != last_tv_state:
      if new_tv_state:
        myisy.var_set_value('TVstate', 1)
        vfdOut (vfdPort, ts + " TV On", 5)
      else:
        myisy.var_set_value('TVstate', 0)
        vfdOut (vfdPort, ts + " TV Off", 5)
      last_tv_state = new_tv_state

    sys.stdout.flush()
    
