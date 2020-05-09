import time
import multiprocessing
from core.company import *
from utils.widget import *


def analyze_company(ticker, risk_free_return, quarter=False, year=5):
    """
    This function analyzes one company"s fundamentals
    :param ticker: company stock ticker
    :param risk_free_return: the 3-month t-bill return
    :param quarter: whether to see it's quarter report. If false, will see its annual report
    :param year: see data back to how many years. 5 is the default
    :return:
    """
    c = Company(ticker, quarter=quarter, year=year)
    c.print_financials()
    c.print_quantitative_analysis(risk_free_return)


def compare_companies(ticker_list, risk_free_return, quarter=False, year=5):
    """
    This function compares multiple companies" fundamentals, by comparing the latest report and 10 year mean
    :param ticker: company stock ticker
    :param risk_free_return: the 3-month t-bill return
    :param quarter: whether to see it's quarter report. If false, will see its annual report
    :param year: see data back to how many years. 5 is the default
    :return:
    """
    all_profitability = {}
    all_operating = {}
    all_solvency = {}
    all_growth = {}
    all_investing = {}

    for ticker in ticker_list:
        c = Company(ticker, quarter=quarter)
        try:
            # From Python 3.6 onwards, the standard dict type maintains insertion order by default
            all_profitability[ticker] = c.get_profitability_summary()
            all_operating[ticker] = c.get_operating_summary()
            all_solvency[ticker] = c.get_solvency_summary()
            all_growth[ticker] = c.get_growth_summary()
            all_investing[ticker] = c.get_investing_summary(risk_free_return)[0:7]
        except Exception as e:
            # need to remove any data of a ticker causing exceptions
            if ticker in all_profitability:
                del all_profitability[ticker]
            if ticker in all_operating:
                del all_operating[ticker]
            if ticker in all_solvency:
                del all_solvency[ticker]
            if ticker in all_growth:
                del all_growth[ticker]
            if ticker in all_investing:
                del all_investing[ticker]
            print(f"{ticker} cannot scrape - {e}")

    p = pd.concat(list(all_profitability.values()), axis=1)
    o = pd.concat(list(all_operating.values()), axis=1)
    s = pd.concat(list(all_solvency.values()), axis=1)
    g = pd.concat(list(all_growth.values()), axis=1)
    i = pd.concat(list(all_investing.values()), axis=1)

    p.columns = o.columns = s.columns = g.columns = i.columns = list(all_profitability.keys())

    p, p_new_columns, p_multilevel_index = p.T, [], []
    o, o_new_columns, o_multilevel_index = o.T, [], []
    s, s_new_columns, s_multilevel_index = s.T, [], []
    g, g_new_columns, g_multilevel_index = g.T, [], []
    i, i_new_columns, i_multilevel_index = i.T, [], []

    for c in p.columns:
        p_new_columns.append(c)
        p_new_columns.append(f"{c}_mean")
        p_new_columns.append(f"{c}_rank")
        p_multilevel_index.append((c, "value"))
        p_multilevel_index.append((c, "mean"))
        p_multilevel_index.append((c, "rank"))
        p[f"{c}_mean"] = p[c].mean()
        p[f"{c}_rank"] = p[c].rank(ascending=False if c != "Expenses Portion" else True)

    for c in o.columns:
        o_new_columns.append(c)
        o_new_columns.append(f"{c}_mean")
        o_new_columns.append(f"{c}_rank")
        o_multilevel_index.append((c, "value"))
        o_multilevel_index.append((c, "mean"))
        o_multilevel_index.append((c, "rank"))
        o[f"{c}_mean"] = o[c].mean()
        o[f"{c}_rank"] = o[c].rank(ascending=True)

    for c in s.columns:
        s_new_columns.append(c)
        s_new_columns.append(f"{c}_mean")
        s_new_columns.append(f"{c}_rank")
        s_multilevel_index.append((c, "value"))
        s_multilevel_index.append((c, "mean"))
        s_multilevel_index.append((c, "rank"))
        s[f"{c}_mean"] = s[c].mean()
        s[f"{c}_rank"] = s[c].rank(ascending=False if c != "Liability/Asset Ratio" else True)

    for c in g.columns:
        g_new_columns.append(c)
        g_new_columns.append(f"{c}_mean")
        g_new_columns.append(f"{c}_rank")
        g_multilevel_index.append((c, "value"))
        g_multilevel_index.append((c, "mean"))
        g_multilevel_index.append((c, "rank"))
        g[f"{c}_mean"] = g[c].mean()
        g[f"{c}_rank"] = g[c].rank(ascending=False)

    for c in i.columns:
        i_new_columns.append(c)
        i_new_columns.append(f"{c}_mean")
        i_new_columns.append(f"{c}_rank")
        i_multilevel_index.append((c, "value"))
        i_multilevel_index.append((c, "mean"))
        i_multilevel_index.append((c, "rank"))
        i[f"{c}_mean"] = i[c].mean()
        i[f"{c}_rank"] = i[c].rank(ascending=False if c != "wacc" else True)

    p = p[p_new_columns]
    o = o[o_new_columns]
    s = s[s_new_columns]
    g = g[g_new_columns]
    i = i[i_new_columns]

    p.columns = pd.MultiIndex.from_tuples(p_multilevel_index)
    o.columns = pd.MultiIndex.from_tuples(o_multilevel_index)
    s.columns = pd.MultiIndex.from_tuples(s_multilevel_index)
    g.columns = pd.MultiIndex.from_tuples(g_multilevel_index)
    i.columns = pd.MultiIndex.from_tuples(i_multilevel_index)

    print_table_title("Profitability Comparison")
    print(p.applymap(rank_number).to_string())
    print_table_title("Operation Comparison")
    print(o.applymap(rank_number).to_string())
    print_table_title("Solvency Comparison")
    print(s.applymap(rank_number).to_string())
    print_table_title("Growth Comparison")
    print(g.applymap(rank_number).to_string())
    print_table_title("Investing Comparison")
    print(i.applymap(rank_number).to_string())


def scrape_company_fundamentals(ticker_list, file_path, risk_free_return, quarter=False, year=5):
    """
    This function scrapes all the companies in the ticker_list for financial data and save to tsv file.
    :param ticker: company stock ticker
    :param risk_free_return: the 3-month t-bill return
    :param quarter: whether to see it's quarter report. If false, will see its annual report
    :param year: see data back to how many years. 5 is the default
    :return:
    """
    p = multiprocessing.Pool(multiprocessing.cpu_count())
    items = [
        "ticker", "market cap", "industry", "sector", "current price", "gross margin", "net income margin",
        "expenses portion", "ROE", "ROA", "receivables turnover days", "inventories turnover days",
        "total assets turnover days", "liability/asset ratio", "current ratio", "acid-test ratio", "revenue growth",
        "net income growth", "operating income growth", "free cash flow growth", "wacc", "roic", "excess return", 
        "economic profit", "stockholders equity growth", "dividend yield", "dividend payout ratio", "dcf", "beta",
        "annual return", "annual risk"
    ]
    with open(file_path, "w") as fp:
        fp.write("\t".join(items)+"\n")
        tickers_failed = []
        for result in p.imap(company_scraping_worker, [[ticker, risk_free_return, quarter] for ticker in ticker_list]):
            if len(result) <= 5:
                tickers_failed.append(result)
            else:
                fp.write(result)
        print(f"failed tickers={tickers_failed}")


def company_scraping_worker(args):
    """
    This is a helper function to parallelize the company information scraping.
    :param args: a list of four arguments: [ticker, risk_free_return, market_return, quarter]
    :return: the ticker if cannot scrape, or scraping info if can scrape
    """
    c = Company(args[0], quarter=args[2])
    try:
        t0 = time.clock()
        data = c.serialize_fundamentals_summary(args[1])
        print(f"- {args[0]} scraping done, takes {round(time.clock() - t0, 2)} seconds")
        return data
    except Exception:
        print(f"cannot scrape {args[0]}")
        return args[0]