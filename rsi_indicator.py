import talib
import numpy as np
from indicator_base import IndicatorBase


class RsiIndicator(IndicatorBase):
    def __init__(self, indicator_args_dict):
        super().__init__(indicator_args_dict)

        self.period = indicator_args_dict["period"]
        self._raw_values = []
        self._period = 120
        self.type = 'close'

        if 'type' in indicator_args_dict:
            self.type = indicator_args_dict['type']

    def get_value(self, idx=None):
        if idx is None:
            return self.values[-1]
        return self.values[idx]

    def on_new_candle(self, candle):
        value = candle[self.type]
        self._raw_values.append(value)

        self.values.append(self.get_rsi_new_value(value))

    def get_rsi_new_value(self, new_val=None):
        if len(self._raw_values) < self.period + 1:
            return 50

        last = self._raw_values[(-self._period):]
        if new_val is not None:
            last.append(new_val)
        new_values = np.array(last)
        res = talib.RSI(new_values, timeperiod=self.period)
        return res.item(-1)

    def has_enough_data(self):
        return len(self.values) > self._period
