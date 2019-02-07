# Dynamic Currency Pricing API

This project contains the following functionality:
1. Transaction Matching Algorithm
2. Coin Pricing Algorithm
3. Verification Backend



### Transaction Matching Algorithm:
Created a thread that ran the Transacton Mathing every minute. Used SQLITE3 to store all the transactions.<br/>
Following Tables were created.
1. Buy_coins
2. Sell_couns
3. matched_txn + sell_txn + buy_txn<br/>
    Transacton matched and stored for users to query and retreive

Used Python-Flask and deployed on heroku/AWS-EBS<br/>


### Coin Pricing Algorithm:
Dynamically price the coin according to to the current market sentiment(Twitter) and demand and supply gap.

##### Market Sentiment:
* Positive news increased the price, negative decrease it.
* Weights are given to user<br/>
        - If verified account/celebrities -> More Impact <br/>
        - If Followers>Following -> Impact according to ratio <br/>
        - If Following>Followers -> Less or negligible impact because can be spam accounts
* Created custom formula so that prices are stable and not fluctuating randomly or frequently in minutes.


### Verification Backend:
Used a combination of python-flask and AWS S3
* Documents of users uploaded to AWS S3 and verification set through python flask on heroku/AWS-EBS
* Verification admin manually verified users and sent verification confirmation


##### Pricing Algorithm and Matching algorithm are running as daemon threads



### API Endpoints

##### BUY
* **URL**:<br/>
 /buy
* **Method**:<br/>
  `POST`
* **URL Params**<br/>
    None
* **Data Params**<br/>
* **Success Response**<br/>
* **Error Response**<br/>

##### SELL
* **URL**:<br/>
/sell
* **Method**:<br/>
  `POST`
* **URL Params**<br/>
    None
* **Data Params**<br/>
* **Success Response**<br/>
* **Error Response**<br/>

##### BUY Matched
* **URL**:<br/>
/buymatched
* **Method**:<br/>
  `POST`
* **URL Params**<br/>
    None
* **Data Params**<br/>
* **Success Response**<br/>
* **Error Response**<br/>

##### SELL Matched
* **URL**:<br/>
/sellmatched
* **Method**:<br/>
  `POST`
* **URL Params**<br/>
    None
* **Data Params**<br/>
* **Success Response**<br/>
* **Error Response**<br/>

##### Get Dynamic Price
* **URL**:<br/>
/dynamicPrice
* **Method**:<br/>
  `GET`
* **URL Params**<br/>
    None
* **Data Params**<br/>
* **Success Response**<br/>
* **Error Response**<br/>


##### Send Verification Flag
* **URL**:<br/>
/sendVerify
* **Method**:<br/>
  `POST`
* **URL Params**<br/>
    None
* **Data Params**<br/>
* **Success Response**<br/>
* **Error Response**<br/>

##### Receive Verification Flag
* **URL**:<br/>
/recVerify
* **Method**:<br/>
  `POST`
* **URL Params**<br/>
    None
* **Data Params**<br/>
* **Success Response**<br/>
* **Error Response**<br/>


##### Sell Transaction Received
* **URL**:<br/>
/delsel
* **Method**:<br/>
  `POST`
* **URL Params**<br/>
    None
* **Data Params**<br/>
* **Success Response**<br/>
* **Error Response**<br/>

##### Buy Transaction Received
* **URL**:<br/>
/delbuy
* **Method**:<br/>
  `POST`
* **URL Params**<br/>
    None
* **Data Params**<br/>
* **Success Response**<br/>
* **Error Response**<br/>


##### Get All Transactions
* **URL**:<br/>
/getTransactions
* **Method**:<br/>
  `POST`
* **URL Params**<br/>
    None
* **Data Params**<br/>
* **Success Response**<br/>
* **Error Response**<br/>
