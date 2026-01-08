### Opsett

Teknologi

#### scoop
Pakkeinstallering på windows:

```
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
```

#### uv, git og python


``` scoop install git python uv ```

### Opprett isolert miljø med uv

` uv venv .venv ` 

Activate with: ` .venv\Scripts\activate `

### Installer grunnpakker (via uv)
` uv pip install pandas matplotlib yfinance `


## VSCode
 
Sørg for at VSCode bruker det rette miljøet: 
` Ctrl + Shift + P → Python: Select Interpreter → trading_lab\.venv `

Vi trenger følgende extensions:
- Python (Microsoft)
- Pylance
- Jupyter (for notebooks)


## Git

### Github

git remote add origin git@github.com:espenhoh/sigmabott.git


## Kjør prosjekt

` uv run sigmabott `

Eller bruk PowerShell scriptet:

` .\run.ps1 `


## Studie

### Dag 1 Candlesticks
[candlestick-charting-what-is-it](https://www.investopedia.com/trading/candlestick-charting-what-is-it/)

### Dag 2 EMA og rsi
[Exponential moving average (EMA)](https://www.investopedia.com/terms/e/ema.asp)

- Alle glidende snitt indikatorer er lagging. De brukes til å verfisere at markedet er snudd, typeisk for sent å bruke dem til å entre markedet da det optimale tidspunktet har passert.
- Brukes for dag traders for å estimere ternden for dagen. Feks hvis trenden for dagen er positiv vil traderen stort segg trade long den dagen.

50 og 200 dags EMA: Long term
8 og 20 dags EMA: Short term

[Relative strength index (rsi)](https://www.investopedia.com/terms/r/rsi.asp)

Generelt < 30: oversolgt, > 70 overkjøpt

Brukes til å identifisere trading range i stigene og synkende trender
- Bullish signaler i bullish trender
- Bearish signaler i bearish trender

Ikke så nyttig ved flat utvikling

### Dag 3: Backtesting

[Backtesting](https://www.investopedia.com/terms/b/backtesting.asp)