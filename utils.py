import numpy as np
import pandas as pd
import requests
from datetime import datetime
import time
import math
import scipy

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
    prob_below_K = scipy.stats.norm(0, 1).cdf(-d2)
    probabilities.append(prob_below_K)

  diff_from_desired_probability = np.abs(np.array(probabilities) - params['probability'])
  rec_ltv_id = diff_from_desired_probability.argmin()
  rec_ltv = liquidation_price_ratios[rec_ltv_id]
  return rec_ltv, probabilities[rec_ltv_id]