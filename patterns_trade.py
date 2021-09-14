import config
import websocket
import json
import time
import gather_data
import candle
import market
import helper

mk = market.Market()

print("Trends to look for")
winningTrends = gather_data.get_winning_trends('ETHUSDT')
print("Number of winning trends:", len(winningTrends))
print('********************************')
print('********************************')

barMap = {}               # map of symbols->list of list of candles
for pairToAdd in config.pairsToTrade:
    barMap[pairToAdd.lower()] = []


def process_bars_for_trade(symbol):
    if symbol not in barMap.keys():
        return False
    if len(barMap[symbol]) == 3:
        candleList = (candle.Candle(), candle.Candle())

        candleList[0].candleStick = barMap[symbol][1]
        candleList[0].leadingCandleStick = barMap[symbol][0]
        candleList[0].determine_classification()
        candleList[0].determine_direction()
        candleList[0].determine_volume_change()

        candleList[1].candleStick = barMap[symbol][2]
        candleList[1].leadingCandleStick = barMap[symbol][1]
        candleList[1].determine_classification()
        candleList[1].determine_direction()
        candleList[1].determine_volume_change()

        for c in candleList:
            print(c.classification, c.direction)

        if candleList in winningTrends:
            print('WINNER')
            return mk.buy_coin_possible(symbol.upper(), 5)
        print('**************************************************')

    return False


def on_message(ws, msg):
    jsonMsg = json.loads(msg)

    if 'e' in jsonMsg.keys() and jsonMsg['e'] == 'kline':
        ticker = str(jsonMsg['s']).lower()
        if ticker in barMap.keys():
            newBar = False

            if len(barMap[ticker]) == 0:
                barMap[ticker].append(helper.stream_kline_to_struct_kline(jsonMsg['k']))
                return
            elif barMap[ticker][-1][candle.TIMESTAMP_INDEX] == jsonMsg['k']['t']:
                barMap[ticker][-1] = helper.stream_kline_to_struct_kline(jsonMsg['k'])
            elif barMap[ticker][-1][candle.TIMESTAMP_INDEX] != jsonMsg['k']['t']:
                barMap[ticker].append(helper.stream_kline_to_struct_kline(jsonMsg['k']))
                newBar = True

            # only keep 3 bars in storage because that's all we need
            if len(barMap[ticker]) > 3:
                barMap[ticker].pop(0)

            # only look on 3 bars
            if len(barMap[ticker]) != 3:
                return

            # check for patterns if we don't have a new bar and it's in the last 7 seconds of the 1m bar
            if not newBar and int(time.time() * 1000) - int(barMap[ticker][-1][candle.TIMESTAMP_INDEX]) > 50000:
                tradeMade = process_bars_for_trade(ticker)

                # if a trade was made, reset everything and cool down for a bit and let our buffers fill up again
                if tradeMade:
                    barMap[ticker] = []
    else:
        print(msg)


print('Starting stream')
streamString = f'wss://stream.binance.com:9443/ws'
for pairToStream in config.pairsToTrade:
    streamString += f'/{(pairToStream.lower())}@kline_1m'

ws = websocket.WebSocketApp(streamString, on_message=on_message)
ws.run_forever()
