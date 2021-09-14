

def stream_kline_to_struct_kline(bar):
    klineList = [float(bar['t']), float(bar['o']), float(bar['h']), float(bar['l']), float(bar['c']), float(bar['v'])]
    return klineList
