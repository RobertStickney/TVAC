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
from Hardware_Drivers.Tdk_lamda_Genesys import Tdk_lambda_Genesys

from Logging.MySql import MySQlConnect
from Logging.Logging import Logging


class TdkLambdaUpdater(Thread):
    def __init__(self, parent=None, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs
        self.parent = parent

        self.pwr_supply = Tdk_lambda_Genesys()
        self.zoneProfiles = ProfileInstance.getInstance().zoneProfiles
        self.hw = HardwareStatusInstance.getInstance()
        self.ps_read_peroid = 4.0  # 0.5s loop period

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
                Logging.logEvent("Debug", "Status Update",
                                {"message": "TDK Lambda Genesys Control Stub Thread",
                                 "level": 2})

                if os.name == 'posix':
                    userName = os.environ['LOGNAME']
                else:
                    userName = "User"
                if "root" in userName:
                    update_power_supplies = [{'addr': self.hw.TdkLambda_PS.get_platen_left_addr()},
                                             {'addr': self.hw.TdkLambda_PS.get_platen_right_addr()},
                                             {'addr': self.hw.TdkLambda_PS.get_shroud_left_addr()},
                                             {'addr': self.hw.TdkLambda_PS.get_shroud_right_addr()}]
                    for ps in update_power_supplies:
                        self.pwr_supply.set_addr(ps['addr'])
                        ps.update(self.pwr_supply.get_out())
                        if not self.hw.OperationalVacuum:
                            self.pwr_supply.set_out_off()
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
                                self.Process_Commands(self.hw.TdkLambda_Cmds.pop(0))

                        except ValueError as err:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            Logging.logEvent("Error", 'Error in TdkLambdaUpdater reading values: "%s"' % err,
                                             {"type": exc_type,
                                              "filename": fname,
                                              "line": exc_tb.tb_lineno,
                                              "thread": "TdkLambdaUpdater"
                                              })
                            if Logging.debug:
                                raise err
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
                                  "thread": "TdkLambdaUpdater"
                                  })
                Logging.logEvent("Debug", "Status Update",
                                 {"message": "There was a {} error in TdkLambdaUpdater. File: {}:{}\n{}".format(
                                     exc_type, fname, exc_tb.tb_lineno, e),
                                  "level": 1})
                if Logging.debug:
                    raise e
                time.sleep(4)
            # nicely close things, to open them back up again...

    def run_set_cmd(self, addr, fun, val):
        self.pwr_supply.set_addr(addr)
        fun(val)

    def Process_Commands(self, cmd):
        print("Tdk command: {}".format(cmd))
        if 'Set Platen Left' == cmd[0]:
            if cmd[2] == 'V':
                self.run_set_cmd(self.hw.TdkLambda_PS.get_platen_left_addr(),
                                 self.pwr_supply.set_pv, cmd[1])
            if cmd[2] == 'C':
                self.run_set_cmd(self.hw.TdkLambda_PS.get_platen_left_addr(),
                                 self.pwr_supply.set_pc, cmd[1])
        elif 'Set Platen Right' == cmd[0]:
            if cmd[2] == 'V':
                self.run_set_cmd(self.hw.TdkLambda_PS.get_platen_right_addr(),
                                 self.pwr_supply.set_pv, cmd[1])
            if cmd[2] == 'C':
                self.run_set_cmd(self.hw.TdkLambda_PS.get_platen_right_addr(),
                                 self.pwr_supply.set_pc, cmd[1])
        elif 'Set Shroud Left' == cmd[0]:
            if cmd[2] == 'V':
                self.run_set_cmd(self.hw.TdkLambda_PS.get_shroud_left_addr(),
                                 self.pwr_supply.set_pv, cmd[1])
            if cmd[2] == 'C':
                self.run_set_cmd(self.hw.TdkLambda_PS.get_shroud_left_addr(),
                                 self.pwr_supply.set_pc, cmd[1])
        elif 'Set Shroud Right' == cmd[0]:
            if cmd[2] == 'V':
                self.run_set_cmd(self.hw.TdkLambda_PS.get_shroud_right_addr(),
                                 self.pwr_supply.set_pv, cmd[1])
            if cmd[2] == 'C':
                self.run_set_cmd(self.hw.TdkLambda_PS.get_shroud_right_addr(),
                                 self.pwr_supply.set_pc, cmd[1])
        elif 'Enable All Output' == cmd[0]:  # Duty cycle is a value from 0-1
            if self.hw.OperationalVacuum:
                self.run_set_cmd(self.hw.TdkLambda_PS.get_platen_left_addr(),
                                 self.pwr_supply.set_out, True)
                self.run_set_cmd(self.hw.TdkLambda_PS.get_platen_right_addr(),
                                 self.pwr_supply.set_out, True)
                self.run_set_cmd(self.hw.TdkLambda_PS.get_shroud_left_addr(),
                                 self.pwr_supply.set_out, True)
                self.run_set_cmd(self.hw.TdkLambda_PS.get_shroud_right_addr(),
                                 self.pwr_supply.set_out, True)
            else:
                Logging.logEvent("Debug", "Status Update",
                                 {
                                     "message": 'TDK Lambda Powers Supply Cant be turned on when not in Operational vacuum',
                                     "level": 3})
        elif 'Enable Platen Output' == cmd[0]:  # Duty cycle is a value from 0-1
            if self.hw.OperationalVacuum:
                self.run_set_cmd(self.hw.TdkLambda_PS.get_platen_left_addr(),
                                 self.pwr_supply.set_out, True)
                self.run_set_cmd(self.hw.TdkLambda_PS.get_platen_right_addr(),
                                 self.pwr_supply.set_out, True)
            else:
                Logging.logEvent("Debug", "Status Update",
                                 {
                                     "message": 'TDK Lambda Powers Supply Cant be turned on when not in Operational vacuum',
                                     "level": 3})
        elif 'Setup Platen' == cmd[0]:  # Duty cycle is a value from 0-1
            Logging.logEvent("Debug", "Status Update",
             {
             "message": 'Setting up Platen',
             "level": 2})
            if self.hw.OperationalVacuum:
                for addr in [self.hw.TdkLambda_PS.get_platen_left_addr(),
                             self.hw.TdkLambda_PS.get_platen_right_addr()]:
                    self.pwr_supply.set_addr(addr)
                    self.pwr_supply.set_pc(0.0)
                    self.pwr_supply.set_pv(0.0)
                    self.pwr_supply.set_out_on()
            else:
                Logging.logEvent("Debug", "Status Update",
                                 {
                                     "message": 'TDK Lambda Powers Supply Cant be turned on when not in Operational vacuum',
                                     "level": 3})
        elif 'Disable All Output' == cmd[0]:  # Duty cycle is a value from 0-1
            self.run_set_cmd(self.hw.TdkLambda_PS.get_platen_left_addr(),
                             self.pwr_supply.set_out, False)
            self.run_set_cmd(self.hw.TdkLambda_PS.get_platen_right_addr(),
                             self.pwr_supply.set_out, False)
            self.run_set_cmd(self.hw.TdkLambda_PS.get_shroud_left_addr(),
                             self.pwr_supply.set_out, False)
            self.run_set_cmd(self.hw.TdkLambda_PS.get_shroud_right_addr(),
                             self.pwr_supply.set_out, False)
        elif 'Disable Platen Output' == cmd[0]:  # Duty cycle is a value from 0-1
            self.run_set_cmd(self.hw.TdkLambda_PS.get_platen_left_addr(),
                             self.pwr_supply.set_out, False)
            self.run_set_cmd(self.hw.TdkLambda_PS.get_platen_right_addr(),
                             self.pwr_supply.set_out, False)
        elif 'Platen Duty Cycle' == cmd[0]:  # Duty cycle is a value from 0-1
            if self.hw.OperationalVacuum:
                if cmd[1] > 1:
                    dutycycle = 1.0
                elif cmd[1] < 0:
                    dutycycle = 0.0
                else:
                    dutycycle = float(cmd[1])
                current = 5.5 * dutycycle
                voltage = current * 80.0
                for addr in [self.hw.TdkLambda_PS.get_platen_left_addr(),
                             self.hw.TdkLambda_PS.get_platen_right_addr()]:
                    self.pwr_supply.set_addr(addr)
                    self.pwr_supply.set_pc(current)
                    self.pwr_supply.set_pv(voltage)
            else:
                Logging.logEvent("Debug", "Status Update",
                                 {
                                     "message": 'TDK Lambda Powers Supply Cant be turned on when not in Operational vacuum',
                                     "level": 3})
        else:
            Logging.logEvent("Error", 'Unknown TDK Lambda command: "%s"' % cmd[0],
                             {"type": 'Unknown TdkLambda_Cmd',
                              "filename": 'ThreadControls/TdkLambdaUpdater.py',
                              "line": 93,
                              "thread": "TdkLambdaUpdater"
                              })


# if __name__ == '__main__':
    # adding debug info
    # if(len(sys.argv)>1):
    #     for arg in sys.argv:
    #         if arg.startswith("-v"):
    #             Logging.verbos = arg.count("v")
    # Logging.logEvent("Debug","Status Update",
    #     {"message": "Debug on: Level {}".format(Logging.verbos),
    #      "level":1})
    # thread = TdkLambdaUpdater()
    # thread.daemon = True
    # thread.start()

    # hw = HardwareStatusInstance.getInstance()
    # p = HardwareStatusInstance.getInstance().TdkLambda_PS
    # c = HardwareStatusInstance.getInstance().TdkLambda_Cmds

    # time.sleep(10)
    # print(p.getJson())

    # hw.OperationalVacuum = True
    # time.sleep(5)
    # print(p.getJson())
    # c.append(['Setup Platen', ''])
    # time.sleep(5)
    # print(p.getJson())
    # c.append(['Platen Duty Cycle', 0.1])
    # time.sleep(5)
    # print(p.getJson())
    # c.append(['Platen Duty Cycle', 0.05])
    # time.sleep(5)
    # print(p.getJson())
    # c.append(['Platen Duty Cycle', 1.0])
    # time.sleep(5)
    # print(p.getJson())
    # c.append(['Platen Duty Cycle', 0.5])
    # c.append(['Platen Duty Cycle', 0.5])
    # c.append(['Platen Duty Cycle', 0.5])
    # c.append(['Platen Duty Cycle', 0.5])
    # time.sleep(5)
    # print(p.getJson())
    # c.append(['Platen Duty Cycle', 0.0])
    # time.sleep(5)
    # print(p.getJson())
    # c.append(['Disable Platen Output', ''])
    # time.sleep(5)
    # print(p.getJson())
