#!/usr/bin/env python3.5

import io
import time


class Tdk_lambda_Genesys:

    def send_cmd(self, command):
        tdk = open('/dev/ttyxuart4', 'r+b', buffering=0)
        for tries in range(1, 3+1):
            tdk.write(self.append_checksum(command).encode())
            time.sleep(0.15 * tries)
            # TODO: Change to error event print("C:--" + self.GenCmd(Command).replace('\r', r'\r') + "---")
            (resp_good, resp) = self.check_checksum(tdk.read(128).decode())
            if resp_good:
                break
            print("TDK LAMBDA cmd try number: {:d}".format(tries))
        else:
            raise Exception('Response: "{:s}" is not "OK"'.format(resp))
        tdk.close()
        return resp

    def append_checksum(self, cmd):
        return '{:s}${:02X}\r'.format(cmd, 0xff & sum(cmd.encode()))

    def check_checksum(self, resp):
        # print("R:---" + resp.replace('\r', r'\r') + "---")
        # print("CS:--" + self.append_checksum(resp[:-4]).replace('\r', r'\r') + "---")
        if resp == self.append_checksum(resp[:-4]):
            return True, resp[:-4].strip()
        else:
            return False, resp.strip()

    def set_addr(self, addr):
        resp = self.send_cmd('ADR {:d}'.format(addr))
        if resp != 'OK':
            raise Exception('Addr {:d}; Response: "{:s}" is not "OK"'.format(addr, resp))

    def get_idn(self):
        return {'Model Name': self.send_cmd('IDN?')}

    def get_rev(self):
        return {'Software Vir': self.send_cmd('REV?')}

    def get_sn(self):
        return {'serial number': self.send_cmd('SN?')}

    def get_date(self):
        return {'last test date': self.send_cmd('DATE?')}

    def get_out(self):
        resp = self.send_cmd('OUT?')
        if resp == 'ON':
            return {'output enable': True}
        elif resp == 'OFF':
            return {'output enable': False}
        else:
            raise Exception('Out? Response: "{:s}" is not "ON" or "OFF"'.format(resp))
    def set_out(self, out_on=False):
        if out_on:
            resp = self.send_cmd('OUT 1')
        else:
            resp = self.send_cmd('OUT 0')
        if resp != 'OK':
            raise Exception('OUT Response: "{:s}" is not "OK"'.format(resp))
    def set_out_on(self):
        resp = self.send_cmd('OUT 1')
        if resp != 'OK':
            raise Exception('OUT 1 Response: "{:s}" is not "OK"'.format(resp))
    def set_out_off(self):
        resp = self.send_cmd('OUT 0')
        if resp != 'OK':
            raise Exception('OUT 0 Response: "{:s}" is not "OK"'.format(resp))

    def get_ast(self):
        resp = self.send_cmd('AST?')
        if resp == 'ON':
            return {'auto restart': True}
        elif resp == 'OFF':
            return {'auto restart': False}
        else:
            raise Exception('AST? Response: "{:s}" is not "OFF" or "OFF"'.format(resp))

    def get_mode(self):
        return {'control mode': self.send_cmd('MODE?')}

    def get_status(self):
        values = self.send_cmd('STT?').split(',')
        d = {}
        for val in values:
            if val[:2] == 'MV':
                d.update({'voltage measured': float(val[3:-1])})
            elif val[:2] == 'PV':
                d.update({'voltage programmed': float(val[3:-1])})
            elif val[:2] == 'MC':
                d.update({'current measured': float(val[3:-1])})
            elif val[:2] == 'PC':
                d.update({'current programmed': float(val[3:-1])})
            elif val[:2] == 'SR':
                d.update({'status reg': int(val[3:-1])})
            elif val[:2] == 'FR':
                d.update({'fault reg': int(val[3:-1])})
            else:
                raise Exception('STT? resp: "{:s}" is not formatted like: '
                                '"MV(float),PV(float),MC(float),PC(float),SR(hex),FR(hex)"'.format(val))
        return d

    # TODO put coersing limits on program values
    def set_pv(self, volt):
        resp = self.send_cmd('PV {:0.2f}'.format(volt))
        if resp != 'OK':
            raise Exception('PV {:0.2f} Response: "{:s}" is not "OK"'.format(volt, resp))

    def set_pc(self, current):
        resp = self.send_cmd('PC {:0.3f}'.format(current))
        if resp != 'OK':
            raise Exception('Pc {:0.2f} Response: "{:s}" is not "OK"'.format(current, resp))



if __name__ == '__main__':
    tdk = Tdk_lambda_Genesys()
    cmds = ['ADR 1', 'IDN?', 'REV?', 'SN?', 'DATE?', 'OUT?', 'AST?', 'DVC?', 'STT?',
            'ADR 2', 'IDN?', 'REV?', 'SN?', 'DATE?', 'OUT?', 'AST?', 'DVC?', 'STT?',
            'ADR 3', 'IDN?', 'REV?', 'SN?', 'DATE?', 'OUT?', 'AST?', 'DVC?', 'STT?',
            'ADR 4', 'IDN?', 'REV?', 'SN?', 'DATE?', 'OUT?', 'AST?', 'DVC?', 'STT?']
    for cmd in cmds:
        print('cmd: "{:s}" - resp: "{:s}"'.format(cmd, tdk.send_cmd(cmd)))
