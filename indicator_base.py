from candle_builder import CandleBuilder


class IndicatorBase(object):

    def __init__(self, params):
        self.params = params
        self.values = []
        self.candle_builder = CandleBuilder(cache_size=1)
        self.candle_size = params['candle_size'] if 'candle_size' in params else 1
        self.candle_builder.add_request_update(self.candle_size, self)

    def on_new_candle(self, candle):
        pass

    def update(self, candle):
        self.candle_builder.on_new_candle(candle)

    def has_enough_data(self):
        raise Exception('has_enough_data not implemented')

    def get_value(self, idx=None):
        raise Exception('get_value not implemented')

    def export_data(self):
        return {'name': self.__class__.__name__,
                'params': self.params,
                'data': self.values}
