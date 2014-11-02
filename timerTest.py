
from Resetable_timer import TimerReset
from Resetable_timer import vfdClear
from Resetable_timer import vfdOut
import time, serial
import gmail_vfd_config

#VFD_CLR_TIMEOUT = 15
#global clrTimer

vfdPort = serial.Serial("/dev/ttyUSB0", 19200, timeout=0.5)
print "Port name: " + vfdPort.name    

gmail_vfd_config.clrTimer = TimerReset(1, vfdClear, args=[vfdPort])
    
print "Starting..."
time.sleep (2)

vfdOut (vfdPort, "This is test1")
time.sleep (5)
vfdOut (vfdPort, "123456789012345678901234")
time.sleep (35)
vfdOut (vfdPort, "This is test2")

#vfdPort.close()
