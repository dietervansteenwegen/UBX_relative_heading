# -*- coding: utf-8 -*-
class OutputBuffer:

    def __init__(self):
        self.status = ''
        self.no_msg_ok = 0
        self.no_msg_nok = 0
        self.last_msg_ok_timestamp = ''
        self.last_error = ''
        self.last_error_timestamp = ''
        self.last_hdg = 999
        self.last_hdg_acc = 999
        self.last_length = 999
        self.last_length_acc = 999
        self.relPosValid = 0
        self.isMoving = 0
        self.gnssFixOK = 0
        self.relPosHeading = 999
        self.accHeading = 999
        self.relPosLength = 999
        self.accLength = 999
        self.relPosHeadingValid = 0
        self.carrSoln = 0
        self.valid = 0

    def update(self, msg, rh):
        if not msg['ok']: # TODO: if (for example) carrSol = 0 -> self.carrSoln stays the last value
            self.no_msg_nok += 1
            self.last_error = msg['err_msg']
            self.valid = 0
            # self.last_error_timestamp =
        else:
            self.no_msg_ok += 1
            self.relPosHeading = msg['relPosHeading']
            self.accHeading = msg['accHeading']
            self.relPosLength = msg['relPosLength']
            self.accLength = msg['accLength']
            self.gnssFixOK = msg['gnssFixOK']
            self.relPosNormalized = msg['relPosNormalized']
            self.isMoving = msg['isMoving']
            self.relPosHeadingValid = msg['relPosHeadingValid']
            self.carrSoln = msg['carrSoln']
            self.valid = 1
            # self.last_msg_ok_timestamp =

    def formatted(self, short = False):
        if short:
            hdg = '{:06.2f}'.format(self.relPosHeading)
            length = '{:04.0f}'.format(self.relPosLength)
            valid = '{}'.format(1 if self.relPosHeadingValid else 0)
            sol = '{}'.format(self.carrSoln)
            msg = '{},{},{},{} (valid/soln/heading/length)'.format(1 if valid else 0, sol,hdg,length)
        else:
            hdg = 'HDG:{:06.2f}({:05.2f})'.format(self.relPosHeading, self.accHeading)
            length = 'LEN:{:04.0f}({:03.0f})cm'.format(self.relPosLength, self.accLength)
            valid = 'VAL:{}'.format('Y' if self.relPosHeadingValid else 'N')
            fix = 'FIX:{}'.format('Y' if self.gnssFixOK else 'N')
            norm = 'NORM:{}'.format('Y' if self.relPosNormalized else 'N')
            mov = 'MOV:{}'.format('Y' if self.isMoving else 'N')
            # print('{}'.format(self.carrSoln))
            sol = 'SOL:{}'.format(self.carrSoln)
            counter = '{:04}/{:04}'.format(self.no_msg_ok, self.no_msg_nok)
            msg = '{}|{}|{}|{}|{}|{}|{}|{}\r\n'.format(counter, fix,valid,sol,norm,mov,hdg,length).strip()
        return msg
