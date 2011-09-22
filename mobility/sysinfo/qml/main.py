#!/usr/bin/python

import sys
import os

from PySide import QtCore
from PySide import QtGui
from PySide import QtDeclarative
from PySide import QtOpenGL
from QtMobility.SystemInfo import QSystemInfo, QSystemDeviceInfo, QSystemDisplayInfo, QSystemStorageInfo, QSystemNetworkInfo, QSystemScreenSaver


class SystemInfoModel(QtCore.QObject):
    changed = QtCore.Signal()

    def __init__(self):
        super(SystemInfoModel, self).__init__()
        self.systemInfo = QSystemInfo(self)
        self.setupGeneral()
        self.setupDevice()
        self.setupDisplay()

    @QtCore.Property(str, notify=changed)
    def currentLanguage(self):
        return self._currentLanguage

    @QtCore.Property("QStringList", notify=changed)
    def availableLanguages(self):
        return self._availableLanguages

    @QtCore.Property(int, notify=changed)
    def displayBrightness(self):
        return self._displayBrightness

    @QtCore.Property(int, notify=changed)
    def colorDepth(self):
        return self._colorDepth

    @QtCore.Property(str, notify=changed)
    def imei(self):
        return self._imei

    @QtCore.Property(str, notify=changed)
    def imsi(self):
        return self._imsi

    @QtCore.Property(str, notify=changed)
    def manufacturer(self):
        return self._manufacturer

    @QtCore.Property(str, notify=changed)
    def product(self):
        return self._product

    @QtCore.Property(str, notify=changed)
    def model(self):
        return self._model

    @QtCore.Property(str, notify=changed)
    def profile(self):
        return self._profile

    @QtCore.Property(str, notify=changed)
    def inputMethod(self):
        return self._inputMethod

    @QtCore.Property(bool, notify=changed)
    def deviceLock(self):
        return self._deviceLock

    @QtCore.Property(str, notify=changed)
    def simStatus(self):
        return self._simStatus

    @QtCore.Property(bool, notify=changed)
    def bluetoothState(self):
        return self._bluetoothState

    def setupGeneral(self):
        self._currentLanguage = self.systemInfo.currentLanguage()
        self._availableLanguages = self.systemInfo.availableLanguages()
        self.emit(QtCore.SIGNAL('changed()'))

    def setupDevice(self):
        self.deviceInfo = QSystemDeviceInfo(self)
        self._batteryLevel = self.deviceInfo.batteryLevel()
        self.deviceInfo.batteryLevelChanged.connect(self.updateBatteryStatus)
        self.deviceInfo.batteryStatusChanged.connect(self.displayBatteryStatus)
        self.deviceInfo.powerStateChanged.connect(self.updatePowerState)
        self._imei = self.deviceInfo.imei()
        self._imsi = self.deviceInfo.imsi()
        self._manufacturer = self.deviceInfo.manufacturer()
        self._model = self.deviceInfo.model()
        self._product = self.deviceInfo.productName()
        self._deviceLock = self.deviceInfo.isDeviceLocked()

        methods = self.deviceInfo.inputMethodType()
        inputs = []
        if methods & QSystemDeviceInfo.Keys:
            inputs.append("Keys")
        if methods & QSystemDeviceInfo.Keypad:
            inputs.append("Keypad")
        if methods & QSystemDeviceInfo.Keyboard:
            inputs.append("Keyboard")
        if methods & QSystemDeviceInfo.SingleTouch:
            inputs.append("Touch Screen")
        if methods & QSystemDeviceInfo.MultiTouch:
            inputs.append("Multi touch")
        if methods & QSystemDeviceInfo.Mouse:
            inputs.append("Mouse")

        self._inputMethod = " ".join(inputs)
        self.updateSimStatus()
        self.updateProfile()

        self._bluetoothState = self.deviceInfo.currentBluetoothPowerState()
        self.deviceInfo.bluetoothStateChanged.connect(self.updateBluetoothState)
        self.emit(QtCore.SIGNAL('changed()'))

    def setupDisplay(self):
        self.displayInfo = QSystemDisplayInfo()
        self._displayBrightness = self.displayInfo.displayBrightness(0)
        self._colorDepth = self.displayInfo.colorDepth(0)
        self.emit(QtCore.SIGNAL('changed()'))

    def updateBluetoothState(self, on):
        self._bluetoothState = on
        self.changed.emit()

    def updateBatteryStatus(self, status):
        self._batteryLevel = status
        self.emit(QtCore.SIGNAL('changed()'))

    def displayBatteryStatus(self, status):
        pass

    def updatePowerState(self, newState):
        pass

    def updateSimStatus(self):
        if self.deviceInfo:
            status = self.deviceInfo.simStatus()
            if status == QSystemDeviceInfo.SimLocked:
                simstring = "Sim Locked";
            elif status == QSystemDeviceInfo.SimNotAvailable:
                simstring = "Sim not available";
            elif status == QSystemDeviceInfo.SingleSimAvailable:
                simstring = "Single Sim Available";
            elif status == QSystemDeviceInfo.DualSimAvailable:
                simstring = "Dual Sim available";
            else:
                simstring = ""

            self._simStatus = simstring


    def updateProfile(self):
        if self.deviceInfo:
            current = self.deviceInfo.currentProfile()
            if current == QSystemDeviceInfo.UnknownProfile:
                profilestring = "Unknown"
            elif current == QSystemDeviceInfo.SilentProfile:
                profilestring = "Silent"
            elif current == QSystemDeviceInfo.NormalProfile:
                profilestring = "Normal"
            elif current == QSystemDeviceInfo.LoudProfile:
                profilestring = "Loud"
            elif current == QSystemDeviceInfo.VibProfile:
                profilestring = "Vibrate"
            elif current == QSystemDeviceInfo.OfflineProfile:
                profilestring = "Offline";
            elif current == QSystemDeviceInfo.PowersaveProfile:
                profilestring = "Powersave";
            elif current ==  QSystemDeviceInfo.CustomProfile:
                profilestring = "custom";

            self._profile = profilestring

class SystemInfoUI(QtCore.QObject):
    def __init__(self):
        super(SystemInfoUI, self).__init__()
        self.view = QtDeclarative.QDeclarativeView()
        self.rc = self.view.rootContext()

        self.model = SystemInfoModel()
        self.rc.setContextProperty('dataModel', self.model)

        self.view.setSource('main.qml')

        if "-no-fs" in sys.argv:
            self.view.show()
        else:
            self.view.showFullScreen()

        self.systemInfo = QSystemInfo(self)

if __name__ == "__main__":
    app = QtGui.QApplication([])
    ui = SystemInfoUI()
    app.exec_()
