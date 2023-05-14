{"filter":false,"title":"utils.py","tooltip":"/Haopeng/utils.py","undoManager":{"mark":0,"position":0,"stack":[[{"start":{"row":0,"column":0},"end":{"row":92,"column":32},"action":"insert","lines":["from time import sleep","","from optibook.synchronous_client import Exchange","","import logging","logger = logging.getLogger('client')","logger.setLevel('ERROR')","","# We start our client with this utils class","# Exchange (e) and a ","","phil_A = 'PHILIPS_B'","phil_B = 'PHILIPS_A'","","e = Exchange()","a = e.connect()","","MAX_POSITIONS = 200","MAX_OUTSTANDING = 500","","def downloadOrderBook(instr):","    '''","    Returns the current bids and asks for the given instrument.","    ","    Parameters","    ------------","    instr: string","        Instrument ('PHILIPS_A' or 'PHILIPS_B').","        No assertion is done for perfomance reasons","        ","        ","    Returns","    ---------","    book.bids, book.asks : PriceVolume, PriceVolume","        Lists of `PriceVolume` objects corresponding to bids and asks for the ","        supplied instrument","    '''","    ","    book = e.get_last_price_book(instr)","    ","    return book.bids, book.asks","","def printCurrentPositions():","    '''","    Prints all current positions, plus position cash","    '''","    positions = e.get_positions_and_cash()","    for p in positions:","        print(p, positions[p])","","","def deleteAllOutstandingOrders(instrument_id, side):","    \"\"\"","    Exits all outstanding positions for the chosen instrument and order type","    ","    Parameters","    ----------","    instrument_id:  str","        Intrument ID (`PHILIPS_A` or `PHILIPS_B`) (no assertion is done ","            for perfomance)","    side: str","        string representing the types of outstanding orders we wish to close.","        Select from 'bid', 'ask', or 'all'","    Returns","    -------","    None","    \"\"\"","    outstanding = e.get_outstanding_orders(instrument_id)","    for o in outstanding.values():","        if(o.side == side or side=='all'):","            result = e.delete_order(instrument_id, order_id=o.order_id)","","def closeAllPosition(debug=False):","    '''","    Iterates and attempts to close all open positions","    ","    Parameters","    -----------","    debug : Bool","        If true, we print our current positions before and after attempting","        to close","    '''","    if(debug):","        print(\"Starting Positions: \")","        print(e.get_positions())","    for s, p in e.get_positions().items():","        if p > 0:","            e.insert_order(s, price=1, volume=p, side='ask', order_type='ioc')","        elif p < 0:","            e.insert_order(s, price=100000, volume=-p, side='bid', order_type='ioc')  ","    if(debug):","        print(\"End Positions: \")","        print(e.get_positions())"],"id":1}]]},"ace":{"folds":[],"scrolltop":1109.9999999999998,"scrollleft":0,"selection":{"start":{"row":15,"column":0},"end":{"row":15,"column":0},"isBackwards":false},"options":{"guessTabSize":true,"useWrapMode":false,"wrapToView":true},"firstLineState":{"row":58,"state":"qqstring3","mode":"ace/mode/python"}},"timestamp":1683983693161,"hash":"631f64a440174f6fe43f9d0157fefc0901982630"}