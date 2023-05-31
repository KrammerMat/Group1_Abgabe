# import all required packages listed in the requirements.txt
from flask import Flask, render_template, request, flash, url_for, redirect
import yfinance as yf
import plotly.graph_objs as go
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = "supergeheim"

# path of text file containing all the tickers you want to show in the pull down select on the home 
script_dir = os.path.dirname(os.path.abspath(__file__))
tickers_file_path = os.path.join(script_dir, "tickers.txt")

# function to get the ticker symbols and company names from tickers.txt to show them in the pull down select
def load_tickers():

    ticker_data = {}
    with open(tickers_file_path, "r") as file:
        for line in file:
            ticker, company = line.strip().split(",")
            ticker_data[ticker] = company
    return ticker_data

ticker_data = load_tickers()

# function for building the stock ticker chart
def build_chart(data, company_name):
    
    # specify the candlestick chart visualizing the retrieved data using the package plotly
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        increasing=dict(line=dict(color='#00ff7f')),
        decreasing=dict(line=dict(color='#ff6347'))
    )])

    # specify the style of the chart
    fig.update_layout(
        
        # adding the company name to the title of the chart
        title={
            'text': company_name + " in USD",
            'font': {
                'size': 22,
                'color': '#B3B3B3'
            }
        },
        # specify buttons for the user and map different time periods to them 
        xaxis=dict(
            title="Date",
            tickformat='%d/%m/%Y',
            showgrid=False,
            rangeselector=dict(
                buttons=list([
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ]),
                bgcolor="#27374D"
            ),
            # add a rangeslider
            rangeslider=dict(
                visible=True,
                thickness=0.1
            ),
            type="date"
        ),
        # add a axis descritpion hardcoded
        yaxis=dict(
            title="Price (USD)",
            tickprefix="$",
            showgrid=False
        ),
        # define the size of the chart
        margin=dict(l=20, r=60, t=100, b=40),
        plot_bgcolor='#27374D',
        paper_bgcolor='#27374D',
        font=dict(color='#B3B3B3')
    )

    # add a dynamic range slide to the x axis based on the visible data
    fig.update_xaxes(rangeslider=dict(visible=True))
    fig.update_layout(xaxis_rangeslider_visible=False)

    # convert the Plotly figure to htmal and populate it on the response.hmtl page
    chart = fig.to_html(full_html=False)
    
    return chart

# home page on which the user can select a stock picker in the the input form
@app.route("/")
def home():
    return render_template("home.html", ticker_data=ticker_data)

# response page visualizing the data retrieved from yahoo finance in a candlestick chart
@app.route("/response", methods=["POST"])
def response():

    # send a post request with the user input which is a yahoo finance ticker symbol
    if request.method == "POST":
        ticker_input = request.form["ticker"]
        processed_input = ticker_input.upper().split(" - ")[-1].upper()
        
        # error message if input is invalid
        if processed_input not in ticker_data:
            flash("No data available for the specified ticker symbol.")
            return redirect(url_for("home"))

        # retrieve data from yahoo finance with specified ticker symbol set as variable processed_input
        data = yf.download(processed_input)
        yticker = yf.Ticker(processed_input)


        # retrieving the company information "longName" for the sent ticker symbol, exception for invalid inputs, e.g. from tickers.txt
        try:
            company_name = yticker.info["longName"]
            
        except:
            flash("No data available for the specified ticker symbol.")
            return redirect(url_for("home"))
        
        # convert the Plotly figure to html and populate it on the response.hmtl page
        chart = build_chart(data, company_name)
        return render_template("response.html", chart=chart, ticker_data=ticker_data)

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run()

