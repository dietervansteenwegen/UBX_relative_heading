# -*- coding: utf-8 -*-
import ubinascii

class UbxMsg:
    # msg_types_and_prefixes is a list with one element for each known message type
    # each element is a list consisting of a string with the msg name and a second element containing a string identifying the msg
    msg_types_and_prefixes = [
        ['relPosNed', b'\x01<'],
    ]

    def __init__(self, msg):
        """tries to convert msg (str) into a byte object. If it fails, sets an empty byte object
        """

        try:
            # bytes.fromhex(msg) does not exist in micropythonre
            # self.ubx_msg = ubinascii.unhexlify(msg.replace(' ',''))
            self.ubx_msg = msg
        except:
            self.ubx_msg = bytes()

        self.contents = dict()
        self.type=''
        self.payload_length = 0
        self.msg_payload = bytes()
        self.checksum = bytes()

    def process(self):
        """
        - checks checksum
        - checks message type
        - processes message according to type
        Returns a dict with
        - element 'ok': True if all went well, else False
        - element 'err_msg': lisst of errors
        - one element for each parsed result
        """
        rtn_dict = {'ok':True, 'err_msg':[]}
        try:
            #check length of message against minimum length
            if len(self.ubx_msg) < 9:
                raise Exception('MSG length to short: {} bytes. Msg: {}'.format(len(self.ubx_msg), self.ubx_msg))
            # check sync characters
            if not self.ubx_msg[:2] == b'\xB5\x62':
                raise Exception('incorrect sync char: {0[0]}, {0[1]} instead of B5,62'.format(self.ubx_msg))
            # check crc
            # needs to be done before the message is split, as checksum is
            # calculated over Class/ID/Length/Payload.
            if not self.__do_checksum():
                raise Exception('Checksum mismatch')
            # split message in different parts
            if not self.__split_msg():
                raise Exception('Error splitting msg in fields')
            # known message type?
            if not self.__check_msg_type():
                raise Exception('Msg type ({}) not known'.format(self.class_id))


            if self.type == 'relPosNed':
                self.relposned_process()

        except Exception as e:
            rtn_dict['ok'] = False
            rtn_dict['err_msg'].append(e)

        finally:
            rtn_dict.update(self.contents)
            return rtn_dict

    def __do_checksum(self):
        """Checks checksum of self.ubx_msg
        sets self.checked to True
        sets self.checksum_ok to True or False
        returns:
        False if checksum mismatch
        True if checksum matches
        """
        # TODO
        msg_checksum = self.ubx_msg[-2:]
        checksum_src = self.ubx_msg[2:-2]
        if self.__calculate_checksum(checksum_src) == msg_checksum:
            return True
        else:
            return False

    def __calculate_checksum(self, source):

        CK_A = 0
        CK_B = 0

        for b in source:
            CK_A += b
            CK_B += CK_A

        CK_A %= 0x100
        CK_B %= 0x100

        ret = bytes()
        ret = int.to_bytes(CK_A,1, 'big') + int.to_bytes(CK_B,1,'big')

        return ret


    def __check_msg_type(self):
        """Checks msg type if checksum is ok,
        sets message type in self.type (string)
        """
        for i in self.msg_types_and_prefixes:
            if self.class_id == i[1]:
                self.type =i[0]
                return True
        return False

    def __split_msg(self):
        """Takes self.ubx_msg and splits it in:
        - self.payload_length (int)
        - self.checksum (list of two bytes)
        - self.msg_payload (list)
        - self.msg_class_id (list of 2 bytes)
        """
        # start from the end and work backward
        try:
            # get payload length
            self.payload_length = self.__payload_length()
            # check total msg length
            if len(self.ubx_msg) != (self.payload_length + 8):
                raise Exception('msgs length ({}) does not match payload length field ({})'.format(len(self.ubx_msg), self.payload_length))
            self.checksum = self.ubx_msg[-2:]
            self.ubx_msg = self.ubx_msg[:-2]
            self.msg_payload = self.ubx_msg[-self.payload_length:]
            self.ubx_msg = self.ubx_msg[:-self.payload_length]
            self.class_id = self.ubx_msg[2:4]

            return True

        except Exception as e:
            raise Exception('Could not split message: {}'.format(e))


    def __payload_length(self):
        """At this moment, payload should be a 2 byte chunk in position [4:5].
        Get value, convert to int and return.
        """
        try:
            return int.from_bytes(self.ubx_msg[4:6], 'little')
        except:
            return False

    def relposned_process(self):
        # processed the message to get length and heading of rel pos vector

        # relPosHeading
        chunk = self.msg_payload[24:28]
        self.contents['relPosHeading'] = int.from_bytes(chunk,'little',True) / 100000

        # relPosLength
        chunk = self.msg_payload[20:24]
        self.contents['relPosLength'] = int.from_bytes(chunk, 'little',True)

        # accLength
        chunk = self.msg_payload[48:52]
        self.contents['accLength'] = int.from_bytes(chunk, 'little',False) / 10

        # accHeading
        chunk = self.msg_payload[52:56]
        self.contents['accHeading'] = int.from_bytes(chunk, 'little',False) / 100000

        # flags
        chunk = self.msg_payload[60:]
        flags = int.from_bytes(chunk, 'little',False)
        self.contents['gnssFixOK'] = bit_set(flags, 0)
        self.contents['diffSoln'] = bit_set(flags, 1)
        self.contents['relPosValid'] = bit_set(flags, 2)
        self.contents['isMoving'] = bit_set(flags, 5)
        self.contents['relPosHeadingValid'] = bit_set(flags, 8)
        self.contents['relPosNormalized'] = bit_set(flags, 9)
        self.contents['carrSoln'] = (bit_set(flags, 4) *2) + bit_set(flags, 3)
        return True


def bit_set(value, bit_no):
    mask = 1 << bit_no
    return True if int(value)&mask > 0 else False


def main():
    with open('messages') as src:
        for line in src:
            msg = ubx_msg(line)
            ret = msg.process()

            # if ret['ok']:
            #     print(ret)
            print(ret)

if __name__ == '__main__':
    main()
