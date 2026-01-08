"""
Backtest engine - handles all backtesting logic separate from UI.
"""
from dataclasses import dataclass
from typing import List, Optional
import pandas as pd
from src.utils.yahoo_finance import download_yf
from src.strategies import Strategy, CombinedStrategy, EMAStrategy, RSIStrategy
from src.event_manager import EventManager


@dataclass
class BacktestConfig:
    """Configuration for a backtest run."""
    symbol: str
    period: str
    interval: str
    use_ema: bool
    ema_window: int
    use_rsi: bool
    rsi_window: int
    rsi_oversold: int
    rsi_overbought: int


@dataclass
class BacktestResult:
    """Results from a backtest run."""
    data: pd.DataFrame
    total_return: float
    buy_hold_return: float
    max_drawdown: float
    sharpe_ratio: float
    symbol: str
    config: BacktestConfig


class BacktestEngine:
    """Engine for running backtests with various strategies."""
    
    def __init__(self, event_manager: Optional[EventManager] = None):
        self.event_manager = event_manager or EventManager()
    
    def run_backtest(self, config: BacktestConfig) -> BacktestResult:
        """
        Run a backtest with the given configuration.
        
        Args:
            config: BacktestConfig with all parameters
            
        Returns:
            BacktestResult with data and metrics
            
        Raises:
            ValueError: If no data available or no strategies selected
        """
        # Download data
        data = download_yf(config.symbol, period=config.period, interval=config.interval)
        
        if data.empty:
            raise ValueError(f"No data available for {config.symbol}")
        
        # Initialize strategies
        strategies = self._build_strategies(config)
        
        if not strategies:
            raise ValueError("At least one strategy must be selected")
        
        # Apply combined strategy
        combined_strategy = CombinedStrategy(strategies=strategies)
        data = combined_strategy.generate_signals(data)
        
        # Calculate returns
        data = self._calculate_returns(data)
        
        # Calculate metrics
        metrics = self._calculate_metrics(data, config.interval)
        
        return BacktestResult(
            data=data,
            total_return=metrics['total_return'],
            buy_hold_return=metrics['buy_hold_return'],
            max_drawdown=metrics['max_drawdown'],
            sharpe_ratio=metrics['sharpe_ratio'],
            symbol=config.symbol,
            config=config
        )
    
    def _build_strategies(self, config: BacktestConfig) -> List[Strategy]:
        """Build list of strategies based on configuration."""
        strategies = []
        
        if config.use_ema:
            strategies.append(
                EMAStrategy(ema_window=config.ema_window, event_manager=self.event_manager)
            )
        
        if config.use_rsi:
            strategies.append(
                RSIStrategy(
                    rsi_window=config.rsi_window,
                    overbought=config.rsi_overbought,
                    oversold=config.rsi_oversold,
                    event_manager=self.event_manager
                )
            )
        
        return strategies
    
    def _calculate_returns(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate returns and cumulative returns."""
        data["return"] = data["Close"].pct_change()
        data["strategy_return"] = data["signal"].shift(1) * data["return"]
        data["cum_return"] = (1 + data["return"]).cumprod()
        data["cum_strategy"] = (1 + data["strategy_return"]).cumprod()
        return data
    
    def _calculate_metrics(self, data: pd.DataFrame, interval: str) -> dict:
        """Calculate performance metrics."""
        total_return = (data["cum_strategy"].iloc[-1] - 1) * 100
        buy_hold_return = (data["cum_return"].iloc[-1] - 1) * 100
        
        # Calculate max drawdown
        cummax = data["cum_strategy"].cummax()
        drawdown = (data["cum_strategy"] - cummax) / cummax
        max_drawdown = drawdown.min() * 100
        
        # Calculate Sharpe ratio (annualized for daily data)
        mean_return = data["strategy_return"].mean()
        std_return = data["strategy_return"].std()
        
        if std_return > 0:
            sharpe_ratio = mean_return / std_return
            if interval == "1d":
                sharpe_ratio *= (252 ** 0.5)  # Annualize for daily data
        else:
            sharpe_ratio = 0.0
        
        return {
            'total_return': total_return,
            'buy_hold_return': buy_hold_return,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio
        }


def run_simple_backtest(
    symbol: str,
    period: str = "6mo",
    interval: str = "4h",
    ema_window: int = 20,
    rsi_window: int = 14,
    rsi_oversold: int = 30,
    rsi_overbought: int = 70
) -> BacktestResult:
    """
    Convenience function to run a backtest with default settings.
    
    Args:
        symbol: Trading symbol (e.g., 'BTC-USD')
        period: Time period for data
        interval: Data interval
        ema_window: EMA window size
        rsi_window: RSI window size
        rsi_oversold: RSI oversold threshold
        rsi_overbought: RSI overbought threshold
        
    Returns:
        BacktestResult with data and metrics
    """
    config = BacktestConfig(
        symbol=symbol,
        period=period,
        interval=interval,
        use_ema=True,
        ema_window=ema_window,
        use_rsi=True,
        rsi_window=rsi_window,
        rsi_oversold=rsi_oversold,
        rsi_overbought=rsi_overbought
    )
    
    engine = BacktestEngine()
    return engine.run_backtest(config)
