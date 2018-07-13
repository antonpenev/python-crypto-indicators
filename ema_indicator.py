from indicator_base import IndicatorBase


class EmaIndicator(IndicatorBase):

    def __init__(self, processor, indicator_args_dict):
        super().__init__(indicator_args_dict)
        self.period = indicator_args_dict["period"]
        self.velocity_vals = []
        self.raw_vals = []
        self.type = 'close'
        if 'type' in indicator_args_dict:
            self.type = indicator_args_dict['type']

    def get_potential_value(self, vals, price, period):
        multiplier = 2 / float(1 + period)
        tmp = ((price - vals[-1]) * multiplier) + vals[-1]
        return tmp

    def on_new_candle(self, candle):
        value = candle[self.type]

        self.raw_vals.append(value)
        if len(self.raw_vals) < self.period:
            return

        if len(self.raw_vals) == self.period:
            self.values.append(sum(self.raw_vals) / self.period)
        else:
            self.values.append(self.get_potential_value(
                self.values, value, self.period))
            self.velocity_vals.append(self.values[-1] - self.values[-2])

    def get_last_value(self):
        return self.values[-1]

    def has_enough_data(self):
        return len(self.values) > 0

    def get_value(self, idx=None):
        if idx is None:
            return self.values[-1]
        if len(self.values) == 0:
            return -1000
        return self.values[idx - self.period]

    def get_ema_velocity_val(self, idx=None):
        if idx is None:
            return self.velocity_vals[-1]
        return self.velocity_vals[(len(self.velocity_vals) - self.period - 1)]


class VolPriceEmaIndicator(EmaIndicator):
    def update(self, candle):
        val = candle['close'] * candle['volume']
        super().update({'vol*price': val, 'open_time': candle['open_time']})
