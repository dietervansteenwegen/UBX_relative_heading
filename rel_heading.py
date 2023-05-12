# -*- coding: utf-8 -*-
from filters import MovingAvg

MOVING_AVG_SIZE = 40
RTK_COUNT_TRUST = 3  # 3 should be a good start, it means one non-fixed msg can come in, but then needs at least 2 fixed msg
RTK_UPPER_LIMIT = 5
RTK_LOWER_LIMIT = -15
MAX_ACC_LENGTH = 15
MAX_ACC_HEADING = 1
ANT_DISTANCE = 166
ANT_DISTANCE_MARGIN = 3
MAX_STEP_CHANGE = 0.7

class RelativeHeading:
    """Accepts messages from the ubx_msg class.
    To cope with carrSoln changes, self.rtk_count is kept (value -5 to +5)
    An RTK Fixed msg adds 1, an RTK float or no RTK substracts 2
    The trigger point RTK_COUNT_TRUST where our solution is trusted needs to be determined.
    Most info in self.update() function.
    """

    __all__ = ['update']

    class NoUpdate(Exception):
        """update last_err and return None."""

    def __init__ (self):
        self.update_counter = 0
        self._rtk_qual_count = 0
        self.last_err = ''
        self.value = 999
        self.valid = False
        self.updated = False
        self.moving_avg = MovingAvg(MOVING_AVG_SIZE)
        self._reset()

    def _reset(self):
        # self.confidence = None
        # self.last_estimate_error = None
        # self.last_estimate = None
        self.valid = False
        self.rh_value = 999
        self.moving_avg.reset()

    def update(self, msg):
        """
        With each update:
        * increment self.msg_rcv
        * update self.rtk_qual_count
        * check self._rtk_qual_count
        * check relPosHeadVal
        * check carrSoln = 2 (rtk fix)
        * accLength < MAX_ACC_LENGTH
        * if ANT_DISTANCE, verify limits (ANT_DISTANCE_MARGIN) against difference with relPosLength
        * accHeading should be less than 1 degree
        * if all above is good, pass to the moving average filter
        * if the last relative heading and result of average filter differ more than MAX_STEP_DIFF, set 'valid' to False
        """
        self.update_counter += 1 # one more incoming message
        self.last_err = ''
        self.updated = False
        self._update_rtk_qual_count(msg['carrSoln'])

        try:
            # Check if RTK is steady
            if not self._rtk_qual_count > RTK_COUNT_TRUST:
                raise RelativeHeading.NoUpdate('RTK solution not reliable')

            # check if relPosHeadVal is good:
            if not msg['relPosHeadingValid']:
                raise RelativeHeading.NoUpdate('relPosHead invalid')

            # check RTK Fix
            if msg['carrSoln'] < 2:
                raise RelativeHeading.NoUpdate('carrSoln < 2 (value: {})'.format(msg['carrSoln']))

            # check accuray length against MAX_ACC_LENGTH
            if msg['accLength'] > MAX_ACC_LENGTH:
                raise RelativeHeading.NoUpdate('accLength > MAX_ACC_LENGTH ({}/{})'.format(msg['accLength'], MAX_ACC_LENGTH))

            # if set, check the antenna distance against the received value and the set margin
            if ANT_DISTANCE:
                if abs(msg['relPosLength'] - ANT_DISTANCE) > ANT_DISTANCE_MARGIN:
                    err_msg = 'To much margin against set ant. distance (L: {}/ S: {}/ M: {})'.format(
                        msg['relPosLength'],
                        ANT_DISTANCE,
                        ANT_DISTANCE_MARGIN,
                    )
                    raise RelativeHeading.NoUpdate(err_msg)

            # check heading accuracy
            if msg['accHeading'] > MAX_ACC_HEADING:
                raise RelativeHeading.NoUpdate('accHeading > MAX_ACC_HEADING ({}/{})'.format(msg['accHeading'], MAX_ACC_HEADING))

            if not self.moving_avg.update(msg['relPosHeading']):
                raise RelativeHeading.NoUpdate('Moving avg update issue gave no result')

            # Check if difference between last relPosHead and the average isn't to big (moving structure)
            step_diff = abs(msg['relPosHeading'] - self.moving_avg.result)
            if  step_diff > MAX_STEP_CHANGE:
                raise RelativeHeading.NoUpdate('Step difference to big: diff: {}/max: {}'.format(step_diff, MAX_STEP_CHANGE))

            # Finally, if all went well, update self.value, set valid to true and return the value
            self.valid = True
            self.value = self.moving_avg.result
            self.updated = True
            return self.value

        except RelativeHeading.NoUpdate as e:
            self.valid = False
            self.last_err = e.args[0]
            return None

    def _update_rtk_qual_count(self, carrSoln):
        """Check if the carrSoln is good enough or whether it is time to reset the moving
            average filter."""
        if carrSoln == 2 :
            self._rtk_qual_count +=1
        else:
            self._rtk_qual_count -=2

        # keep value within limits
        if self._rtk_qual_count < RTK_LOWER_LIMIT:
            self._rtk_qual_count =RTK_LOWER_LIMIT
            # Rx has become lousy, reset the filter
            self._reset()
            print('_rtk_qual_count is at lower limit. reset')
        if self._rtk_qual_count > RTK_UPPER_LIMIT:
            self._rtk_qual_count = RTK_UPPER_LIMIT

        return True

    def return_value(self):
        if self.valid:
            self.updated = False
            return self.value
        return None
