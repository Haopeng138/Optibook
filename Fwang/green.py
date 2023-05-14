'''
This is an example bot that trades a single instrument C2_GREEN_ENERGY_ETF.
All it does is to randomly insert either a BID or an ASK every 5 seconds.
The price at which it inserts is equal to the opposite side of the order book.
Thus, if the best bid in the order book is currently 90, it will send a sell order for price 90.
If the best ask in the order book is 91, it will send a buy order for price 91.

The order type this bot uses is IOC (immediate or cancel). This means that if the order does not
immediately trade, it will not be visible to others in the order book. Instead, it will be cancelled automatically.
'''
import logging
import time
from typing import List
from optibook import common_types as t
from optibook import ORDER_TYPE_IOC, ORDER_TYPE_LIMIT, SIDE_ASK, SIDE_BID
from optibook.exchange_responses import InsertOrderResponse
from optibook.synchronous_client import Exchange
import random
import json

logging.getLogger('client').setLevel('ERROR')
logger = logging.getLogger(__name__)

BASKET_INSTRUMENT_ID = 'C2_GREEN_ENERGY_ETF'
STOCK_INSTRUMENT_IDS = ['C2_SOLAR_CO', 'C2_WIND_LTD']

e = Exchange()
e.connect()

def print_report(e: Exchange):
    pnl = e.get_pnl()
    positions = e.get_positions_and_cash()
    my_trades = e.poll_new_trades(BASKET_INSTRUMENT_ID)
    all_market_trades = e.poll_new_trade_ticks(BASKET_INSTRUMENT_ID)
    logger.info(f'I have done {len(my_trades)} trade(s) in {BASKET_INSTRUMENT_ID} since the last report. There have been {len(all_market_trades)} market trade(s) in total in {BASKET_INSTRUMENT_ID} since the last report.')
    logger.info(f'My PNL is: {pnl:.2f}')
    logger.info(f'My current positions are: {json.dumps(positions, indent=3)}')


def print_order_response(order_response: InsertOrderResponse):
    if order_response.success:
        logger.info(f"Inserted order successfully, order_id='{order_response.order_id}'")
    else:
        logger.info(f"Unable to insert order with reason: '{order_response.success}'")

#def get_cash_delta

def trade_cycle(e: Exchange, vol: int,bought_prc: int,sell_prc: int):
    basket_book = e.get_last_price_book(BASKET_INSTRUMENT_ID)
    if basket_book and basket_book.bids and basket_book.asks:
        
        new_bid = basket_book.bids[0].price + 0.1
        new_ask = basket_book.asks[0].price - 0.1
        bought_prc = new_bid*vol*2
        sell_prc = new_ask*vol*2
        
        if bought_prc < sell_prc:
            e.insert_order(BASKET_INSTRUMENT_ID, price=new_ask, volume=vol*2, side=SIDE_ASK, order_type=ORDER_TYPE_IOC)
            e.insert_order(STOCK_INSTRUMENT_IDS[0], price=new_bid, volume=vol, side=SIDE_BID, order_type=ORDER_TYPE_IOC)
            e.insert_order(STOCK_INSTRUMENT_IDS[1], price=new_bid, volume=vol, side=SIDE_BID, order_type=ORDER_TYPE_IOC)
        
    else:
        logger.info('No top bid/ask or no book at all for the basket instrument')

    print_report(e)
    
def closeAllPosition(debug=False):
    '''
    Iterates and attempts to close all open positions
    
    Parameters
    -----------
    debug : Bool
        If true, we print our current positions before and after attempting
        to close
    '''
    if(debug):
        print("Starting Positions: ")
        print(e.get_positions())
    for s, p in e.get_positions().items():
        if p > 0:
            e.insert_order(s, price=1, volume=p, side='ask', order_type='ioc')
        elif p < 0:
            e.insert_order(s, price=100000, volume=-p, side='bid', order_type='ioc')  
    if(debug):
        print("End Positions: ")
        print(e.get_positions())

def main():

    basket_book = e.get_last_price_book(BASKET_INSTRUMENT_ID)
    vol=2
    bought_prc = -1
    sell_prc = -1
    #closeAllPosition()
    
    new_bid = basket_book.bids[0].price + 0.1
    response: InsertOrderResponse = e.insert_order(STOCK_INSTRUMENT_IDS[0], price=new_bid, volume=vol, side=SIDE_BID, order_type=ORDER_TYPE_IOC)
    response: InsertOrderResponse = e.insert_order(STOCK_INSTRUMENT_IDS[1], price=new_bid, volume=vol, side=SIDE_BID, order_type=ORDER_TYPE_IOC)
    

    # you can also define host/user/pass yourself
    # when not defined, it is taken from ~/.optibook file if it exists
    # if that file does not exists, an error is thrown
    #exchange = Exchange(host='host-to-connect-to', info_port=7001, exec_port=8001, username='your-username', password='your-password')
    #exchange.connect()
    
    sleep_duration_sec = 1
    while True:
        trade_tick_history = exchange.get_trade_tick_history(instrument_id)
        logger.info(f'Iteration complete. Sleeping for {sleep_duration_sec} seconds')
        time.sleep(sleep_duration_sec)


if __name__ == '__main__':
    main()