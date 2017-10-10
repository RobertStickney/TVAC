#!/usr/bin/env python3.5
from threading import Thread
import time
import datetime
import os
import sys

if __name__ == '__main__':
    sys.path.insert(0, os.getcwd())

from Collections.ProfileInstance import ProfileInstance
from Collections.HardwareStatusInstance import HardwareStatusInstance
from Tdk_lamda.Tdk_lamda_Genesys import Tdk_lambda_Genesys

from Logging.MySql import MySQlConnect
from Logging.Logging import Logging


class TdkLambdaControlStub(Thread):
    def __init__(self, parent=None, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs
        self.parent = parent

        self.pwr_supply = Tdk_lambda_Genesys()
        self.zoneProfiles = ProfileInstance.getInstance().zoneProfiles
        self.hw = HardwareStatusInstance.getInstance()
        self.ps_read_peroid = 0.5  # 0.5s loop period

    # def logVoltagesData(self):
    #     coloums = "( profile_I_ID, guage, pressure, time )"
    #     values  = "( \"{}\",{},{},\"{}\" ),\n".format(self.zoneProfiles.profileUUID,
    #                                            self.gauges.get_cryopump_address(),
    #                                            self.gauges.get_cryopump_pressure(),
    #                                            datetime.datetime.fromtimestamp(time.time()))
    #     values += "( \"{}\",{},{},\"{}\" ),\n".format(self.zoneProfiles.profileUUID,
    #                                            self.gauges.get_chamber_address(),
    #                                            self.gauges.get_chamber_pressure(),
    #                                            datetime.datetime.fromtimestamp(time.time()))
    #     values += "( \"{}\",{},{},\"{}\" )".format(self.zoneProfiles.profileUUID,
    #                                         self.gauges.get_roughpump_address(),
    #                                         self.gauges.get_roughpump_pressure(),
    #                                         datetime.datetime.fromtimestamp(time.time()))
    #     sql = "INSERT INTO tvac.Pressure {} VALUES {};".format(coloums, values)
    #     # print(sql)
    #     mysql = MySQlConnect()
    #     try:
    #         mysql.cur.execute(sql)
    #         mysql.conn.commit()
    #     except Exception as e:
    #         raise e
    #         #return e

    def run(self):
        '''
        '''
        # used for testing
        first = True
        while True:
            # While true to restart the thread if it errors out
            try:
                # Thread "Start up" stuff goes here
                Logging.logEvent("Event", "Thread Start",
                                {"thread": "TDK Lambda Genesys Control Stub",
                                 "ProfileInstance": ProfileInstance.getInstance()})
                Logging.logEvent("Debug", "Status Update",
                                {"message": "TDK Lambda Genesys Control Stub Thread",
                                 "level": 2})

                userName = os.getlogin()
                if "root" in userName:
                    update_power_supplies = [{'addr': self.hw.TdkLambda_PS.get_platen_left_addr()},
                                             {'addr': self.hw.TdkLambda_PS.get_platen_right_addr()},
                                             {'addr': self.hw.TdkLambda_PS.get_shroud_left_addr()},
                                             {'addr': self.hw.TdkLambda_PS.get_shroud_right_addr()}]
                    for ps in update_power_supplies:
                        self.pwr_supply.set_addr(ps['addr'])
                        ps.update(self.pwr_supply.get_idn())
                        ps.update(self.pwr_supply.get_rev())
                        ps.update(self.pwr_supply.get_sn())
                        ps.update(self.pwr_supply.get_date())
                        ps.update(self.pwr_supply.get_ast())
                        ps.update(self.pwr_supply.get_out())
                        ps.update(self.pwr_supply.get_mode())
                    self.hw.TdkLambda_PS.update(update_power_supplies)
                next_status_read_time = time.time()
                while True:
                    next_status_read_time += self.ps_read_peroid
                    if "root" in userName:
                        try:
                            update_power_supplies = [{'addr': self.hw.TdkLambda_PS.get_platen_left_addr()},
                                                     {'addr': self.hw.TdkLambda_PS.get_platen_right_addr()},
                                                     {'addr': self.hw.TdkLambda_PS.get_shroud_left_addr()},
                                                     {'addr': self.hw.TdkLambda_PS.get_shroud_right_addr()}]
                            for ps in update_power_supplies:
                                self.pwr_supply.set_addr(ps['addr'])
                                if not self.hw.OperationalVacuum and self.hw.TdkLambda_PS.get_val(ps['addr'], 'output enable'):
                                    self.pwr_supply.set_out_off()
                                ps.update(self.pwr_supply.get_status())
                                ps.update(self.pwr_supply.get_out())
                                ps.update(self.pwr_supply.get_mode())
                            self.hw.TdkLambda_PS.update(update_power_supplies)
                            # Logging.logEvent("Debug", "Status Update",
                            #                  {"message": "Reading and writing with PfeifferGaugeControlStub.\nCryopump: {:f}; Chamber: {:f}; RoughPump: {:f}\n".format(
                            #                      self.gauges.get_cryopump_pressure(),
                            #                      self.gauges.get_chamber_pressure(),
                            #                      self.gauges.get_roughpump_pressure()
                            #                  ),
                            #                   "level": 4})
                            # cmd[0] = location; cmd[1] = value; cmd[2] = Volts or Current
                            while len(self.hw.TdkLambda_Cmds):
                                cmd = self.hw.TdkLambda_Cmds.pop()
                                if 'Set Platen Left' == cmd[0]:
                                    if cmd[2] == 'V'
                                        self.run_set_cmd(self.hw.TdkLambda_PS.get_platen_left_addr(),
                                                         self.pwr_supply.set_pv, cmd[1])
                                    if cmd[2] == 'C'
                                        self.run_set_cmd(self.hw.TdkLambda_PS.get_platen_left_addr(),
                                                         self.pwr_supply.set_pc, cmd[1])
                                elif 'Set Platen Right' == cmd[0]:
                                    if cmd[2] == 'V'
                                        self.run_set_cmd(self.hw.TdkLambda_PS.get_platen_right_addr(),
                                                         self.pwr_supply.set_pv, cmd[1])
                                    if cmd[2] == 'C'
                                        self.run_set_cmd(self.hw.TdkLambda_PS.get_platen_right_addr(),
                                                         self.pwr_supply.set_pc, cmd[1])
                                elif 'Set Shroud Left' == cmd[0]:
                                    if cmd[2] == 'V'
                                        self.run_set_cmd(self.hw.TdkLambda_PS.get_shroud_left_addr(),
                                                         self.pwr_supply.set_pv, cmd[1])
                                    if cmd[2] == 'C'
                                        self.run_set_cmd(self.hw.TdkLambda_PS.get_shroud_left_addr(),
                                                         self.pwr_supply.set_pc, cmd[1])
                                elif 'Set Shroud Right' == cmd[0]:
                                    if cmd[2] == 'V'
                                        self.run_set_cmd(self.hw.TdkLambda_PS.get_shroud_right_addr(),
                                                         self.pwr_supply.set_pv, cmd[1])
                                    if cmd[2] == 'C'
                                        self.run_set_cmd(self.hw.TdkLambda_PS.get_shroud_right_addr(),
                                                         self.pwr_supply.set_pc, cmd[1])
                                elif 'Platen Duty Cycle' == cmd[0]:  #Duty cycle is a value from 0-1
                                    if cmd[1] > 1:
                                        dutycycle = 1.0
                                    elif cmd[1] < 0:
                                        dutycycle = 0.0
                                    else:
                                        dutycycle = float(cmd[1])
                                    self.run_set_cmd(self.hw.TdkLambda_PS.get_platen_left_addr(),
                                                     self.pwr_supply.set_pv, 450.0 * dutycycle)
                                    self.run_set_cmd(self.hw.TdkLambda_PS.get_platen_right_addr(),
                                                     self.pwr_supply.set_pv, 450.0 * dutycycle)
                                else:
                                    Logging.logEvent("Error", 'Unknown TDK Lambda command: "%s"' % cmd[0],
                                                     {"type": 'Unknown TdkLambda_Cmd',
                                                      "filename": 'ThreadControls/TdkLambdaControlStub.py',
                                                      "line": 93,
                                                      "thread": "TdkLambdaControlStub"
                                                      })

                        except ValueError as err:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            Logging.logEvent("Error", 'Error in TdkLambdaControlStub reading values: "%s"' % err,
                                             {"type": exc_type,
                                              "filename": fname,
                                              "line": exc_tb.tb_lineno,
                                              "thread": "TdkLambdaControlStub"
                                              })
                    else:
                        Logging.logEvent("Debug", "Status Update",
                                         {"message": "Test run of TDK Lambda Power Supplies loop",
                                          "level": 4})
                        # if first:
                        #     # TODO: Test the system at differnt starting pressures, it could restart at any point
                        #     # What happens when pressure in roughing  is more than cryo?
                        #     self.hw.TdkLambda_PS.update([{'addr': 1, 'voltage programmed': 1000},
                        #                          {'addr': 2, 'voltage programmed': 0.00001},
                        #                          {'addr': 3, 'voltage programmed': 999}],
                        #                          {'addr': 4, 'voltage programmed': 999}])
                        #     first = False
                        #     goingUp = False
                        # else:
                        #     print("get_pressure_chamber: "+ str(self.hw.TdkLambda_PS.get_chamber_pressure()))
                        #     if True or self.hw.TdkLambda_PS.get_chamber_pressure() > 0.0000001 and not goingUp:
                        #         self.hw.TdkLambda_PS.update([{'addr': 1, 'Pressure': self.gauges.get_cryopump_pressure()/2.5},
                        #                                      {'addr': 2, 'Pressure': self.gauges.get_chamber_pressure()/5},
                        #                                      {'addr': 3, 'Pressure': self.gauges.get_roughpump_pressure()/3}])
                        #     else:
                        #         goingUp = True
                        #         self.gauges.update([{'addr': 1, 'Pressure': self.gauges.get_cryopump_pressure()*2.5},
                        #                                      {'addr': 2, 'Pressure': self.gauges.get_chamber_pressure()*5},
                        #                                      {'addr': 3, 'Pressure': self.gauges.get_roughpump_pressure()*3}])
                        # Just to see the screen for longer
                        time.sleep(5)

                    if __name__ != '__main__':
                        pass # self.logPressureData()
                    if time.time() < next_status_read_time:
                        time.sleep(next_status_read_time - time.time())

            except Exception as e:
                # FileCreation.pushFile("Error",self.zoneUUID,'{"errorMessage":"%s"}'%(e))
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                Logging.logEvent("Error", "TDK Lambda Power Supplies Interface Thread",
                                 {"type": exc_type,
                                  "filename": fname,
                                  "line": exc_tb.tb_lineno,
                                  "thread": "TdkLambdaControlStub"
                                  })
                Logging.logEvent("Debug", "Status Update",
                                 {"message": "There was a {} error in TdkLambdaControlStub. File: {}:{}\n{}".format(
                                     exc_type, fname, exc_tb.tb_lineno, e),
                                  "level": 2})
                # raise e
            # nicely close things, to open them back up again...
            finally:
                userName = os.getlogin()
                if "root" in userName:
                    pass
                time.sleep(4)

    def run_set_cmd(self, addr, function, val):
        self.pwr_supply.set_addr(addr)
        if self.hw.OperationalVacuum:
            if not self.hw.TdkLambda_PS.get_val(addr, 'output enable'):
                self.pwr_supply.set_out_on()
            function(val)
        else:
            Logging.logEvent("Debug", "Status Update",
                             {"message": 'TDK Lambda Powers Supply Cant be turned on when not in Operational vacuum',
                              "level": 4})


if __name__ == '__main__':
    # adding debug info
    if(len(sys.argv)>1):
        for arg in sys.argv:
            if arg.startswith("-v"):
                Logging.verbos = arg.count("v")
    Logging.logEvent("Debug","Status Update",
        {"message": "Debug on: Level {}".format(Logging.verbos),
         "level":1})
    thread = TdkLambdaControlStub()
    thread.daemon = True
    thread.start()

    p = HardwareStatusInstance.getInstance().TdkLambda_PS
    while True:
        time.sleep(5)
        print(p.getJson())
