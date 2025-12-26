from abc import ABC, abstractmethod
import pandas as pd
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator


class Strategy(ABC):
    """
    Abstract base class for trading strategies.
    """

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on the strategy.

        Args:
            data (pd.DataFrame): The input data containing price information.

        Returns:
            pd.DataFrame: The data with an additional 'signal' column.
        """
        pass


class EMAStrategy(Strategy):
    def __init__(self, ema_window: int):
        self.ema_window = ema_window

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        data[f"EMA{self.ema_window}"] = EMAIndicator(
            data["Close"], window=self.ema_window
        ).ema_indicator()
        data["signal"] = 0
        data.loc[data["Close"] > data[f"EMA{self.ema_window}"], "signal"] = 1  # Buy
        data.loc[data["Close"] < data[f"EMA{self.ema_window}"], "signal"] = -1  # Sell
        return data


class RSIStrategy(Strategy):
    def __init__(self, rsi_window: int, overbought: int = 70, oversold: int = 30):
        self.rsi_window = rsi_window
        self.overbought = overbought
        self.oversold = oversold

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        data["RSI"] = RSIIndicator(data["Close"], window=self.rsi_window).rsi()
        data["signal"] = 0
        data.loc[data["RSI"] < self.oversold, "signal"] = 1  # Buy
        data.loc[data["RSI"] > self.overbought, "signal"] = -1  # Sell
        return data