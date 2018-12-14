from flask import Flask, request, jsonify, Response
import os
from flask import g
import sqlite3
import json
import threading
import time
from werkzeug.utils import secure_filename
import apikeys
from  textblob import TextBlob
import re
import oauth2 as oauth
import logging
import urllib2 as urllib
from os import environ

app = Flask(__name__)
DATABASE = "demp.db"
priceIndex=400.000

# ------------------------------------------
# -logging stuff
logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )
# ------------------------------------------



# create a database if it is not existing already in the folder
if not os.path.exists(DATABASE):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("CREATE TABLE buy_coins (recv_address varchar(256), quantity int, price varchar(20));")
    cur.execute("CREATE TABLE sell_coins (sender_address varchar(256), quantity int, price varchar(20));")
    cur.execute("CREATE TABLE matched_txn (sender_address varchar(256), recv_address varchar(256),quantity int, price varchar(20));")
    cur.execute("CREATE TABLE sell_txn(sender_address varchar(256), recv_address varchar(256),quantity int, price varchar(20));")
    cur.execute("CREATE TABLE buy_txn(sender_address varchar(256), recv_address varchar(256),quantity int, price varchar(20));")
    cur.execute("CREATE TABLE verify(address varchar(256), bool int);")
    conn.commit()
    conn.close()

# ------------------------------------------------------------------------------------------------------
# twitter api connection
# ------------------------------------------------------------------------------------------------------

class twitter:
    # twitter application credentials
    consumer_key = apikeys.consumer_key
    consumer_secret = apikeys.consumer_secret
    access_token_key = apikeys.access_token_key
    access_token_secret = apikeys.access_token_secret
    # credentials end

    #  default http_header to be passes is NONE and post_body is a blank string

    _debug = 0

    oauth_token    = oauth.Token(key=access_token_key, secret=access_token_secret)
    oauth_consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)

    signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()

    http_method = "GET"


    http_handler  = urllib.HTTPHandler(debuglevel=_debug)
    https_handler = urllib.HTTPSHandler(debuglevel=_debug)

    # def __init__(self):
    #     print "yo"

    # Construct, sign, and open a twitter request
    # using the hard-coded credentials above.

    def twitterreq(self,url, method, parameters):
        req = oauth.Request.from_consumer_and_token(twitter.oauth_consumer,
                                                    token=twitter.oauth_token,
                                                    http_method=twitter.http_method,
                                                    http_url=url,
                                                    parameters=parameters)

        req.sign_request(twitter.signature_method_hmac_sha1, twitter.oauth_consumer, twitter.oauth_token)

        headers = req.to_header()

        if twitter.http_method == "POST":
            encoded_post_data = req.to_postdata()
        else:
            encoded_post_data = None
            url = req.to_url()

        opener = urllib.OpenerDirector()
        opener.add_handler(twitter.http_handler)
        opener.add_handler(twitter.https_handler)

        response = opener.open(url, encoded_post_data)

        return response



# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------
# sentiment analysis code for twitter
# ------------------------------------------------------------------------------------------------------
def clean_tweet(tweet):
    # Utility function to clean tweet text by removing links, special characters
    # using simple regex statements.
    #
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])| (\w+:\ / \ / \S+)", " ", tweet).split())

# defining a global sentiment variable to be accessed from antwhere
sentiment=0
# Defining a background function which will run in thread to take and monotoe tweets in realtime
def getTwitterSentiments():
    try:
        logging.debug('Starting')
        global sentiment
        twit_req=twitter()
        url = "https://stream.twitter.com/1.1/statuses/filter.json?track=bitcoin"
        parameters = []
        response = twit_req.twitterreq(url, "GET", parameters)
        for line in response:
            try:
                twit_content=json.loads(line)["text"]
                analysis = TextBlob(clean_tweet(twit_content))
                sentiment+=analysis.sentiment.polarity
                # print sentiment
                time.sleep(1)
            except ValueError:
                logging.debug("ValueErrorCaught")
                del twit_req
                getTwitterSentiments()
        logging.debug('sentiment crashed')
    except Exception as e:
        del twit_req
        logging.debug('sentiment crashed outside')
        getTwitterSentiments()


# ------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------



# a matcher thread which matches transactions after a fixed interval of time
def buy_sell_match():
    logging.debug('Matcher Started')
    with app.app_context():
        time.sleep(60)
        while True:
            try:
                cur = get_db().cursor()
                cur2=get_db().cursor()
                res = cur.execute("Select bc.recv_address, sc.sender_address, sc.quantity, bc.price, sc.price from sell_coins as sc inner join buy_coins as bc where sc.quantity=bc.quantity")
                for row in res:
                    if(abs(float(row[3])-float(row[4]))<1):
                        cur2.execute("Insert into matched_txn values(?,?,?,?)",(row[1],row[0],row[2], row[4]))
                        cur2.execute("Insert into sell_txn values(?,?,?,?)", (row[1], row[0], row[2], row[4]))
                        cur2.execute("Insert into buy_txn values(?,?,?,?)", (row[1], row[0], row[2], row[4]))
                        cur2.execute("Delete from buy_coins where recv_address=? AND quantity=? AND price=?",(row[0],row[2],row[3]))
                        cur2.execute("Delete from sell_coins where sender_address=? AND quantity=? AND price=?",(row[1],row[2],row[4]))
                        get_db().commit()
            except Exception as e:
                logging.debug('Exception in Matcher'+str(e))
                exit()
    logging.debug('Matcher Crashed')
    buy_sell_match()



#Start sentiment thread in background in python
try:
    gts= threading.Thread(name="sentiments", target= getTwitterSentiments)
    gts.setDaemon(True)
    gts.start()
    bsm = threading.Thread(name="BuySellMatch", target=buy_sell_match)
    bsm.setDaemon(True)
    bsm.start()
    # thread.start_new_thread( getTwitterSentiments, ("Start",) )
    # thread.start_new_thread(buy_sell_match(), ("Start",))
except:
    print "Error: unable to start thread"



# Create Connection with Database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


# CLose Connection with database
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()



# Initialize Database from python shell for the 1st time
# >>> from yourapplication import init_db
# >>> init_db()
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# endpoint to buy coins
@app.route("/buy", methods=["POST"])
def receive_coins():
    try:
        recv_address = request.json['address']
        quantity = request.json['quantity']
        amount= request.json['amount']
        # print recv_address
        # print quantity
        cur=get_db().cursor()
        res= cur.execute("INSERT into buy_coins values(?,?,?)",(recv_address,int(quantity),amount))
        get_db().commit()
        return Response(status=200)
    except Exception as e:
        print (e)
        return Response(status=510)
#     Response(js, status=200, mimetype='application/json')

# endpoint to sell coins
@app.route("/sell", methods=["POST"])
def sell_coins():
    try:
        sender_address = request.json['address']
        quantity = request.json['quantity']
        amount= request.json['amount']
        cur=get_db().cursor()
        res= cur.execute("INSERT into sell_coins values(?,?,?);",(sender_address,int(quantity),amount))
        get_db().commit()
        return Response(status=200)
    except:
        return Response(status=500)
#     Response(js, status=200, mimetype='application/json')


# endpoint asked by buyer for a match
# will ask every 10 seconds for request
# after 10 min will expire-->set this in java to delete
@app.route("/buymatched", methods=["POST"])
def sell_match():
    try:
        recv_address = request.json['address']
        cur = get_db().cursor()
        res = cur.execute("Select sender_address, quantity, price from buy_txn where recv_address=? Limit 1",(recv_address, ))
        for row in res:
            items = {}
            items['recv_from'] = str(row[0])
            items['quantity'] = int(row[1])
            items['price'] = str(row[2])
            return Response(json.dumps(items), status=200, mimetype='application/json')
        return Response(status=550)
    except Exception as e:
        print e
        return Response(status=590)


# endpoint asked by a seller for a match
# will ask every 10 seconds for request
# after 10 min will expire---->set this in java to delete
@app.route("/sellmatched", methods=["POST"])
def buy_match():
    try:
        sender_address = request.json['address']
        cur = get_db().cursor()
        res = cur.execute("Select recv_address, quantity, price from sell_txn where sender_address=? limit 1", (sender_address, ))
        for row in res:
            # logging.debug(row)
            items = {}
            items['send_to'] = str(row[0])
            items['quantity'] = int(row[1])
            items['price'] = str(row[2])
            return Response(json.dumps(items), status=200, mimetype='application/json')

        return Response(status=550)
    except:
        return Response(status=510)


prevMultiplier=0
polar=0
@app.route("/dynamicPrice", methods=["GET"])
def sendDynamicPrice():
    global priceIndex
    global sentiment
    global prevMultiplier
    global polar
    try:
        cur = get_db().cursor()
        items_buy=cur.execute("Select count(*) from buy_coins;").fetchone()[0]
        items_sell=cur.execute("Select count(*) from sell_coins;").fetchone()[0]
        if(items_sell!=0 and items_sell!=0):
            ratio=float(items_buy)/float(items_sell)
        else:
            ratio=1.000
        multiplier= float(sentiment)*float(ratio)
        if(multiplier>prevMultiplier):
            polar=1
        if(multiplier<prevMultiplier):
            polar=-1
        prevMultiplier=multiplier
        priceIndex=(polar*float(priceIndex)*float(abs(multiplier))*0.000001)+float(priceIndex)
        # print multiplier
        items = {}
        items['Price']= priceIndex
        return Response(json.dumps(items), status=200, mimetype='application/json')

    except Exception as e:
        logging.debug("Error in Dynamic Price"+str(e))
        return Response(status=430)



@app.route("/sendVerify", methods=["POST"])
def sendVerify():
    try:
        address = request.json['address']
        bool = request.json['bool']
        cur = get_db().cursor()
        if (int(bool)==0):
            res=cur.execute("Update verify SET bool=? where address=?;", (int(bool), address))
        else:
            res = cur.execute("Update verify SET bool=? where address=?;", (int(bool), address))
            if not res.rowcount:
                res = cur.execute("INSERT into verify values(?,?);", (address, int(bool)))
                # print ("inside")
        get_db().commit()
        return Response(status=200)

    except Exception as e:
        logging.debug("Error in send Verify"+str(e))
        return Response(status=430)


@app.route("/recVerify", methods=["POST"])
def recVerify():
    try:
        address = request.json['address']
        cur = get_db().cursor()
        res = cur.execute("Select bool from verify where address=? LIMIT 1;", (address,))
        for row in res:
            items = {}
            items['bool'] = int(row[0])

            return Response(json.dumps(items), status=200, mimetype='application/json')
        return Response(status=430)
    except Exception as e:
        logging.debug("Error in receive Verify" + str(e))
        return Response(status=430)


@app.route("/delsel", methods=["POST"])
def delsel():
    try:
        address = request.json['address']
        cur = get_db().cursor()
        res = cur.execute("Delete from sell_txn where sender_address=? ", (address,))
        # res.rowcount
        get_db().commit()
        if res.rowcount>0:
            return Response( status=200)
        return Response(status=430)
    except Exception as e:
        logging.debug("Error in receive Verify" + str(e))
        return Response(status=490)

@app.route("/delbuy", methods=["POST"])
def delbuy():
    try:
        address = request.json['address']
        cur = get_db().cursor()
        res = cur.execute("Delete from buy_txn where recv_address=? ", (address,))
        # res.rowcount
        get_db().commit()
        if res.rowcount>0:
            return Response( status=200)
        return Response(status=430)
    except Exception as e:
        logging.debug("Error in receive Verify" + str(e))
        return Response(status=490)




if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0',port=5050)