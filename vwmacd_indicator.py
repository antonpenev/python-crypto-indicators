from core.indicators.ema_indicator import EmaIndicator
from core.indicators.indicator_base import IndicatorBase
class VwmacdIndicator(IndicatorBase):
    def __init__(self, processor, indicator_args_dict):
        super().__init__(indicator_args_dict)

        self.long = indicator_args_dict["long"]
        self.short = indicator_args_dict["short"]
        self.signal = indicator_args_dict["signal"]
        self.processor = processor

        vol_price_ema_slow_params = {"period": self.long, 'type':'vol*price'}
        vol_price_ema_fast_params = {"period": self.short, 'type':'vol*price'}
        vol_ema_slow_params = {"period": self.long, 'type':'volume'}
        vol_ema_fast_params = {"period": self.short, 'type':'volume'}
        signal_ema_params = {"period": self.signal, 'type':'d'}

        self.vol_price_ema_slow = self.processor.get_indicator("VolPriceEmaIndicator", vol_price_ema_slow_params)
        self.vol_price_ema_fast = self.processor.get_indicator("VolPriceEmaIndicator", vol_price_ema_fast_params)

        self.vol_ema_slow = self.processor.get_indicator("EmaIndicator", vol_ema_slow_params)
        self.vol_ema_fast = self.processor.get_indicator("EmaIndicator", vol_ema_fast_params)
        self.signal_ema = EmaIndicator(processor=None, indicator_args_dict = signal_ema_params)
        self.macd_vals = []

    def on_new_candle(self, candle):

        if not self.vol_ema_slow.has_enough_data():
            return
        maFast = self.vol_price_ema_fast.get_last_value() / self.vol_ema_fast.get_last_value()
        maSlow = self.vol_price_ema_slow.get_last_value() / self.vol_ema_slow.get_last_value()
        d = maSlow - maFast
        self.signal_ema.update({'d':d, 'open_time':candle['open_time']})
        if not self.signal_ema.has_enough_data():
            return
        maSignal = self.signal_ema.get_last_value()
        dm = maSignal - d
        self.macd_vals.append(dm)

    def get_value(self, idx = None):
        if len(self.macd_vals) == 0:
            return 0
        return self.macd_vals[-1]

    def has_enough_data(self):
        return len(self.macd_vals) > 0