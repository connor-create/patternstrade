import enum

# For indexing in candlesticks
TIMESTAMP_INDEX = 0
OPEN_INDEX = 1
HIGH_INDEX = 2
LOW_INDEX = 3
CLOSE_INDEX = 4
VOLUME_INDEX = 5


# Models for types of candlesticks
class Classification(enum.Enum):
    unclassified = 0
    big = 1
    small = 2
    doji = 3
    dragonfly_doji = 4
    gravestone_doji = 5
    hanging_man = 6
    hammer = 7
    inverted_hammer = 8
    spinning_top = 9
    shaven_head = 10
    shaven_bottom = 11
    marubozu = 12


# Defined by open price -> close price. stagnant is less than .02% change
class Direction(enum.Enum):
    bullish = 0
    bearish = 1
    stagnant = 2


# Change in volume from previous bar.   stagnant is less than 2% change
class DeltaVolume(enum.Enum):
    increasing = 0
    decreasing = 1
    stagnant = 2


# Combines all classifications into one class
class Candle:
    def __init__(self):
        self.leadingCandleStick = {}
        self.candleStick = {}
        self.classification = Classification.unclassified
        self.direction = Direction.stagnant
        self.volumeChange = DeltaVolume.stagnant

    def __eq__(self, other):
        # Do not compare candlesticks
        return self.classification == other.classification

    def __hash__(self):
        return hash(self.classification)

    def determine_classification(self):
        highSolid = float(self.candleStick[CLOSE_INDEX])
        lowSolid = float(self.candleStick[OPEN_INDEX])
        if float(self.candleStick[OPEN_INDEX]) > float(self.candleStick[CLOSE_INDEX]):
            highSolid = float(self.candleStick[OPEN_INDEX])
            lowSolid = float(self.candleStick[CLOSE_INDEX])

        openCloseSize = abs(float(self.candleStick[OPEN_INDEX]) - float(self.candleStick[CLOSE_INDEX]))
        highLowSize = abs(float(self.candleStick[HIGH_INDEX]) - float(self.candleStick[LOW_INDEX]))
        topWickSize = abs(float(self.candleStick[HIGH_INDEX]) - highSolid)
        bottomWickSize = abs(lowSolid - float(self.candleStick[LOW_INDEX]))

        # Make sure bar is substantial
        if highLowSize < highSolid * .004:
            self.classification = Classification.small

        # Big
        if topWickSize > 0 and bottomWickSize > 0:
            if topWickSize < openCloseSize * .15 and bottomWickSize < openCloseSize * .15:
                self.classification = Classification.big
                return

        # Dojis
        if openCloseSize < highLowSize * .15:
            if topWickSize > openCloseSize * 5 and bottomWickSize > openCloseSize * 5:
                self.classification = Classification.doji
                return
            if bottomWickSize > highLowSize * .70:
                self.classification = Classification.dragonfly_doji
                return
            if topWickSize > highLowSize * .70:
                self.classification = Classification.gravestone_doji
                return

        # Hanging Man
        if topWickSize == 0 and bottomWickSize > 0:
            if openCloseSize <= highLowSize * .40:
                if openCloseSize >= highLowSize * .20:
                    self.classification = Classification.hanging_man
                    return

        # Hammer
        if topWickSize < highLowSize * .1:
            if openCloseSize <= highLowSize * .40:
                self.classification = Classification.hammer
                return

        # Inverted Hammer
        if bottomWickSize < highLowSize * .1:
            if openCloseSize <= highLowSize * .40:
                self.classification = Classification.hammer
                return

        # Spinning Top
        if topWickSize > highLowSize * .15:
            if bottomWickSize > highLowSize * .15:
                self.classification = Classification.spinning_top
                return

        # Shaven Head
        if topWickSize == 0:
            if highLowSize * .70 > openCloseSize > highLowSize * .30:
                self.classification = Classification.shaven_head
                return

        # Shaven Bottom
        if bottomWickSize == 0:
            if highLowSize * .70 > openCloseSize > highLowSize * .30:
                self.classification = Classification.shaven_bottom
                return

        # Marubozu
        if bottomWickSize == 0 and topWickSize == 0:
            self.classification = Classification.marubozu
            return

        self.classification = Classification.unclassified
        return

    def determine_direction(self):
        if (abs(float(self.candleStick[OPEN_INDEX]) - float(self.candleStick[CLOSE_INDEX])) / float(self.candleStick[OPEN_INDEX])) <= .0002:
            self.direction = Direction.stagnant
        elif float(self.candleStick[OPEN_INDEX]) > float(self.candleStick[CLOSE_INDEX]):
            self.direction = Direction.bearish
        else:
            self.direction = Direction.bullish

    def determine_volume_change(self):
        if float(self.candleStick[VOLUME_INDEX]) < .01:
            self.volumeChange = DeltaVolume.decreasing
        elif (abs(float(self.candleStick[VOLUME_INDEX]) - float(self.leadingCandleStick[VOLUME_INDEX])) / float(self.candleStick[VOLUME_INDEX])) <= .05:
            self.volumeChange = DeltaVolume.stagnant
        elif float(self.candleStick[VOLUME_INDEX]) > float(self.leadingCandleStick[VOLUME_INDEX]):
            self.volumeChange = DeltaVolume.increasing
        else:
            self.volumeChange = DeltaVolume.decreasing

