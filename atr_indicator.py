import talib
import numpy as np
from indicator_base import IndicatorBase


class ATRData(object):
    def __init__(self):
        self.high = []
        self.low = []
        self.close = []

    def on_new_candle(self, candle):
        self.high.append(candle['high'])
        self.low.append(candle['low'])
        self.close.append(candle['close'])

    def length(self):
        return len(self.high)

    def get_last_data(self, period, precision):
        return self.high[-period - precision:], self.low[-period - precision:], self.close[-period - precision:]


class ATRIndicator(IndicatorBase):
    def __init__(self, processor, indicator_args_dict):
        super().__init__(indicator_args_dict)

        self.timeperiod = indicator_args_dict["period"]
        self.atr_data = ATRData()
        self.last_candle = None
        self.precision = 70

    def get_value(self, idx=None):
        if idx is None:
            return self.values[-1]
        return self.values[idx]

    def on_new_candle(self, candle):
        self.atr_data.on_new_candle(candle)
        self.values.append(self.get_new_value())
        self.last_candle = candle

    def get_new_value(self, new_candle=None):
        if self.atr_data.length() < self.timeperiod + self.precision:
            return 50

        high, low, close = self.atr_data.get_last_data(
            self.timeperiod, self.precision)
        if new_candle is not None:
            high.append(new_candle['high'])
            low.append(new_candle['low'])
            close.append(new_candle['close'])
        high_nparr = np.array(high)
        low_nparr = np.array(low)
        close_nparr = np.array(close)
        res = talib.ATR(high=high_nparr, low=low_nparr,
                        close=close_nparr, timeperiod=self.timeperiod)
        return res.item(-1)

    def has_enough_data(self):
        return len(self.values) > 0
