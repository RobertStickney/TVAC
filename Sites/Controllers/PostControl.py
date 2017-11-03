from Collections.ProfileInstance import ProfileInstance
from Collections.HardwareStatusInstance import HardwareStatusInstance
from ThreadControls.ThreadCollectionInstance import ThreadCollectionInstance

from Logging.Logging import Logging


class PostControl:

    def loadProfile(self,data):
        profileInstance = ProfileInstance.getInstance()
        return profileInstance.zoneProfiles.loadProfile(data["profile_name"])

    def saveProfile(self, data):
        profileInstance = ProfileInstance.getInstance()
        return profileInstance.zoneProfiles.saveProfile(data)

    def runSingleProfile(self, data):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.runSingleThread(data)
        return "{'result':'success'}"

    def pauseSingleThread(self, data):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.pause(data)
        return "{'result':'success'}"

    def removePauseSingleThread(self, data):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.removePause(data)
        return "{'result':'success'}"

    def holdSingleThread(self, data):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.holdThread(data)
        return "{'result':'success'}"

    def releaseHoldSingleThread(self, data):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.releaseHoldThread(data)
        return "{'result':'success'}"

    def abortSingleThread(self, data):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.abortThread(data)
        return "{'result':'success'}"

    def calculateRamp(self, data):
        threadInstance = ThreadCollectionInstance.getInstance()
        threadInstance.threadCollection.calculateRamp(data)
        return "{'result':'success'}"

    def SendHwCmd(self, data):
        if type(data) is not list:
            return '{"result":"Needs a json dictionary of a cmds."}'
        hw = HardwareStatusInstance.getInstance()
        Logging.debugPrint(3,"POST: SendHwCmd '%s'" % data)
        if data[0] == "Shi_MCC_Cmds":  # ['cmd', arg, arg,... arg]
            hw.Shi_MCC_Cmds.append(data[1:])
        elif data[0] == "Shi_Compressor_Cmds":  # 'cmd'
            hw.Shi_Compressor_Cmds.append(data[1])
        elif data[0] == "TdkLambda_Cmds":  # ['cmd', arg, arg,... arg]
            hw.TdkLambda_Cmds.append(data[1:])
        else:
            return '{"result":"Unknown Hardware Target."}'
        return '{"result":"success"}'

    def setPC104_Digital(self, data):
        pins = HardwareStatusInstance.getInstance().PC_104
        Logging.debugPrint(3,"POST: setPC104_Digital '%s'" % data)
        pins.digital_out.update(data)
        Logging.debugPrint(4,"Digital out data: '%s'" % pins.digital_out.getJson())
        return "{'result':'success'}"

    def setPC104_Analog(self, data):
        pins = HardwareStatusInstance.getInstance().PC_104
        pins.analog_out.update(data)
        return "{'result':'success'}"

    def heatUpShroud(self, data):
        dutyCycle = float(data['dutyCycle'])
        tdKs = HardwareStatusInstance.getInstance().TdkLambda_PS
        if not ProfileInstance.getInstance().activeProfile:
            if dutyCycle == 0:
                if tdKs.get_shroud_left().output_enable or tdKs.get_shroud_right().output_enable:
                    HardwareStatusInstance.getInstance().TdkLambda_Cmds.append(['Disable Shroud Output'])
                    return "{'result':'Disabled Shroud'}"
                else:
                    return "{'result':'Shroud Off'}"
            else:
                if not (tdKs.get_shroud_left().output_enable and tdKs.get_shroud_right().output_enable):
                    HardwareStatusInstance.getInstance().TdkLambda_Cmds.append(['Setup Shroud'])
                    print("Turning on Shroud")
                HardwareStatusInstance.getInstance().TdkLambda_Cmds.append(['Shroud Duty Cycle', dutyCycle])
                return "{'result':'Shroud duty cycle set'}"
        else:
            return "{'result':'Not used in Profile'}"

    def heatUpPlaten(self, data):
        dutyCycle = float(data['dutyCycle'])
        tdKs = HardwareStatusInstance.getInstance().TdkLambda_PS
        tdKs.get_platen_left().output_enable = True
        tdKs.get_platen_right().output_enable = True
        if not ProfileInstance.getInstance().activeProfile:
            if dutyCycle == 0:
                if tdKs.get_platen_left().output_enable or tdKs.get_platen_right().output_enable:
                    HardwareStatusInstance.getInstance().TdkLambda_Cmds.append(['Disable Platen Output'])
                    return "{'result':'Disabled Platen'}"
                else:
                    return "{'result':'Platen Off'}"
            else:
                if not (tdKs.get_platen_left().output_enable and tdKs.get_platen_right().output_enable):
                    HardwareStatusInstance.getInstance().TdkLambda_Cmds.append(['Setup Platen'])
                HardwareStatusInstance.getInstance().TdkLambda_Cmds.append(['Platen Duty Cycle', dutyCycle])
                return "{'result':'Platen duty cycle set'}"
        else:
            return "{'result':'Not used in Profile'}"

