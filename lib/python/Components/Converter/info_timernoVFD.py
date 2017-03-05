from Converter import Converter
from Components.Element import cached
from Poll import Poll
import NavigationInstance
from time import time as time_now

def debugtxt(loque, loque2 = None, inicio = False):
    return
    import os
    if inicio:
        os.system("echo ''>/tmp/infotimer.log")
    os.system("echo '******************************'>>/tmp/infotimer.log")
    os.system('date>>/tmp/infotimer.log')
    os.system("echo '" + str(loque) + "'>>/tmp/infotimer.log")
    if loque2 != None:
        os.system("echo '" + str(loque2) + "'>>/tmp/infotimer.log")
    os.system("echo '******************************'>>/tmp/infotimer.log")


class info_timernoVFD(Poll, Converter, object):

    def __init__(self, argstr):
        Converter.__init__(self, argstr)
        Poll.__init__(self)
        self.poll_interval = 120000
        self.poll_enabled = True
        self.recordings = False
        self.type = 0
        debugtxt('inicio')

    def calcVisibility(self):
        b = self.simostrar()
        if b:
            debugtxt('calcVisibility True')
        else:
            debugtxt('calcVisibility False')
        return b

    def changed(self, what):
        vis = self.calcVisibility()
        if vis:
            debugtxt('changed True')
        else:
            debugtxt('changed False')
        for x in self.downstream_elements:
            debugtxt('changed visible')
            x.visible = vis

    def connectDownstream(self, downstream):
        Converter.connectDownstream(self, downstream)
        downstream.visible = self.calcVisibility()

    def destroy(self):
        debugtxt('destroy')

    def simostrar(self):
        self.recordings = self.source.boolean
        ret = False
        self.poll_interval = 120000
        debugtxt('simostrar')
        if self.recordings:
            ret = False
        else:
            try:
                for timer in NavigationInstance.instance.RecordTimer.timer_list:
                    if timer.state == timer.StatePrepared or timer.begin - time_now() < 50 and timer.begin - time_now() >= 0 and not timer.disabled:
                        self.poll_interval = 5000
                        ret = True
                        debugtxt('simostrar hay')
                        break
                    elif timer.state == timer.StateWaiting and not timer.disabled:
                        self.poll_interval = 30000
                        debugtxt('simostrar hay')
                        ret = True
                        break

            except:
                pass

        return ret
