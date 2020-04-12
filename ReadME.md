# Environment Setup
1. install anaconda
2. create & activate a virtual environment
3. install [quantstats](https://github.com/ranaroussi/quantstats) lib: pip install quantstats --upgrade --no-cache-dir 
4. open this repo with your favourite python IDE, I use pycharm
5. in your python IDE, set up the project interpreter as your created virtual environment, which is where you installed quantstats

# Modern Portfolio Theory Optimization 
- optimize your portfolio:
    - in your python IDE, open main.py file, edit the file by adding tickers you would like to invest
    - follow the comments in main.py to run the code
- evaluate your portfolio:
    - follow the comments in the main.py to run the code 
- a presentation of modern portfolio theory & how to use it for portfolio optimization: [click me](https://docs.google.com/presentation/d/1qQLCrJ5L-x1EnufmW91YT8Xu5nBM4e8IyP8v7rfWVOc/edit?usp=sharing)

# a fix to yfinance
line 286 in yfinance\base.py, replace with this
```python
        if len(holders) > 1:
            self._institutional_holders = holders[1]
            if 'Date Reported' in self._institutional_holders:
                self._institutional_holders['Date Reported'] = _pd.to_datetime(
                    self._institutional_holders['Date Reported'])
            if '% Out' in self._institutional_holders:
                self._institutional_holders['% Out'] = self._institutional_holders[
                                                           '% Out'].str.replace('%', '').astype(float) / 100

```

Enjoy! :-)
RY
