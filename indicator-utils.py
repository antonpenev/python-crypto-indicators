from config import config


def sma(time_series, period):
    s_len = len(time_series)
    result = []
    for i in range(period, s_len):
        result.append(sum(time_series[i - period:i]) / period)
    return result


def ema(time_series, period):
    """
    returns a period exponential moving average for
    the time series

    time_series is a list ordered from oldest (index 0) to most
    recent (index -1)
    period is an integer

    returns a numeric array of the exponential
    moving average
    """
    ema = []
    j = 1

    # get period sma first and calculate the next n period ema
    sma = sum(time_series[:period]) / period
    multiplier = 2 / float(1 + period)
    ema.append(sma)

    #EMA(current) = ( (Price(current) - EMA(prev) ) x Multiplier) + EMA(prev)
    ema.append(( (time_series[period] - sma) * multiplier) + sma)

    #now calculate the rest of the values
    for i in time_series[period + 1:]:
        tmp = ((i - ema[j]) * multiplier) + ema[j]
        j = j + 1
        ema.append(tmp)
    return ema
