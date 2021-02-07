#!/usr/bin/python3
import math
from PyQt5 import QtCore
import sys
import time
sys.path.insert(0, "y:\\home\\dek\\src\\gamepad_qobject\\gamepad_qobject")
from gamepad_qobject import Gamepad
sys.path.insert(0, "y:\\home\\dek\\src\\mqtt_qobject\\mqtt_qobject")
from mqtt_qobject import MqttClient


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

        self.client = MqttClient(self)
        self.client.hostname = "postscope.local"
        self.client.connectToHost()

        self.lastTime = time.time()
        self.lastValue = 0

    @QtCore.pyqtSlot(str, str, int)
    def on_gamepadSignal(self, type_, code, state):
        if type_ == 'Sync':
            return
        elif type_ == 'Key':
            if code == 'BTN_TL' and state == 1:
                    cmd = "$J=G91 F10000 Z-0.05"
                    self.client.publish("grblesp32/command", cmd)
            elif code == 'BTN_TR' and state == 1:
                    cmd = "$J=G91 F10000 Z0.05"
                    self.client.publish("grblesp32/command", cmd)
            elif code == 'BTN_SELECT' and state == 1:
                    cmd = "M5"
                    self.client.publish("grblesp32/command", cmd)
            elif code == 'BTN_START' and state == 1:
                    cmd = "M3 S1024"
                    self.client.publish("grblesp32/command", cmd)
            print(type_, code, state)
        elif type_ == 'Absolute':
            if code == 'ABS_THROTTLE':
                t = time.time()
                value =  (1024 - (state * 4))
                if abs(value - self.lastValue) > 5 or t - self.lastTime > 1000:
                    cmd = "M3 S%d" % value
                    self.client.publish("grblesp32/command", cmd)
                    self.lastTime = t
                    self.lastValue = value
            elif code in ('ABS_HAT0X', 'ABS_HAT0Y'):
                if state in (-1, 1):
                    move = -15 * state
                    dir_ = 'X'
                    if code == 'ABS_HAT0X':
                        dir_ = 'Y'
                    cmd = "$J=G91 F10000 %s%d" % (dir_, move)
                    self.client.publish("grblesp32/command", cmd)
                
            elif code == 'ABS_RZ':
                    return
            # elif code == 'ABS_X':
            #     f = state - 512
            #     if abs(f) > 20:
            #         if f < 0:
            #             step = -50
            #         else:
            #             step = 50
            #         cmd = "$J=G91 F%d X%d" % (int(abs(f)*25), step)
            #         print(cmd)
            #         self.client.publish("grblesp32/command", cmd)
            #     else:
            #         print("cancel")
            #         self.client.publish("grblesp32/cancel", "")
            # elif code == 'ABS_Y':
            #     f = -state + 512
            #     if abs(f) > 20:
            #         if f < 0:
            #             step = -50
            #         else:
            #             step = 50
            #         cmd = "$J=G91 F%d Y%d" % (int(abs(f)*25), step)
            #         self.client.publish("grblesp32/command", cmd)
            #     else:
            #         self.client.publish("grblesp32/cancel", "")

if __name__ == "__main__":
    import sys
    app = QtCore.QCoreApplication(sys.argv)
    tui = Tui(app)
    sys.exit(app.exec_())
