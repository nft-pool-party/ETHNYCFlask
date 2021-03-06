from flask import Flask, request
import numpy as np
import pandas as pd
import requests
from datetime import datetime
import time
import utils
from scipy import stats
from flask_cors import CORS, cross_origin
import math
import statistics
from dateutil.relativedelta import relativedelta, MO
from datetime import timedelta
from scipy.stats.stats import pearsonr   


app = Flask(__name__)
CORS(app)
#app.config['CORS_HEADERS'] = 'Content-Type'

rolling_vol_window = 30
BASE_RATE = 8

@app.route('/', methods=['GET', 'POST'])
@cross_origin()
def welcome():
    return "Hello World!"


# def getLTVSingle(address, start_date, limit = 1000):
#     out = utils.get_historical_collection_floor(address, start_date = start_date, limit = 1000)
#     floor_asks_df = utils.process_floor_price_data(out)
#     last_vol, last_price = utils.get_rolling_volatility(floor_asks_df, rolling_vol_window)
#     params = {'price_now': last_price, 'volatility': last_vol, 'time': loan_time, 'probability': desired_liquidation_prob}
#     rec_ltv, liquidation_prob = utils.get_rec_ltv_ratio(params)
#     rec_loan_amount = rec_ltv * last_price

#     return {'collection_address': address, 'current_price': last_price, 'volatility': last_vol, 
#             'rec_ltv': rec_ltv, 'rec_loan_amount': rec_loan_amount}

@app.route('/getLTV', methods=['GET'])
@cross_origin()
def getLTV():
    address = request.args.get('address').lower() if request.args.get('address') else '0xf87e31492faf9a91b02ee0deaad50d51d56d5d4d'
    loan_time = int(request.args.get('loanTime')) if request.args.get('loanTime') else 30
    desired_liquidation_prob = float(request.args.get('liquidationProb')) if request.args.get('liquidationProb') else 0.25
    start_date = datetime(2022, 1, 1)
    out = utils.get_historical_collection_floor(address, start_date = start_date, limit = 1000)
    floor_asks_df = utils.process_floor_price_data(out)
    last_vol, last_price = utils.get_rolling_volatility(floor_asks_df, rolling_vol_window)
    params = {'price_now': last_price, 'volatility': last_vol, 'time': loan_time, 'probability': desired_liquidation_prob}
    rec_ltv, liquidation_prob = utils.get_rec_ltv_ratio(params)
    rec_loan_amount = rec_ltv * last_price

    return {'collection_address': address, 'current_price': last_price, 'volatility': last_vol, 'loan_time': loan_time,
            'rec_ltv': rec_ltv, 'rec_loan_amount': rec_loan_amount, 'liquidation_prob': liquidation_prob}


@app.route('/getInterestRate', methods = ['GET'])
@cross_origin()
def getInterestRate():
    address = request.args.get('address').lower() if request.args.get('address') else '0xf87e31492faf9a91b02ee0deaad50d51d56d5d4d'
    tokenId = request.args.get('tokenId') if request.args.get('tokenId') else '133851'
    risk = utils.ETHNY_risk('1', address, tokenId)
    interest_rate = risk * BASE_RATE
    if interest_rate > 10.2:
        interest_rate = 10.2
    elif interest_rate < 6:
        interest_rate = 6 
    return {'collection_address': address, 'token_id': tokenId, 'risk': risk, 'interest_rate': interest_rate}


@app.route('/getLTVMultiple', methods = ['GET'])
@cross_origin()
def getLTVMultiple():
    addresses_raw = request.args.get('addressList') if request.args.get('addressList') else '0xf87e31492faf9a91b02ee0deaad50d51d56d5d4d'
    # Parse the comma-separated list of addresses
    addresses = addresses_raw.split(',')
    print(addresses)
    return  {'address0': addresses[0], 'address1': addresses[1]}



if __name__ == "__main__":
    app.run()