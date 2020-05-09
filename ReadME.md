# Environment Setup
1. install anaconda
2. create & activate a virtual environment
3. install [quantstats](https://github.com/ranaroussi/quantstats) lib: ```pip install quantstats --upgrade --no-cache-dir``` 
4. open this repo with your favourite python IDE, I use pycharm
5. in your python IDE, set up the project interpreter as your created virtual environment, which is where you installed quantstats

# How to run
1. open main.py, go to the main function
2. set three global variables: ```risk_free_return```, ```year```, ```quarter```
    - ```risk_free_return```: 3-month treasury bill yield. It's updated daily. To get the latest yield, click [here](https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yield) 
    - ```year```: how many years back do you want to get the data. max is 10
    - ```quarter```: a boolean value to toggle quarter or annual report for company fundamentals
3. adjust the ```number``` variable below the global variables to run what you need. 
4. You will need to read on to know what each number indicates.

# Company Fundamentals Analysis
- analyze a company's fundamentals
    - set ```number = 1.1```, fill in the function with a company stock ticker
    - run ```main.py``` 
    - it will print historical financials including balance sheet, income statements, & cash flow statements
    - the console also shows the following analysis:
        - profitability:
            - Gross Margin
            - Net Profit Margin
            - Expenses Portion
            - ROE
            - ROA
        - operating:
            - Receivables Turnover Days
            - Inventories Turnover Days
            - Total Assets Turnover Days
        - solvency:
            - Liability/Asset Ratio
            - Current Ratio
            - Acid-test Ratio
        - growth:
            - Revenue Growth
            - Net Income Growth
            - Operating Income Growth
            - Free Cash Flow Growth
        - investing:
            - wacc
            - roic
            - excess return
            - economic profit
            - stockholders equity growth
            - dividendYield
            - dividendPayoutRatio
            - Number of Shares
            - Market Capitalization
            - Enterprise Value
 
 # Companies' Fundamentals Comparison
 - set ```number = 1.2```
 - either prepare a .txt file containing company tickers at each line, or specify the company tickers in ```ticker_list``` variable
 - run ```main.py```
 - it will produce a table comparing different companies profitability, operating capabilities, solvency and investment value
 - the comparison provides both mean and latest values
 - below picture shows an example
 
 ![Companies' Fundamentals Comparion](docs/2_companies_fundamentals_comparison.jpg?raw=true "Companies' Fundamentals Comparion")

# Plot Assets Correlations
- set ```number = 3.1```
- fill in tickers of interested in ```asset_tickers``` variable
- run main.py
- it will generate an image describing the pair-wise assets correlations
- below picture shows an example
![Plot Assets Correlations](docs/6_plot_assets_correlations.png?raw=true "Plot Assets Correlations")

# Optimize Portfolio with Modern Portfolio Theory
- My slides on Modern Portfolio Theory: [click me](https://docs.google.com/presentation/d/1qQLCrJ5L-x1EnufmW91YT8Xu5nBM4e8IyP8v7rfWVOc/edit?usp=sharing)
    - this slide introduces in great details and a friendly way to help understand & apply MPT optimization
- #### optimizing risk
    - when optimizing risk, the optimizer will find the optimal weights for the assets to minimize the portfolio risk
    - set ```number = 3.2```
    - set ```asset_tickers``` to be a list of tickers of interest
    - run main.py
    - in the console, optimal weights for each assets will be provided
    - the efficient frontier will also be plotted (will only plot efficient frontier for less than 4 assets)
    - below pictures show an example
    
    ![risk-optimized weights](docs/7_mpt_risk_weights.jpg?raw=true "risk-optimized weights")
    ![efficient frontier](docs/7_mpt_risk_ef.png?raw=true "efficient frontier")
- #### optimizing sharpe ratio
    - when optimizing sharpe ratio, the optimizer will find the optimal weights for assets to maximize the portfolio sharpe ratio
    - set ```number = 3.3```
    - set ```asset_tickers``` to be a list of tickers of interest
    - run main.py
    - in the console, optimal weights for each assets will be provided
    - It will also provide the risk return of portfolios in different ratios of risk-free asset and risky assets
    - the efficient frontier, and the capital market line will be plotted
    - below pictures show an example
    ![risk-optimized weights](docs/8_mpt_sharpe_weights.jpg?raw=true "sharpe-optimized weights")
    ![efficient frontier](docs/8_mpt_sharpe_ef.png?raw=true "efficient frontier")

# Evaluation for Modern Portfolio Theory
- why do evaluation?
    - modern portfolio theory did change how people invest, by focusing on diversification, risk and return, etc
    - however, modern portfolio theory does has its assumptions (which is too ideal), and limitations due to its assumptions
    - since we used MPT to optimize our portfolio, we need to understand how well MPT works on the selected assets
    - that's the need to do the evaluation
    - I suggest you to do evaluation for every assets combo you would like to invest
- evaluation methods explained
    - or a year yi (i >= 2) in a series of years: [y1, y2, y3, …, yn]
    - get prediction: 
        - use history data [y1, y2, …, yi-1] to find the optimal weights
        - apply these optimal weights to the data in year yi, so as to get predicted risk, return, & sharpe
    - get ground truth:
        - use only data in year yi to find the optimal weights in that year
        - apply these weights to the data in year yi, so as to get the best-possible portfolio in that year
    - we compare prediction and ground truth
- how to run evaluation
    - set ```number = 3.4```
    - fill in ```asset_ticers``` with ticker strings of interest
    - run main.py
    - this will generate 4 pictures
        - risk optimization
            - a figure shows to provide evidence on how well the MPT tracks risk-optimized ground truth. 
            - another figure plots the return of the portfolio if using MPT risk-optimized weights, and ground truth weights
        - sharpe ration optimization
            - a figure shows to provide evidence on how well the MPT tracks sharpe ratio optimized ground truth. 
            - another figure plots the return of the portfolio if using MPT sharpe ratio optimized weights, and ground truth weights
- what to <b>observe</b> from the 4 pictures:
    - if optimize portfolio by minimizing the risk, the predicted portfolio risk should be higher than ground truth
    - if optimize portfolio by maximizing sharpe ratio, predicted portfolio sharpe should be lower than ground truth
    - the <b>closer</b> the prediction tracks the ground truth, the <b>more evidently</b> that MPT works in terms of predicting the <b>best</b> portfolio
- below pictures show an example
![MPT risk track](docs/9_risk_track.png?raw=true "MPT risk track")
![MPT risk track return](docs/9_risk_track_return.png?raw=true "MPT risk track return")
![MPT sharpe track](docs/9_sharpe_track.png?raw=true "MPT sharpe track")
![MPT sharpe track return](docs/9_sharpe_track_return.png?raw=true "MPT sharpe track return")

Enjoy! :-)

RY
