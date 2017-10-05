#!/usr/bin/env python3.5

import io
import time


class Tdk_lambda_Genesys:

    def send_cmd(self, command):
        tdk = open('/dev/ttyxuart4', 'r+b', buffering=0)
        for tries in range(1, 3+1):
            tdk.write(self.append_checksum(command).encode())
            time.sleep(0.10 * tries)
            # TODO: Change to error event print("C:--" + self.GenCmd(Command).replace('\r', r'\r') + "---")
            (resp_good, resp) = self.check_checksum(tdk.read(64).decode())
            print("R:---" + resp.replace('\r', r'\r') + "---")
            if resp_good:
                break
            print("TDK LAMBDA cmd try number: {:d}".format(tries))
        else:
            raise Exception('Response: "{:s}" is not "OK"'.format(resp))
        tdk.close()
        return resp

    def append_checksum(self, cmd):
        return '{:s}${:2X}\r'.format(cmd, 0xff & sum(cmd.encode()))

    def check_checksum(self, resp):
        print("CS:--" + self.append_checksum(resp[:-4]).replace('\r', r'\r') + "---")
        if resp == self.append_checksum(resp[:-4]):
            return True, resp[:-4].strip()
        else:
            return False, resp.strip()

    def set_addr(self, addr):
        resp = self.send_cmd('ADR {:d}'.format(addr))
        if resp != 'OK':
            raise Exception('Response: "{:s}" is not "OK"'.format(resp))

    def get_idn(self):
        pass


if __name__ == '__main__':
    tdk = Tdk_lambda_Genesys()
    cmds = ['ADR 1', 'IDN?', 'REV?', 'SN?', 'DATE?', 'OUT?', 'AST?', 'DVC?', 'STT?',
            'ADR 1', 'IDN?', 'REV?', 'SN?', 'DATE?', 'OUT?', 'AST?', 'DVC?', 'STT?',
            'ADR 2', 'IDN?', 'REV?', 'SN?', 'DATE?', 'OUT?', 'AST?', 'DVC?', 'STT?']
    for cmd in cmds:
        print('cmd: "{:s}" - resp: "{:s}"'.format(cmd, tdk.send_cmd(cmd)))
