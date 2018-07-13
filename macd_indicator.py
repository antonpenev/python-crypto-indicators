from ema_indicator import EmaIndicator
from indicator_base import IndicatorBase


class MACDResult(object):
    def __init__(self, macd, macdsignal, macdhist):
        self.macd = macd
        self.macdsignal = macdsignal
        self.macdhist = macdhist


class MACDIndicator(IndicatorBase):
    def __init__(self, processor, indicator_args_dict):
        super().__init__(indicator_args_dict)

        self.long = indicator_args_dict["long"]
        self.short = indicator_args_dict["short"]
        self.signal = indicator_args_dict["signal"]
        self.processor = processor

        ema_slow_params = {"period": self.long, 'type': 'close'}
        ema_fast_params = {"period": self.short, 'type': 'close'}
        signal_ema_params = {"period": self.signal, 'type': 'macd'}

        self.ema_slow = self.processor.get_indicator(
            "EmaIndicator", ema_slow_params)
        self.ema_fast = self.processor.get_indicator(
            "EmaIndicator", ema_fast_params)
        self.signal_ema = EmaIndicator(
            processor=None, indicator_args_dict=signal_ema_params)
        self.macd_vals = []

    def on_new_candle(self, candle):

        if not self.ema_slow.has_enough_data():
            return

        macd = self.ema_fast.get_last_value() - self.ema_slow.get_last_value()
        self.signal_ema.update(
            {'macd': macd, 'open_time': candle['open_time']})
        if not self.signal_ema.has_enough_data():
            return
        ema_signal = self.signal_ema.get_last_value()
        hist = macd - ema_signal
        result = MACDResult(macd, ema_signal, hist)
        self.macd_vals.append(result)

    def get_value(self, idx=None):
        if len(self.macd_vals) == 0:
            return 0
        return self.macd_vals[-1]

    def has_enough_data(self):
        return len(self.macd_vals) > 0
