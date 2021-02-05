import math
from PyQt5 import QtCore
from gamepad_qobject import Gamepad
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
        self.client.hostname = "localhost"
        self.client.connectToHost()


    @QtCore.pyqtSlot(str, str, int)
    def on_gamepadSignal(self, type_, code, state):
        if type_ == 'Sync':
            return
        elif type_ == 'Key':
            if code == 'BTN_TOP2' and state == 0:
                    cmd = "$J=G91 F10000 Z-0.1"
                    self.client.publish("grblesp32/command", cmd)
                    return
            elif code == 'BTN_PINKIE' and state == 0:
                    cmd = "$J=G91 F10000 Z0.1"
                    self.client.publish("grblesp32/command", cmd)
                    return
            else:
                print(type_, code, state)
        elif type_ == 'Absolute':
            if code == 'ABS_THROTTLE':
                cmd = "M3 S%d" % (1024 - (state * 4))
                self.client.publish("grblesp32/command", cmd)
                return
            elif code == 'ABS_HAT0X':
                if state == -1:
                    cmd = "$J=G91 F10000 X-25"
                    self.client.publish("grblesp32/command", cmd)
                    return
                elif state == 1:
                    cmd = "$J=G91 F10000 X25"
                    self.client.publish("grblesp32/command", cmd)
                    return
            elif code == 'ABS_HAT0Y':
                if state == -1:
                    cmd = "$J=G91 F10000 Y25"
                    self.client.publish("grblesp32/command", cmd)
                    return
                elif state == 1:
                    cmd = "$J=G91 F10000 Y-25"
                    self.client.publish("grblesp32/command", cmd)
                    return

if __name__ == "__main__":
    import sys
    app = QtCore.QCoreApplication(sys.argv)
    tui = Tui(app)
    sys.exit(app.exec_())
