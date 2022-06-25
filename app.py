from flask import Flask, request
import numpy as np
import pandas as pd
import requests
from datetime import datetime
import time
import utils
from scipy import stats

app = Flask(__name__)

rolling_vol_window = 30

@app.route('/hello/', methods=['GET', 'POST'])
def welcome():
    return "Hello World!"

@app.route('/getLTV/', methods=['GET'])
def getLTV():
    address = request.args.get('address') if request.args.get('address') else '0xf87e31492faf9a91b02ee0deaad50d51d56d5d4d'
    loan_time = int(request.args.get('loanTime')) if request.args.get('loanTime') else 30
    desired_liquidation_prob = float(request.args.get('liquidationProb')) if request.args.get('liquidationProb') else 0.25
    df = pd.DataFrame([1,2,3])
    start_date = datetime(2022, 1, 1)
    out = utils.get_historical_collection_floor(address, start_date = start_date, limit = 1000)
    floor_asks_df = utils.process_floor_price_data(out)
    last_vol, last_price = utils.get_rolling_volatility(floor_asks_df, rolling_vol_window)
    params = {'price_now': last_price, 'volatility': last_vol, 'time': loan_time, 'probability': desired_liquidation_prob}
    rec_ltv, liquidation_prob = utils.get_rec_ltv_ratio(params)
    rec_loan_amount = rec_ltv * last_price

    return {'collection_address': address, 'current_price': last_price, 'volatility': last_vol, 'loan_time': loan_time,
            'rec_ltv': rec_ltv, 'rec_loan_amount': rec_loan_amount, 'liquidation_prob': liquidation_prob}

if __name__ == "__main__":
    app.run()