# NFT Loan Appraisal Algorithm

This is the backend server which runs appraisal algorithms for a propsective NFT loan denoted by collection address and token ID. There are two components to this appraisal:

## Recommended Loan-to-Value Ratio

Here, we predict the probability that the floor price of the NFT collection drops below a given percentage of the current floor price by the loan maturity. 

Technology used:
- Reservoir API to obtain historical NFT collection floor prices aggregated across different NFT exchanges (OpenSea, X2Y2, LooksRare).
- Calculates volatility over lookback window of 30 days.
- Uses Stochastic Brownian Motion model (commonly used in options pricing) to calculate probability of floor price breaching a given percentage (e.g. 20%) by a given time
- Recommends loan-to-value ratio so that the probability of collateral (floor price) falling below loan amount is 20% (a parameter that can be tweaked depending on risk tolerance)




