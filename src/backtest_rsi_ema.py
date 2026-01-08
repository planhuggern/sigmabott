import matplotlib.pyplot as plt
from src.backtest_engine import run_simple_backtest


def backtest():
    """Run backtest using the backtest engine and display results with matplotlib."""
    # Run backtest using the engine
    result = run_simple_backtest(
        symbol="BTC-USD",
        period="6mo",
        interval="4h",
        ema_window=20,
        rsi_window=14,
        rsi_oversold=30,
        rsi_overbought=70
    )
    
    data = result.data
    
    # Create visualization
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(11, 6))

    # EMA and Close price
    (ema,) = ax1.plot(data.index, data["EMA20"], label="EMA20")
    (close,) = ax1.plot(data.index, data["Close"], label="Close")
    ax1.legend()
    ax1.set_title("RSI+EMA Backtest")

    # RSI
    ax2.plot(data.index, data["RSI"], label="RSI(14)", linewidth=1)
    ax2.axhline(70, linestyle="--")
    ax2.axhline(30, linestyle="--")
    ax2.legend()
    ax2.set_title("RSI")

    # Cumulative returns
    (hold,) = ax3.plot(data.index, (data["cum_return"] - 1) * 100, label="Kjøp & hold")
    (strategy,) = ax3.plot(
        data.index, (data["cum_strategy"] - 1) * 100, label="Strategi"
    )
    ax3.legend()
    ax3.set_ylabel("avkastning (%)")
    ax3.tick_params(axis="y")

    plt.tight_layout()
    plt.show()

    # Print statistics from result
    print(f"Total avkastning: {result.total_return:.2f}% | Max drawdown: {result.max_drawdown:.2f}%")
    print(f"Kjøp & hold: {result.buy_hold_return:.2f}% | Sharpe Ratio: {result.sharpe_ratio:.2f}")


def main():
    backtest()


if __name__ == "__main__":
    main()
