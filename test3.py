import math
from PyQt5 import QtCore
from gamepad_qobject import Gamepad
from qt_grbl import grblesp32_serial_qobject

class Tui(QtCore.QObject):

    def __init__(self, app):
        super(Tui, self).__init__()

        self.app = app
        self.gamepad_thread = QtCore.QThread()
        self.gamepad = Gamepad()
        self.gamepad.messageSignal.connect(self.on_gamepadSignal)
        self.gamepad.moveToThread(self.gamepad_thread)
        self.gamepad_thread.started.connect(self.gamepad.loop)
        self.gamepad_thread.start()


        self.grblesp32 = grblesp32_serial_qobject.GRBLESP32Client()
        self.grblesp32.messageSignal.connect(self.on_ramps_read)
        self.grblesp32.statusSignal.connect(self.on_ramps_status)
        self.grblesp32.stateSignal.connect(self.on_ramps_state)
        
    @QtCore.pyqtSlot(str, str, int)
    def on_gamepadSignal(self, type_, code, state):
        if type_ == 'Sync':
            return
        if type_ == 'Key':
            if code == 'BTN_TOP2' and state == 0:
                    cmd = "$J=G91 F10000 Z-0.1"
                    self.grblesp32.send_line(cmd)
                    return
            elif code == 'BTN_PINKIE' and state == 0:
                    cmd = "$J=G91 F10000 Z0.1"
                    self.grblesp32.send_line(cmd)
                    return
            # elif code == 'BTN_TR' and state == 0:
            #         cmd = "M5"
            #         self.grblesp32.send_line(cmd)
            #         return
            # elif code == 'BTN_TL' and state == 0:
            #         cmd = "M3 S1024"
            #         self.grblesp32.send_line(cmd)
            #         return
            #elif code == 'BTN_EAST':
            #    self.app.quit()
            else:
                print(type_, code, state)
        elif type_ == 'Absolute':
            if code == 'ABS_THROTTLE':
                cmd = "M3 S%d" % (1024 - (state * 4))
                self.grblesp32.send_line(cmd)
                return
            elif code == 'ABS_HAT0X':
                if state == -1:
                    cmd = "$J=G91 F10000 X-25"
                    self.grblesp32.send_line(cmd)
                    return
                elif state == 1:
                    cmd = "$J=G91 F10000 X25"
                    self.grblesp32.send_line(cmd)
                    return
            
                    
            elif code == 'ABS_HAT0Y':
                if state == -1:
                    cmd = "$J=G91 F10000 Y25"
                    self.grblesp32.send_line(cmd)
                    return
                elif state == 1:
                    cmd = "$J=G91 F10000 Y-25"
                    self.grblesp32.send_line(cmd)
                    return
    def on_ramps_read(self, data):
        print("grblesp32 serial read:", data)

    def on_ramps_status(self, data):
        print("grblesp32 serial status:", data)

    def on_ramps_state(self, state):
        print("grblesp32 serial state:", state)


if __name__ == "__main__":
    import sys
    app = QtCore.QCoreApplication(sys.argv)
    tui = Tui(app)
    sys.exit(app.exec_())
