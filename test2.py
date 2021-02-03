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
        print(type_, code, state)
        if type_ == 'Absolute':
            if code == 'ABS_HAT0Y':
                if state == -1:
                    cmd = "$J=G91 F10000 Y25"
                    self.client.publish("grblesp32/command", cmd)
                elif state == 1:
                    cmd = "$J=G91 F10000 Y-25"
                    self.client.publish("grblesp32/command", cmd)
            if code == 'ABS_HAT0X':
                if state == -1:
                    cmd = "$J=G91 F10000 X-25"
                    self.client.publish("grblesp32/command", cmd)
                elif state == 1:
                    cmd = "$J=G91 F10000 X25"
                    self.client.publish("grblesp32/command", cmd)
        if type_ == 'Key':
            if code == 'BTN_WEST' and state == 1:
                    cmd = "$J=G91 F10000 Z-0.1"
                    self.client.publish("grblesp32/command", cmd)
            if code == 'BTN_SOUTH' and state == 1:
                    cmd = "$J=G91 F10000 Z0.1"
                    self.client.publish("grblesp32/command", cmd)
            # if code == 'ABS_Y':
            #     cmd = "$J=G91 G21 F1000 X100"
            #     self.client.publish("grblesp32/command", float(state))
            # elif code == 'ABS_RY':
            #     self.client.publish("robitt/control/right_setpoint", float(state))
        if type_ == 'Key':
            if code == 'BTN_EAST':
                self.app.quit()


if __name__ == "__main__":
    import sys
    app = QtCore.QCoreApplication(sys.argv)
    tui = Tui(app)
    sys.exit(app.exec_())
