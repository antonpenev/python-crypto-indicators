# Python Crypto Indicators

Useful indicators to generate financial technical indicators.
Some are based on Talib (but with little tweak to improve perfomance).
Others are attemps for basic Rain Forest Machine learning algorithms.

## Requirements

Install all needed external modules with

```
python -r requirements.txt
```

## Usage

### Pick some indicator

```
from rsi_indicator import RsiIndicator

my_indicator = RsiIndicator()
```

### Feed the indicator with data

```
my_indicator.on_new_candle(candle)
```

`candle` is OHLCV based candle

### Get aggregated data

```
my_indicator.export_data()
```

## List of supported indicators.

- RSI
- CCI
- MACD
- EMA
- ATR
- RF ML
- Volume weighted MACD
