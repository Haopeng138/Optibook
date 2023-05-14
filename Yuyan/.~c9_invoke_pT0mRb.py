'''
EXAMPLE AUTO QUOTER

Do not edit this file directly. Instead, copy it somewhere else in your workspace.
These are simple bots that illustrate the Optibook API and some simple trading concepts. These bots will not make a profit.

This is an example bot that quotes the instrument C2_GREEN_ENERGY_ETF.
Quoting an instrument means sending both bids and asks at the same time and making these publicly visible in the order book,
so that other participants can trade with you. The logic of this bot is very simple. It looks at the current order book and tries to 
improve the price by 0.10 cents if possible. If the best bid is 90 and the best ask is 91, it will try to send a bid=90.10 and ask=90.90.
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

BASKET_INSTRUMENT_IDS = ['C1_FOSSIL_FUEL_ETF', 'C2_GREEN_ENERGY_ETF']
STOCK_INSTRUMENT_IDS = ['C1_GAS_INC', 'C1_OIL_CORP', 'C2_SOLAR_CO', 'C2_WIND_LTD']
ALL_IDS = ['C1_FOSSIL_FUEL_ETF', 'C2_GREEN_ENERGY_ETF', 'C1_GAS_INC', 'C1_OIL_CORP', 'C2_SOLAR_CO', 'C2_WIND_LTD']


def closeAllPosition(e, debug=False):
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

def print_order_response(order_response: InsertOrderResponse):
    if order_response.success:
        logger.info(f"Inserted order successfully, order_id='{order_response.order_id}'")
    else:
        logger.info(f"Unable to insert order with reason: '{order_response.success}'")

def exists_gain(e, b_id, s1_id, s2_id):
    book_b = e.get_last_price_book(b_id)
    book_s1 = e.get_last_price_book(s1_id)
    book_s2 = e.get_last_price_book(s2_id)
    
    if book_b and book_s1.bids and book_s2.bids and book_b.asks:
        # Comprar stock y vender basket 
        gain = (book_s1.bids[0].price + book_s2.bids[0].price) - (2*book_b.asks[0].price)
        if (gain > 0.5):
            # print([0, book_b.asks[0].price, book_b.asks[0].volume, book_s1.bids[0].price, book_s1.bids[0].volume, book_s2.bids[0].price, book_s2.bids[0].volume])
            return [0, book_b.asks[0].price, book_b.asks[0].volume, book_s1.bids[0].price, book_s1.bids[0].volume, book_s2.bids[0].price, book_s2.bids[0].volume, gain]
            
    if book_b and book_s1.asks and book_s2.asks and book_b.bids:
        # Comprar basket y vender stock
        gain = (2*book_b.bids[0].price) - (book_s1.asks[0].price + book_s2.asks[0].price)
        if (gain > 0.5):
            # print([1, book_b.bids[0].price, book_b.bids[0].volume, book_s1.asks[0].price, book_s1.asks[0].volume, book_s2.asks[0].price, book_s2.asks[0].volume])
            return [1, book_b.bids[0].price, book_b.bids[0].volume, book_s1.asks[0].price, book_s1.asks[0].volume, book_s2.asks[0].price, book_s2.asks[0].volume, gain]

    return [False]
    
def trade_cycle(e: Exchange):
    pass


def main():
    exchange = Exchange()
    exchange.connect()
    
    # closeAllPosition(exchange)
    print(exchange.get_positions_and_cash())
    
    volume_basket = 10
    volume_stock = 5
    
    while True:
        case = ["C1_FOSSIL_FUEL_ETF", "C1_GAS_INC", "C1_OIL_CORP"]
        result = exists_gain(exchange, case[0], case[1], case[2])
        if len(result)<=1: 
            case = ["C2_GREEN_ENERGY_ETF", 'C2_SOLAR_CO', 'C2_WIND_LTD']
            result = exists_gain(exchange, case[0], case[1], case[2])
            if len(result)<=1:
                # time.sleep(1)
                continue
            
        print("REsult in main: ", result)
        
        positions_and_cash = exchange.get_positions_and_cash()
        
        if result[0]==0:
            print(exchange.get_pnl())
            # # Keep position arount boundaries
            # Worst case: About to exceed limits of negative basket -> Need to buy immediately
            if positions_and_cash[case[0]]["volume"] - volume_basket <= -450:
                response: InsertOrderResponse = exchange.insert_order(case[0], price=result[1], volume=volume_basket, side=SIDE_BID, order_type=ORDER_TYPE_IOC)
                # print_order_response(response)
            # Worst case: About to exceed limits of positive stock1 -> Need to sell immediately
            if positions_and_cash[case[1]]["volume"] + volume_stock >= 450:
                response: InsertOrderResponse = exchange.insert_order(case[1], price=result[3], volume=volume_stock, side=SIDE_ASK, order_type=ORDER_TYPE_IOC)
                # print_order_response(response)
            # Worst case: About to exceed limits of positive stock2 -> Need to sell immediately
            if positions_and_cash[case[2]]["volume"] + volume_stock >= 450:
                response: InsertOrderResponse = exchange.insert_order(case[2], price=result[5], volume=volume_stock, side=SIDE_ASK, order_type=ORDER_TYPE_IOC)
                # print_order_response(response)
                
            # Start buying stock and selling basket
            response: InsertOrderResponse = exchange.insert_order(case[0], price=result[1]+0.2*result[7], volume=volume_basket, side=SIDE_ASK, order_type=ORDER_TYPE_IOC)
            # print_order_response(response)
            response: InsertOrderResponse = exchange.insert_order(case[1], price=result[3], volume=volume_stock, side=SIDE_BID, order_type=ORDER_TYPE_IOC)
            # print_order_response(response)
            response: InsertOrderResponse = exchange.insert_order(case[2], price=result[5], volume=volume_stock, side=SIDE_BID, order_type=ORDER_TYPE_IOC)
            
            print(exchange.get_pnl())
        if result[0]==1:
            print(exchange.get_pnl())
            
            # Worst case: About to exceed limits of positive basket -> Need to sell immediately
            if positions_and_cash[case[0]]["volume"] + volume_basket >= 450:
                response: InsertOrderResponse = exchange.insert_order(case[0], price=result[1], volume=volume_basket, side=SIDE_ASK, order_type=ORDER_TYPE_IOC)
                print_order_response(response)
            # Worst case: About to exceed limits of negative stock1 -> Need to buy immediately
            if positions_and_cash[case[1]]["volume"] - volume_stock <= -450:
                response: InsertOrderResponse = exchange.insert_order(case[1], price=result[3], volume=volume_stock, side=SIDE_BID, order_type=ORDER_TYPE_IOC)
                print_order_response(response)
            # Worst case: About to exceed limits of negative stock2 -> Need to buy immediately
            if positions_and_cash[case[2]]["volume"] - volume_stock <= -450:
                response: InsertOrderResponse = exchange.insert_order(case[2], price=result[5], volume=volume_stock, side=SIDE_BID, order_type=ORDER_TYPE_IOC)
                print_order_response(response)
                
            # Start buying basket and selling stock
            response: InsertOrderResponse = exchange.insert_order(case[0], price=result[1]-0.2*result[7], volume=volume_basket, side=SIDE_BID, order_type=ORDER_TYPE_IOC)
            # print_order_response(response)
            response: InsertOrderResponse = exchange.insert_order(case[1], price=result[3], volume=volume_stock, side=SIDE_ASK, order_type=ORDER_TYPE_IOC)
            # print_order_response(response)
            response: InsertOrderResponse = exchange.insert_order(case[2], price=result[5], volume=volume_stock, side=SIDE_ASK, order_type=ORDER_TYPE_IOC)
            
            print(exchange.get_pnl())
            
        '''
        for pos in positions_and_cash:
            if positions_and_cash[pos]["volume"] > 280:
                response: InsertOrderResponse = exchange.insert_order(pos, price=50, volume=15, side=SIDE_ASK, order_type=ORDER_TYPE_IOC)
                print_order_response(response)
            if positions_and_cash[pos]["volume"]< -280:
                response: InsertOrderResponse = exchange.insert_order(pos, price=210, volume=15, side=SIDE_BID, order_type=ORDER_TYPE_IOC)
                print_order_response(response)
        '''
        
        # time.sleep(1)
        
        
    
    print(exchange.get_positions_and_cash())
    

if __name__ == '__main__':
    main()
