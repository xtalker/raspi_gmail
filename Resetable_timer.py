
# From: http://code.activestate.com/recipes/577407-resettable-timer-class-a-little-enhancement-from-p/

from threading import Thread, Event, Timer
import time
import gmail_vfd_include


# Function to clear the vfd screen
def vfdClear(port):
    #print "vfdClear: Clear display, port: %s" % port.name
    port.write(str(unichr(0x0c)))  # clear (0C)


# Function to send message to VFD
def vfdOut(port, msg, timeout):
    #global clrTimer
    #This avoids UTF decode exceptions when printing
    msg = msg.encode('ascii', 'ignore')
    print "vfdOut: sending: %s" % msg

    # Restart the clear timer if not running, reset if is running
    if gmail_vfd_include.clrTimer.is_alive():
        #print "vfdOut: Timer is running, resetting..."
        gmail_vfd_include.clrTimer.reset()
    else:
        #print "vfdOut: Timer not running, Restarting..."
        #gmail_vfd_include.clrTimer = TimerReset(gmail_vfd_include.VFD_CLR_TIMEOUT, vfdClear, args=[port])
        gmail_vfd_include.clrTimer = TimerReset(timeout, vfdClear, args=[port])
        gmail_vfd_include.clrTimer.start()

    # Setup vfd
    port.write(str(unichr(0x1f) + unichr(0x03)))  # Horiz scroll mode
    port.write(str(unichr(0x1f) + unichr(0x73) + unichr(0x03)))  # Scroll speed
    port.write(msg + " ")


def TimerReset(*args, **kwargs):
    """ Global function for Timer """
    return _TimerReset(*args, **kwargs)


class _TimerReset(Thread):
    """Call a function after a specified number of seconds:

    t = TimerReset(30.0, f, args=[], kwargs={})
    t.start()
    t.cancel() # stop the timer's action if it's still waiting
    """

    def __init__(self, interval, function, args=[], kwargs={}):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = Event()
        self.resetted = True

    def cancel(self):
        """Stop the timer if it hasn't finished yet"""
        self.finished.set()
        
    def run(self):
        #print "Time: %s - timer running..." % time.asctime()

        while self.resetted:
            #print "Time: %s - timer waiting for timeout in %.2f..." % (time.asctime(), self.interval)
            self.resetted = False
            self.finished.wait(self.interval)

        if not self.finished.isSet():
            self.function(*self.args, **self.kwargs)
        self.finished.set()
        #print "Time: %s - timer finished!" % time.asctime()

    def reset(self, interval=None):
        """ Reset the timer """

        if interval:
            #print "Time: %s - timer resetting to %.2f..." % (time.asctime(), interval)
            self.interval = interval
        #else:
            #print "Time: %s - timer resetting..." % time.asctime()

        self.resetted = True
        self.finished.set()
        self.finished.clear()


