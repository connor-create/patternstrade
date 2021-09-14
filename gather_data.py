from binance.client import Client
from binance import enums
import config
import candle


def get_winning_trends(symbol):
    client = Client(config.apiKey, config.apiSecret, tld='us')

    winningTrends = {}              # Stores the determined trends from first pass, list of lists of candles (length of numOfCandlesToLookFor)
    totalTrends = {}                # Stores total trends amount, winning and losing

    # Get Historical Klines
    oneMinData = client.get_historical_klines(symbol=symbol, interval=enums.KLINE_INTERVAL_1MINUTE, start_str='1609542363000',
                                               klines_type=enums.HistoricalKlinesType.SPOT)

    # Look for areas where price increases in a way we want it to
    for x in range(len(oneMinData)):
        if x < 10:
            continue
        if x == len(oneMinData) - 10:
            break

        barsToCheck = [oneMinData[x], oneMinData[x + 1], oneMinData[x + 2], oneMinData[x + 3], oneMinData[x + 4], oneMinData[x + 5],
                       oneMinData[x + 6], oneMinData[x + 7], oneMinData[x + 8], oneMinData[x + 9], oneMinData[x + 10]]
        buyPrice = float(barsToCheck[0][candle.CLOSE_INDEX])
        takeProfitPrice = buyPrice + buyPrice * .0030
        stopLossPrice = buyPrice - buyPrice * .0060
        takeProfitHit = False
        stopLossHit = False
        for z in range(len(barsToCheck)):
            if z == 0:
                continue
            if float(barsToCheck[z][candle.LOW_INDEX]) <= stopLossPrice:
                stopLossHit = True
                break
            if float(barsToCheck[z][candle.HIGH_INDEX]) >= takeProfitPrice:
                takeProfitHit = True
                break

        # If no target was hit, then make it a loss
        if not takeProfitHit and not stopLossHit:
            stopLossHit = True

        # Add to the list of candles
        if takeProfitHit:
            candleList = [candle.Candle(), candle.Candle()]

            candleList[0].candleStick = oneMinData[x-1]
            candleList[0].leadingCandleStick = oneMinData[x-2]
            candleList[0].determine_classification()
            candleList[0].determine_direction()
            candleList[0].determine_volume_change()

            candleList[1].candleStick = oneMinData[x]
            candleList[1].leadingCandleStick = oneMinData[x-1]
            candleList[1].determine_classification()
            candleList[1].determine_direction()
            candleList[1].determine_volume_change()

            # if candleList[0].classification == candle.Classification.unclassified or \
            #    candleList[1].classification == candle.Classification.unclassified or \
            #     continue

            if tuple(candleList) in winningTrends.keys():
                winningTrends[tuple(candleList)] += 1
            else:
                winningTrends[tuple(candleList)] = 1

    filteredWinningTrends = []
    print(len(winningTrends.keys()))

    for pt in winningTrends.keys():
        totalTrends[tuple(pt)] = 0

    # calculate total trends for all bars
    for y in range(len(oneMinData)):
        if y + 2 >= len(oneMinData):
            break

        tempBarList = [candle.Candle(), candle.Candle()]
        tempBarList[0].candleStick = oneMinData[y]
        tempBarList[0].leadingCandleStick = oneMinData[y - 1]
        tempBarList[0].determine_classification()
        tempBarList[0].determine_direction()
        tempBarList[0].determine_volume_change()

        tempBarList[1].candleStick = oneMinData[y + 1]
        tempBarList[1].leadingCandleStick = oneMinData[y]
        tempBarList[1].determine_classification()
        tempBarList[1].determine_direction()
        tempBarList[1].determine_volume_change()

        if tuple(tempBarList) in totalTrends.keys():
            totalTrends[tuple(tempBarList)] += 1

    # compare and return winners
    for trend in winningTrends.keys():
        numWinningOccurrences = winningTrends[trend]
        numTotalOccurrences = totalTrends[trend]
        print(numWinningOccurrences, numTotalOccurrences)

        if float(numWinningOccurrences) >= (float(numTotalOccurrences) * .50):
            # for t in trend:
            #     print(t.classification, t.direction, t.volumeChange)
            # print('**************************************************************************')
            filteredWinningTrends.append(trend)

    return filteredWinningTrends
