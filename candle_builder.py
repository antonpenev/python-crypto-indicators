from circular_list import CircularList
import datetime


def squash_candles(candle_arr):
    squashed_candle = candle_arr[0]
    candle_arr_len = len(candle_arr)
    if candle_arr_len == 1:
        return squashed_candle

    for i in range(1, candle_arr_len):
        c = candle_arr[i]
        squashed_candle['volume'] = squashed_candle['volume'] + c['volume']
        squashed_candle['low'] = c['low'] if c['low'] < squashed_candle['low'] else squashed_candle['low']
        squashed_candle['high'] = c['high'] if c['high'] > squashed_candle['high'] else squashed_candle['high']
    squashed_candle['close'] = candle_arr[-1]['close']
    return squashed_candle


class RequestUpdate:
    def __init__(self, interval, requester):
        self.interval = interval
        self.requester = requester
        self.current_streak = 0
        self.candles = []

    def update(self, candle):
        self.candles.append(candle)
        self.current_streak += 1
        if self.current_streak < self.interval:
            return

        candle = squash_candles(self.candles)
        self.requester.on_new_candle(candle)
        self.candles = []
        self.current_streak = 0

    def clone(self):
        cloned = RequestUpdate(self.interval, self.requester)
        cloned.current_streak = self.current_streak
        for candle in self.candles:
            cloned.candles.append(candle)

        return cloned


class CandleBuilder(object):
    DEFAULT_CACHE_SIZE = 1000

    def __init__(self, cache_size=None):
        self.required_updates = []
        # they are held here until it is synced with exchange candles timeframe
        self.pending_updates = []
        self.partial_candles = []
        self.cache_size = CandleBuilder.DEFAULT_CACHE_SIZE if cache_size is None else cache_size
        self.candles_list = CircularList(self.cache_size)

    def add_request_update(self, interval, requester):
        if self.candles_list.length() < interval or interval == 1:  # If interval is 1, we do not need headstart
            self.pending_updates.append(RequestUpdate(interval, requester))
        else:
            request_update = RequestUpdate(
                interval=interval, requester=requester)
            headstart_length = self.get_num_candles_for_headstart(interval)
            headstart_candles = self.candles_list.get_last_n_elements(
                headstart_length)
            for candle in headstart_candles:
                request_update.update(candle)
            self.required_updates.append(request_update)

    def remove_request_update(self, requester):
        for update in self.pending_updates:
            if update.requester == requester:
                self.pending_updates.remove(update)
                break

        for update in self.required_updates:
            if update.requester == requester:
                self.required_updates.remove(update)
                break

    def get_num_candles_for_headstart(self, interval):
        last_candle = self.candles_list.get_last_elemet()
        time = datetime.datetime.fromtimestamp(last_candle['open_time'] / 1000)
        minutes = time.hour * 60 + time.minute
        return minutes % interval

    def check_pending_updates(self, candle):
        if len(self.pending_updates) == 0:
            return

        tmp_updates = []
        time = datetime.datetime.fromtimestamp(candle['open_time'] / 1000)
        minutes = time.hour * 60 + time.minute
        for update in self.pending_updates:
            now = datetime.datetime.now()
            if minutes % update.interval == 0:
                tmp_updates.append(update)

        for tmp_update in tmp_updates:
            self.pending_updates.remove(tmp_update)
            self.required_updates.append(tmp_update)

    def on_new_candle(self, candle):
        self.candles_list.add(candle)
        if len(self.partial_candles) == 0:
            self.partial_candles.append(candle)
        self.check_pending_updates(candle)
        for request in self.required_updates:
            request.update(candle)

    def clone(self):
        cloned = CandleBuilder()
        all_candles = self.candles_list.get_ordered_elements()
        for candle in all_candles:
            cloned.candles_list.add(candle)
        for requester in self.pending_updates:
            cloned.pending_updates.append(requester.clone())
        for requester in self.required_updates:
            cloned.required_updates.append(requester.clone())
        return cloned

    def drop_all_requesters(self):
        self.pending_updates = []
        self.required_updates = []

    @staticmethod
    def get_candle_from_arrays(candles, idx):
        candle = dict()
        for candle_key in candles:
            candle[candle_key] = candles[candle_key][idx]
        return candle
