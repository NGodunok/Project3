import requests
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import webbrowser

API_KEY = "OVOCU1LAVMVSV4ZY"
BASE_URL = "https://www.alphavantage.co/query"

def get_stock_data(symbol, function, interval=None):
    params = {
        "function": function,
        "symbol": symbol,
        "apikey": API_KEY,
        "datatype": "json"
    }
    if interval:
        params["interval"] = interval
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        #checking for API limit or API error
        if "Note" in data:
            print("API call limit reached. Please wait and try again later.")
            return None
        
        if "Error Message" in data:
            print("Error: Invalid stock symbol or function. Please check input")
            return None
        
        time_series_key = next((key for key in data.keys() if 'Time Series' in key), None)
        if not time_series_key:
            print("Unexpected API response or response format. No time series data found.")
            return None
    
        df = pd.DataFrame.from_dict(data[time_series_key], orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.apply(pd.to_numeric)
        return df
    
    except requests.exceptions.RequestException as e:
        print(f"Networking error: {e}")
        return None
    
    except ValueError:
        print("Error occured while attempting to parse API response. Please try again.")
        return None


def plot_stock_data(df, start_date, end_date, chart_type, symbol):
    df = df.sort_index()

    filtered_df = df.loc[start_date:end_date]
    
    if filtered_df.empty:
        print("No data available for the selected date range.")
        return
    
    plt.figure(figsize=(10, 5))
    if chart_type == "line":
        plt.plot(filtered_df.index, filtered_df['4. close'], label=f'{symbol} Closing Price', linestyle='-')
    elif chart_type == "bar":
        plt.bar(filtered_df.index, filtered_df['4. close'], label=f'{symbol} Closing Price')
    
    plt.xlabel("Date")
    plt.ylabel("Closing Price (USD)")
    plt.title(f"Stock Data for {symbol} ({start_date} to {end_date})")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    chart_filename = "stock_chart.png"
    plt.savefig(chart_filename)
    plt.show()
    
    webbrowser.open(chart_filename)

def main():
    symbol = input("Enter stock symbol (e.g., AAPL, MSFT): ").upper()
    
    # Loop until valid graph type is entered
    while True:
        chart_type = input("Enter chart type (line/bar): ").strip().lower()
        if chart_type in ["line", "bar"]:
            break  # Exit loop if valid input
        else:
            print("Invalid input. Please enter either 'line' or 'bar'.")

    functions = {
        "1": "TIME_SERIES_INTRADAY",
        "2": "TIME_SERIES_DAILY",
        "3": "TIME_SERIES_DAILY_ADJUSTED",
        "4": "TIME_SERIES_WEEKLY",
        "5": "TIME_SERIES_WEEKLY_ADJUSTED",
        "6": "TIME_SERIES_MONTHLY",
        "7": "TIME_SERIES_MONTHLY_ADJUSTED"
    }
    
    print("Select time series function:")
    for key, value in functions.items():
        print(f"{key}. {value}")
    
    function_choice = input("Enter your choice: ")
    function = functions.get(function_choice)
    if not function:
        print("Invalid choice. Exiting.")
        return
    
    interval = None
    if function == "TIME_SERIES_INTRADAY":
        interval = input("Enter interval (1min, 5min, 15min, 30min, 60min): ")
    
    while True:
        start_date = input("Enter start date (YYYY-MM-DD): ")
        end_date = input("Enter end date (YYYY-MM-DD): ")
        
        try:
            start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            if start_date_obj > end_date_obj:
                print("Error: End date cannot be before start date. Please try again.")
            else:
                break
        except ValueError:
            print("Invalid date format. Please enter in YYYY-MM-DD format.")
    
    df = get_stock_data(symbol, function, interval)
    if df is not None:
        plot_stock_data(df, start_date, end_date, chart_type, symbol)

if __name__ == "__main__":
    main()

