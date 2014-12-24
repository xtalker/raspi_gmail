# Gmail checker include
import os

#VFD_CLR_TIMEOUT = 30

global clrTimer

# Ping an address waiting 'wait' for a response, return boolean response
def pinger(address, wait):

    response = os.system("ping -c 1 -q -W " + str(wait) + " " + address + " > /dev/null 2>&1")
    # 256 = no response, 0 = responded

    #print "Pinger: Response: " + str(response) 

    if response == 0:
        return True
    else:
        return False
