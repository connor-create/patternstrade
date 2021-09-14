from binance.client import Client
from binance import exceptions
import time
import config

makerFee = .0008
takerFee = .0008


class Market:
    def __init__(self):
        self.client = Client(api_key=config.apiKey, api_secret=config.apiSecret, tld='us')

    def buy_coin_possible(self, symbol, percentOfEquity):
        if len(self.client.get_open_orders()):
            print("Order already open")
            return False

        symbol = symbol.upper()

        # Get equity amount of our USD
        accountValue = float(self.client.get_asset_balance("USDT")["free"])
        if accountValue < 10:
            print("Account value error:", accountValue, "USDT")
            return False
        if accountValue < 500:
            print("You lost too much money today", accountValue, "USDT")
            return False

        # calculate how much of the symbol that is
        moneyToSpend = percentOfEquity * accountValue / 100.0
        symbolQuantity = moneyToSpend / float(self.client.get_symbol_ticker(symbol=symbol)["price"])

        # set the limit buy so we get it at the price we want hopefully
        order = None
        try:
            order = self.client.order_market_buy(
                symbol=symbol,
                quantity="{:0.0{}f}".format(symbolQuantity, 3),
            )
        except exceptions.BinanceAPIException as e:
            print(e)
            return False

        # wait 2 seconds.  usually small orders will go through immediately but if this scales it wouldn't
        time.sleep(.5)

        # see if it went through at our price, otherwise cancel it
        if order is not None:
            for openOrder in self.client.get_open_orders():
                if order["orderId"] == openOrder["orderId"]:
                    self.client.cancel_order(symbol=symbol, orderId=order["orderId"])
                    print("Could not fill", order)
                    return False

        # calculate the takeprofit and stoploss price
        actualBuyPrice = float(order['fills'][0]['price'])
        actualBuyQuantity = float(order['fills'][0]['qty']) * .98
        endProfitPrice = actualBuyPrice + actualBuyPrice * .0030
        stopLossPrice = actualBuyPrice - actualBuyPrice * .0060
        try:
            order = self.client.order_oco_sell(
                symbol=symbol,
                quantity="{:0.0{}f}".format(actualBuyQuantity, 3),
                price="{:0.0{}f}".format(endProfitPrice, 2),
                stopPrice="{:0.0{}f}".format(stopLossPrice + .01, 2),
                stopLimitPrice="{:0.0{}f}".format(stopLossPrice, 2),
                stopLimitTimeInForce='GTC'
            )
        except exceptions.BinanceAPIException as e:
            print(e)
            return False

        return True


    def get_symbol_price(self, symbol):
        recentTrades = self.client.get_recent_trades(symbol=symbol)
        lastTrade = {}

        for trade in recentTrades:
            if lastTrade == {} or int(trade["time"]) > int(lastTrade["time"]):
                lastTrade = trade

        return float(lastTrade["price"])
