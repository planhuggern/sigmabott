import numpy as np
import pandas as pd


def calculate_log_returns():
    prices = pd.Series([100, 105, 103, 110])
    simple_ret = prices.pct_change()
    log_ret = np.log(prices / prices.shift(1))

    print(pd.DataFrame({"Price": prices, "Simple": simple_ret, "Log": log_ret}))
    print("Total simple:", (1 + simple_ret.dropna()).prod())
    print("Total log:", log_ret.sum(), "→ exp() gives", np.exp(log_ret.sum()) - 1)

def main():
    calculate_log_returns() 



if __name__ == "__main__":
    main()
