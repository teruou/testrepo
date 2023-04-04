import os
import pandas as pd
from alpha_vantage.foreignexchange import ForeignExchange
from datetime import datetime
from dateutil.relativedelta import relativedelta


def fetch_fx_data(start_date, end_date):
    # Alpha Vantage APIキーを設定
    api_key = 'your_api_key'
    fx = ForeignExchange(key=api_key)
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # Get daily exchange rate data
    fx_data, _ = fx.get_currency_exchange_daily("USD", "JPY", outputsize="full")
    fx_data = {datetime.strptime(date, "%Y-%m-%d"): float(data["4. close"]) for date, data in fx_data.items() if start_date <= datetime.strptime(date, "%Y-%m-%d") <= end_date}

    # Convert the dictionary to a DataFrame
    fx_dataframe = pd.DataFrame.from_dict(fx_data, orient="index", columns=["Exchange Rate"])
    fx_dataframe.index.name = "Date"
    fx_dataframe.sort_index(ascending=True, inplace=True)

    return fx_dataframe


def write_fx_data_to_csv(start_year_month, end_year_month):
    start_date = datetime.strptime(start_year_month, "%Y-%m") + relativedelta(day=1)
    end_date = datetime.strptime(end_year_month, "%Y-%m") + relativedelta(day=31)

    fx_data = fetch_fx_data(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    print("Processed DataFrame:")
    print(fx_data.head())

    fx_data.to_csv("usd_jpy_fx_data.csv", index_label="Date", header=["Exchange Rate"])

    with open("usd_jpy_fx_data.csv", "r") as f:
        print("CSV file content:")
        print(f.read())


if __name__ == "__main__":
    start_year_month = "2004-01"
    end_year_month = "2023-03"
    write_fx_data_to_csv(start_year_month, end_year_month)
