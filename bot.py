import websocket, json, pprint
import config #file containing personal API keys
from binance.client import Client
from binance.enums import *

#1 minute candlestick
SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m" 

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYBOL = "ETHUSD"
TRADE_QUANTITY = 0.05

closes = []
in_position = False

#tld for usa (american binance)
#Python binance client
client = Client(config.API_KEY, config.API_SECRET, tld="us")

def order(side, quantity, symbol, order_type = ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol = symbol, side = side, type = order_type, quantity = quantity)
        print(order)
    except Exception as e:
        return False

    return True

def on_open(ws):
    print("opened connection")

def on_close(ws):
    print("closed connection")

def on_message(ws, message):
    global closes

    print("recieved message")
    #print(message)
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message["k"]

    is_candle_closed = candle["x"]
    close = candle["c"]

    #retrieve closing candlestick/final price when x is true
    if is_candle_closed:
        print("candle closed at {}".format(close))
        #continuously append closing prices to our list
        closes.append(float(close))
        print("closes")
        print(closes)

        #need at least 15 closes
        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD0)
            print("all rsi calculated so far")
            print(rsi)
            last_rsi = rsi(-1)
            print("the current rsi is{}".format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT:
                #print("SELL")
                if in_position:
                    print("SELL")
                    order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYBOL)
                    if order_succeeded:
                        in_position = False
                else:
                    print("Overbought, but none owned. no execution.")
                    order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYBOL)
                    if order_succeeded:
                        in_position = True

            if last_rsi > RSI_OVERSOLD:
                #print("BUY")
                if in_position:
                    print("Oversold, but already owned. no execution.")
                else:
                    print("BUY")
            

ws = websocket.WebSocketApp(SOCKET, on_open = on_open, on_close = on_close, on_message = on_message) 
ws.run_forever()