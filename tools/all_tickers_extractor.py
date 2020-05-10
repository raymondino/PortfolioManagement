import requests
from string import Template


def extract_all_tickers():
    """
    This function scrapes all tickers available across three security exchanges
    :return:
    """
    letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
               "U", "V", "W", "X", "Y", "Z"]
    exchanges = ["AMEX", "NYSE", "NASDAQ"]
    url_template = Template('https://financialmodelingprep.com/api/v3/search?query=$l&exchange=$e')
    all_tickers = set()

    for e in exchanges:
        print(f"scraping {e}")
        for l in letters:
            url = url_template.substitute(l=l, e=e)
            data = requests.get(url).json()
            for d in data:
                all_tickers.add(d['symbol'])

    path = r"C:\Users\ruya\Documents\PortfolioManagement\data\all_tickers.txt"
    with open(path, 'w', encoding='utf-8') as fp:
        for t in all_tickers:
            fp.write(t+'\n')


if __name__ == '__main__':
    extract_all_tickers()
