# Dynamic Currency Pricing API

This project contains the following functionality:
1. Transaction Matching Algorithm
2. Coin Pricing Algorithm
3. Verification Backend



#### Transaction Matching Algorithm:
Created a thread that ran the Transacton Mathing every minute. Used SQLITE3 to store all the transactions.
Following Tables were created.
1. Buy_coins
2. Sell_couns
3. matched_txn + sell_txn + buy_txn<br/>
    Transacton matched and stored for users to query and retreive

Used Python-Flask and deployed on heroku/AWS-EBS<br/>


#### Coin Pricing Algorithm:
Dynamically price the coin according to to the current market sentiment(Twitter) and demand and supply gap.

##### Market Sentiment:
* Positive news increased the price, negative decrease it.
* Weights are given to user<br/>
        - If verified account/celebrities -> More Impact <br/>
        - If Followers>Following -> Impact according to ratio <br/>
        - If Following>Followers -> Less or negligible impact because can be spam accounts
* Created custom formula so that prices are stable and not fluctuating randomly or frequently in minutes.


#### Verification Backend:
Used a combination of python-flask and AWS S3
* Documents of users uploaded to AWS S3 and verification set through python flask on heroku/AWS-EBS
* Verification admin manually verified users and sent verification confirmation


##### Pricing Algorithm and Matching algorithm are running as daemon threads 