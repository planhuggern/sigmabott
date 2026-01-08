import matplotlib.pyplot as plt
from src.utils.yahoo_finance import download_yf
from src.strategies import CombinedStrategy, EMAStrategy, RSIStrategy


def backtest():
    # Hent data
    data = download_yf("BTC-USD", period="6mo", interval="4h")

    # Initialize individual strategies
    ema_strategy = EMAStrategy(ema_window=20)
    rsi_strategy = RSIStrategy(rsi_window=14)

    # Initialize combined strategy with individual strategies
    combined_strategy = CombinedStrategy(strategies=[ema_strategy, rsi_strategy])

    # Apply combined strategy
    data = combined_strategy.generate_signals(data)

    # Beregn avkastning
    data["return"] = data["Close"].pct_change()
    data["strategy_return"] = data["signal"].shift(1) * data["return"]

    # Kumulativ avkastning
    data["cum_price"] = (1 + data["return"]).cumprod()
    data["cum_strategy"] = (1 + data["strategy_return"]).cumprod()
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(11, 6))

    # Plot
    # plt.figure(figsize=(10,5))
    (ema,) = ax1.plot(data.index, data["EMA20"], label="EMA20")
    (close,) = ax1.plot(data.index, data["Close"], label="Close")
    ax1.legend()
    ax1.set_title("RSI+EMA Backtest")

    # Create a single legend
    # lines = [ema, close, hold]
    # labels = [l.get_label() for l in lines]
    # ax2.legend(lines, labels, loc='upper left') # Adjust loc as needed

    ax2.plot(data.index, data["RSI"], label="RSI(14)", linewidth=1)
    ax2.axhline(70, linestyle="--")
    ax2.axhline(30, linestyle="--")
    ax2.legend()
    ax2.set_title("RSI")

    (hold,) = ax3.plot(data.index, (data["cum_price"] - 1) * 100, label="Kjøp & hold")
    (strategy,) = ax3.plot(
        data.index, (data["cum_strategy"] - 1) * 100, label="Strategi"
    )
    ax3.legend()
    ax3.set_ylabel("avkastning (%)")
    ax3.tick_params(axis="y")

    plt.tight_layout()
    plt.show()

    # Enkel statistikk
    total_ret = data["cum_strategy"].iloc[-1] - 1
    max_dd = (data["cum_strategy"] / data["cum_strategy"].cummax() - 1).min()
    print(f"Total avkastning: {total_ret:.2%} | Max drawdown: {max_dd:.2%}")


def main():
    backtest()


if __name__ == "__main__":
    main()
