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

def get_historical_collection_floor(collection_address, start_date, limit=None):
  start_date_unix = time.mktime(start_date.timetuple())
  if limit is not None :
    url = f"https://api.reservoir.tools/events/collections/floor-ask/v1?collection={collection_address}&startTimestamp={start_date_unix}&sortDirection=desc&limit={limit}"
  else:
    url = f"https://api.reservoir.tools/events/collections/floor-ask/v1?collection={collection_address}&startTimestamp={start_date_unix}&sortDirection=desc"
  headers = {
      "Accept": "*/*",
      "x-api-key": "demo-api-key"
  }
  response = requests.get(url, headers=headers)
  out = response.json()
  return out

def process_floor_price_data(out):

  floor_asks = []
  for event in out['events']:
    collection_ = event['event']
    floorask_ = event['floorAsk']
    floor_asks.append({'price': floorask_['price'],
                      'previousPrice': collection_['previousPrice'],
                      'source': floorask_['source'],
                      'tokenId': floorask_['tokenId'],
                      'createdAt': collection_['createdAt'],
                      'validUntil': floorask_['validUntil']})

  floor_asks_df = pd.DataFrame(floor_asks)
  floor_asks_df['validUntil'] = pd.to_datetime(floor_asks_df['validUntil'].astype(int), unit = 's')
  floor_asks_df['createdAt'] = pd.to_datetime(floor_asks_df['createdAt'])
  floor_asks_df = floor_asks_df.sort_values(by = 'createdAt', ascending = False)
  return floor_asks_df

def get_rolling_volatility(floor_asks_df, rolling_vol_window):
  # Resample to get daily volatility
  a = floor_asks_df.set_index('createdAt')['price']
  floor_asks_daily = a.resample('D').median().ffill()

  rolling_vol = floor_asks_daily.pct_change().rolling(rolling_vol_window).std()
  last_vol_value = rolling_vol[-1]
  if np.isnan(last_vol_value):
    last_vol_value = 0.01

  return last_vol_value, floor_asks_daily.iloc[0]

def get_rec_ltv_ratio(params):
  liquidation_price_ratios = np.arange(0.05, 1.00, 0.05)
  probabilities = []

  for liquidation_price_ratio in liquidation_price_ratios:
    S = params['price_now']
    K = S * liquidation_price_ratio
    #K = 80
    t = params['time']
    #r = 0.1 / 365 
    r = 0
    sigma = params['volatility']

    d1 = (math.log(S/K) + (r + sigma**2 / 2) * t) / (sigma * math.sqrt(t))
    d2 = d1 - sigma * math.sqrt(t)
    # probability of ending up below this price
    prob_below_K = stats.norm(0, 1).cdf(-d2)
    probabilities.append(prob_below_K)

  diff_from_desired_probability = np.abs(np.array(probabilities) - params['probability'])
  rec_ltv_id = diff_from_desired_probability.argmin()
  rec_ltv = liquidation_price_ratios[rec_ltv_id]
  return rec_ltv, probabilities[rec_ltv_id]


### Premium
def ETHNY_risk(chain_id, contract_address, token_id):
    """output: """
    
    
    def vol_parameter(chain_id, contract_address, token_id):
    
        current_date = datetime.today()
        start_date = current_date + relativedelta(months=-6)
        
        
        
        def get_historical_collection_floor(collection_address, start_date, limit=None):
          start_date_unix = time.mktime(start_date.timetuple())
          if limit is not None :
            url = f"https://api.reservoir.tools/events/collections/floor-ask/v1?collection={collection_address}&startTimestamp={start_date_unix}&sortDirection=desc&limit={limit}"
          else:
            url = f"https://api.reservoir.tools/events/collections/floor-ask/v1?collection={collection_address}&startTimestamp={start_date_unix}&sortDirection=desc"
          headers = {
              "Accept": "*/*",
              "x-api-key": "demo-api-key"
          }
          response = requests.get(url, headers=headers)
          out = response.json()
          return out
      
        out = get_historical_collection_floor(contract_address, start_date = start_date, limit = 1000)
        
        floor_asks = []
        for event in out['events']:
          collection_ = event['event']
          floorask_ = event['floorAsk']
          floor_asks.append({'price': floorask_['price'],
                             'previousPrice': collection_['previousPrice'],
                             'source': floorask_['source'],
                             'tokenId': floorask_['tokenId'],
                             'createdAt': collection_['createdAt'],
                             'validUntil': floorask_['validUntil']})
        
        floor_asks_df = pd.DataFrame(floor_asks)
        floor_asks_df['validUntil'] = pd.to_datetime(floor_asks_df['validUntil'].astype(int), unit = 's')
        floor_asks_df['createdAt'] = pd.to_datetime(floor_asks_df['createdAt'])
        floor_asks_df = floor_asks_df.sort_values(by = 'createdAt', ascending = False)
        
        a = floor_asks_df.set_index('createdAt')['price']
        floor_asks_daily = a.resample('D').median().ffill()
        
        rolling_vol_window = 20
        rolling_vol = floor_asks_daily.pct_change().rolling(rolling_vol_window).std()
        
        current_vol = rolling_vol[-1]
        
        rolling_vol_array = np.array(rolling_vol)
        rolling_vol_array = rolling_vol_array[np.logical_not(np.isnan(rolling_vol_array))]
        
        mean_vol = statistics.mean(rolling_vol_array)
                
        vol_param = math.sqrt(current_vol/mean_vol)
        
        return(math.sqrt(vol_param))
    
    
    def crypto_nft_req_return(chain_id, collection_address, token_id):
        
        def crypto_timeseries(token, start, finish, interval):
            base_url = 'https://data.messari.io/api/v1/assets/'
            endpoint = f'{token}/metrics/price/time-series?start={start}&end={finish}&interval={interval}'
            url = base_url + endpoint
            result = requests.get(url).json()
            data = result["data"]
            return(data)
    

        nfti_df = crypto_timeseries('NFTI', '2022-06-01', '2022-06-25', '1d')
        tcap_df = crypto_timeseries('TCAP', '2022-06-01', '2022-06-25', '1d')
        
        nfti_list = []
        for i in range(len(nfti_df['values'])):
            nfti_list.append(nfti_df['values'][i][4])
            
        tcap_list = []
        for i in range(len(tcap_df['values'])):
            tcap_list.append(tcap_df['values'][i][4])
            
        var_cov_matrix = np.cov(nfti_list, tcap_list)
        
        beta = var_cov_matrix[0][1]/var_cov_matrix[1][1]
        rf = 0.0411
        rm = 0.0567
        
        req_r = rf + beta*(rm - rf)
        
        return(math.sqrt(1 + req_r))
        
    
    def nft_whitelist_verification(contract_addy, token_id):
        headers = {"X-API-KEY": "786f40019b704c9da6c95dc29540db71"}
        base_url = 'https://api.opensea.io/api/v1/asset/'
        endpoint = f'{contract_addy}/{token_id}/?include_orders=false'
        url = base_url + endpoint
        result = requests.get(url, headers = headers).json()
        
        if(result['collection']['safelist_request_status'] == 'verified'):
            white_val = 0.97
        else:
            white_val = 1.05
        
        return(white_val)
    
    
    def price_ratio(contract_addy, token_id):
        def get_contract_sales_stats(stat_args, contract_address):
        
            headers = {
                'Authorization': 'c2c3e088-d722-42f0-9b98-684efad606cf',
                'Content-Type': 'application/json',
            }
        
            params = {
                'chain': 'ethereum',
            }
        
            get_addr = 'https://api.nftport.xyz/v0/transactions/stats/'
            input_addr = f"{get_addr}{contract_address}"
            
            response = requests.get(input_addr, params=params, headers=headers)
            json_file = response.json()
            
            res = []
            
            for x in range(len(stat_args)):
                res.append(json_file['statistics'][stat_args[x]])
        
            return res
        
        seven_over_thirty_price = ['seven_day_average_price', 'thirty_day_average_price']
        
        def seven_over_thirty(args_lst, contract_address): 
            #index 0 is 7 day, index 1 is 30 day
            lst = get_contract_sales_stats(args_lst, contract_address)
            return (lst[0]/lst[1])
        
        seven_thirty_price = math.sqrt(seven_over_thirty(seven_over_thirty_price, contract_addy))
        
        return(seven_thirty_price)
    
    
    def volume_ratio(contract_addy, token_id):
        def get_contract_sales_stats(stat_args, contract_address):
        
            headers = {
                'Authorization': 'c2c3e088-d722-42f0-9b98-684efad606cf',
                'Content-Type': 'application/json',
            }
        
            params = {
                'chain': 'ethereum',
            }
        
            get_addr = 'https://api.nftport.xyz/v0/transactions/stats/'
            input_addr = f"{get_addr}{contract_address}"
            
            response = requests.get(input_addr, params=params, headers=headers)
            json_file = response.json()
            
            res = []
            
            for x in range(len(stat_args)):
                res.append(json_file['statistics'][stat_args[x]])
        
            return res
        
        seven_over_thirty_volume = ['seven_day_volume', 'thirty_day_volume'] 
        
        def seven_over_thirty(args_lst, contract_address): 
            #index 0 is 7 day, index 1 is 30 day
            lst = get_contract_sales_stats(args_lst, contract_address)
            return (lst[0]/lst[1])
    
        seven_thirty_volume = math.sqrt((1 - seven_over_thirty(seven_over_thirty_volume, contract_addy) * 7 / 30))
        
        return(seven_thirty_volume)
    
        
    
    def check_if_wash_traded(contract_address, token_id):
        headers = {
            'Authorization': 'c2c3e088-d722-42f0-9b98-684efad606cf',
            'Content-Type': 'application/json',
        }
    
        params = {
            'chain': 'ethereum',
            'type': 'transfer',
        }

        def hasDuplicate(nums, k):
             d = {}
             for i, e in enumerate(nums):
                 if e in d:
                     if i - d.get(e) <= k:
                        return True
                 d[e] = i
             return False
    
        ## sample call address
        ## https://api.nftport.xy/v0/transactions/nfts/{contract_address}/{token_id}
        ## 0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D == BAYC CONTRACT 
        ## TOKEN_ID == 7537 https://opensea.io/assets/ethereum/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d/7537
        
        get_addr = 'https://api.nftport.xyz/v0/transactions/nfts/'
        input_addr = f"{get_addr}{contract_address}/{token_id}"
        
        response = requests.get(input_addr, params=params, headers=headers)
        json = response.json()
        
        buyer_addrs = []
        seller_addrs = [] 
        
        for x in range(len(json["transactions"])):
            buyer_addrs.append(json["transactions"][x]["transfer_to"])
            seller_addrs.append(json["transactions"][x]["transfer_from"])
        
        if(hasDuplicate(buyer_addrs,2)):
            extra_val = 1.1
        if(hasDuplicate(seller_addrs,2)):
            extra_val = 1.1
        else:
            extra_val = 1.0
        
        return(extra_val)
            
        
    vol = vol_parameter(chain_id, contract_address, token_id)
    req_return = crypto_nft_req_return(chain_id, contract_address, token_id)
    whitelist = nft_whitelist_verification(contract_address, token_id)
    price_r = price_ratio(contract_address, token_id)
    volume_r = volume_ratio(contract_address, token_id)
    washed = check_if_wash_traded(contract_address, token_id)
    
    
    
    param_list = [vol, req_return, whitelist, price_r, volume_r, washed]

    
    
    
    fin_val = vol * req_return * whitelist * price_r * volume_r * washed
    
    
    
    return fin_val