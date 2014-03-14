#!/usr/bin/env python
# Gmail checker, update GPIO leds,display on serial VF Display
# 2/15/14 - Bob S.
# 2/25/13 - Added subject awareness, gmail auth file, flush stdout

# Python setup
# sudo apt-get install python-pip
# sudo pip install feedparser
 
import RPi.GPIO as GPIO, feedparser, time, datetime, serial, sys
import urllib2
from Resetable_timer import TimerReset
from Resetable_timer import vfdClear
from Resetable_timer import vfdOut
import gmail_vfd_config; # Global constants
import gmail_vfd_auth; # Gmail credentials

# Constants
DEBUG = 1

NEWMAIL_OFFSET = 0        # If your unread count never goes to zero, set this
MAIL_CHECK_FREQ = 60
GREEN_LED = 9
RED_LED = 4
YELLOW_LED = 22
YELLOW2_LED = 10
BUZZER = 8

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

# Open serial port
vfdPort = serial.Serial("/dev/ttyUSB0", 19200, timeout=0.5)
print "Port name: " + vfdPort.name    

# Init vfd clear timer
gmail_vfd_config.clrTimer = TimerReset(1, vfdClear, args=[vfdPort])

# Create http basic auth handler
auth_handler = urllib2.HTTPBasicAuthHandler()
auth_handler.add_password('New mail feed', 'https://mail.google.com/',
                          gmail_vfd_auth.USERNAME, gmail_vfd_auth.PASSWORD)
t = time.time()
ts = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
print "Starting at: ",ts 

lastCnt = 0
newmails = 0

while True:
  t = time.time()
  ts = datetime.datetime.fromtimestamp(t).strftime('%H:%M')
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

      for entry in emails.entries:
        #t = time.time()
        #ts = datetime.datetime.fromtimestamp(t).strftime('%H:%M')
        #vfdOut (vfdPort, "New: " + str(newmails) + " at " + ts)
        vfdOut (vfdPort, "Subject: " + entry.title)

      # Write trailing spaces so text scrolls all the way to left
      vfdPort.write(" " * 25)

  else:
    GPIO.output(GREEN_LED, False)
    GPIO.output(RED_LED, True)

  if newmails == 0:
    lastCnt = 0

  for t in range(1, MAIL_CHECK_FREQ / 2):
    GPIO.output(YELLOW_LED, True) 
    time.sleep(1)
    GPIO.output(YELLOW_LED, False)
    time.sleep(1)

    sys.stdout.flush()
    
