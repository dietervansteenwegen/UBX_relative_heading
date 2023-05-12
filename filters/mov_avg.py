# -*- coding: utf-8 -*-
class MovingAverage:

    __all__ = ['update', 'reset', 'update']

    def __init__(self, *args, **kwargs):
        self.reset(*args, _init=True, **kwargs)  # default values

    def reset(
        self, init_est = 999, \
                        init_est_err = 999, \
                        fix_meas_err = None, \
                        _init = False,
    ):
        """set filter to initial values. Gets called by __init__ with argument _init = True"""
        print('reset filter, fix_meas_err = {}'.format(fix_meas_err))
        self._last_est = init_est
        self._last_est_err = init_est_err

        if _init:  # when called by init, the self.fix_meas_err certainly isn't set yet.
            self.fix_meas_err = fix_meas_err  # if fix_meas_err was given by user, use that value, otherwise None (default value)
        else:
            if fix_meas_err:  # if user re-inits/resets
                self.fix_meas_err = fix_meas_err

    def update(self, meas: float, meas_err=None):
        """updates"""
        # TODO: check variables

        try:
            if not self.fix_meas_err and not meas_err:
                raise Exception(
                    'either set a fixed measurement error during init/reset, or specify one with each update',
                )
            meas = float(meas)
            meas_err = float(meas_err) if meas_err else float(self.fix_meas_err)
        except (ValueError, TypeError) as e:
            print('Error in one of the given values for meas_err: {}'.format(e))
            return None, None
        except Exception as e:
            print('error: {}'.format(e))

        self.gain = self._calc_gain(meas_err)
        self.new_est = self._calc_est(meas)
        self.new_est_err = self._calc_est_err()
        self._last_est = self.new_est
        self._last_est_err = self.new_est_err
        print('{:0.2f}|{:0.6f}|{:0.6f}'.format(self.new_est, self.new_est_err, self.gain))
        return self.new_est, self.new_est_err

    def _calc_gain(self, meas_err):
        kg = self._last_est_err / (self._last_est_err + meas_err)
        return kg

    def _calc_est(self, meas):
        est = self._last_est + self.gain * (meas - self._last_est)
        return est

    def _calc_est_err(self):
        est_err = (1 - self.gain) * self._last_est_err
        return est_err
