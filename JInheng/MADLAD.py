from time import sleep
import numpy as np

from optibook.synchronous_client import Exchange
import logging
logger = logging.getLogger('client')
logger.setLevel('ERROR')

# We start our client with this utils class
# Exchange (e) and a 

phil_A = 'C1_FOSSIL_FUEL_ETF'
phil_B = 'C2_GREEN_ENERGY_ETF'

e = Exchange()
e.connect()

MAX_POSITIONS = 200
MAX_OUTSTANDING = 500

def downloadOrderBook(instr):
    '''
    Returns the current bids and asks for the given instrument.
    
    Parameters
    ------------
    instr: string
        Instrument ('PHILIPS_A' or 'PHILIPS_B').
        No assertion is done for perfomance reasons
        
        
    Returns
    ---------
    book.bids, book.asks : PriceVolume, PriceVolume
        Lists of `PriceVolume` objects corresponding to bids and asks for the 
        supplied instrument
    '''
    print("ngjkfds")
    print(e)
    book = e.get_last_price_book(instr)
    print(book)
    return book.bids, book.asks

def printCurrentPositions():
    '''
    Prints all current positions, plus position cash
    '''
    positions = e.get_positions_and_cash()
    for p in positions:
        print(p, positions[p])


def deleteAllOutstandingOrders(instrument_id, side):
    """
    Exits all outstanding positions for the chosen instrument and order type
    
    Parameters
    ----------
    instrument_id:  str
        Intrument ID (`PHILIPS_A` or `PHILIPS_B`) (no assertion is done 
            for perfomance)
    side: str
        string representing the types of outstanding orders we wish to close.
        Select from 'bid', 'ask', or 'all'
    Returns
    -------
    None
    """
    outstanding = e.get_outstanding_orders(instrument_id)
    for o in outstanding.values():
        if(o.side == side or side=='all'):
            result = e.delete_order(instrument_id, order_id=o.order_id)

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

#-----------------------------------------------------------#
#             .   ,  ,.  ,-.      ,     ,.  ,-.             #
#             |\ /| /  \ |  \     |    /  \ |  \            #
#             | V | |--| |  | --- |    |--| |  |            #
#             |   | |  | |  /     |    |  | |  /            #
#             '   ' '  ' `-'      `--' '  ' `-'             #
# Market Arbitrage Dual-Listing Algorithmic Delta (Neutral) #
#-----------------------------------------------------------#

# Market Arbitrage Dual-Listing Algorithmic Delta (Neutral), AKA **MAD-LAD**, is a 
# delta-neutral market-making algorithm that trades on the illiquid market and 
# instantly hedges on the liquid market.

# By continuously holding both a bid and an ask in the illiquid market, making 
# sure that the bid-ask spread for `Philips_B` that we set is always wider than the
# bid-ask spread for `Philips_A`, we can always immediately hedge our position on 
# the more liquid market while making a profit. Thus, this algorithm is characterized
# by an extremely low risk, by having a total position close to zero.

# In order to decrease the risk even more, the algorithm includes a *"pillow"* 
# which ensure a minimum profit for each trade, avoiding low–profit trades.

# In the long run, as the market randomly moves, the difference in times our 
# bid and our spread are met will tend to zero, essentially cashing in the profit
# from the initial position. However, in order to ensure that the positions in the
# two instruments do indeed approach zero, *"unwinding"* is performed. This is achieved by
# transferring positions from the instrument with negative positions to the other when 
# the trade is profitable or neutral. Thus, the profit made by the algorithm is 
# always a real profit and not a virtual, buy never holding unbalanced positions.

# The algorithm showed steady increasing profit, with low–risk and discrete profits. 

#--------------------------------------------------------#
#--------------------------------------------------------#
#-------------------------INIT---------------------------#
#--------------------------------------------------------#
#--------------------------------------------------------#

def initB():
    '''
    Finds and returns initial ask and bid price for `PHILIPS_B`.
    If either of these cannot be found (currently no bids/asks on the market),
    we repeat until an initial start price is found. This is used to find
    an initial entry point into the market.

    Returns
    -------
    initial_bid_B, initial_ask_B : float, float 
        initial_bid_B = Initial bid price for `PHILIPS_B`
        initial_ask_B = Initial ask price for `PHILIPS_B`
    '''
    success = False
    while success == False:
        bids_B, asks_B = downloadOrderBook(phil_B)
        try:
            bid_B = bids_B[0].price
            ask_B = asks_B[0].price
            success = True
        except IndexError:
            pass
    
    initial_bid_B = bid_B - .8
    initial_ask_B = ask_B + .8
    
    return initial_bid_B, initial_ask_B

bid_B, ask_B = initB()
delta = 0.1 #Amount by which we increase/decrease our bid/ask (min possible price difference)
# Minimum amount we wish our B bid/ask to be above/below our A bid/ask
# Therefore, our B spread should always be greater or equal to (A_spread + 2 * pillow) 
pillow = 0.1 
k = 2
volume = 14

sleep_time = 0.1

#--------------------------------------------------------#
#--------------------------------------------------------#
#--------------------MAIN LOOP---------------------------#
#--------------------------------------------------------#
#--------------------------------------------------------#

def mainLoop(t):
    """
    Main function to be looped over.
    Runs all price checks, attempts to run our Delta-Neutral algorithm to make
    small profits based on the difference in liquidity between our two instruments.
    
    Parameters
    -----------
    t : int
        Current time step (increases with iterations)
        
    Returns
    ---------
        None
    """
    
    # Start by calculating the current state of the market
    
    bid_A, ask_A = downloadOrderBook(phil_A)
    bid_B_, ask_B_, = downloadOrderBook(phil_B)
    #utils.printCurrentPositions()
    try:
        best_bid_A = bid_A[0].price
        best_ask_A = ask_A[0].price
        cur_bid_B = bid_B_[0].price
        cur_ask_B = ask_B_[0].price
    except IndexError:
        return
    
    ### BID vs ASK ### 
    
    # When we get BID price, this is the highest price people on the market are willing to pay
    
    # When we get ASK price, this is the lowest price people on the market are willing to sell for
    
    # When we want to buy a stock, we must BID. To gaurentee(ish) this goes through,
    # we must BID at the current best ASK (we buy at the current price people are willing to sell)
    
    bid_updated = False
    ask_updated = False
    global bid_B,ask_B
    
    # Every 9 ticks, we narrow our spread on our B bid and ask
    if t%9 == 0:  
        bid_B += delta
        ask_B -= delta
        
        bid_updated = True
        ask_updated = True
    # -------------------------------------------------------------------------#
    # we check to see if our B bid/ask encapsulates our A bid/ask              #
    # This ensures we are always making safe bets                              #
    # -------------------------------------------------------------------------#
    
    # If our current desired bid B (buy B) price is above the current bid price
    # for A on the market, we decrease it to be below A 
    # This ensures our spread is always large than the spread of A
    if (best_bid_A - bid_B < pillow):
        bid_B = best_bid_A - pillow
        bid_updated = True
    
    # We repeat the above logic for the ask price, the upper bound
    if (ask_B - best_ask_A < pillow):
        ask_B = best_ask_A + pillow
        ask_updated = True
    
    position_b = e.get_positions()[phil_B]
    position_a = e.get_positions()[phil_A]
    
    if(t % 50 == 0): # Occasionally print the current positions
        printCurrentPositions()
    
    # ------------------------------------------------------------------------ #
    # ---------------------PHILIPS_B Positions ------------------------------- #
    # ------------------------------------------------------------------------ #
    
    # If we have updated our B bid, we then attempt to place orders for them.
    # We use Limit orders, as this market is illiquid and we wish to give the 
    # market time to fulfil these orders
    
    if ask_updated and position_b >= - MAX_POSITIONS:
        # To update orders, we simply delete the old one and create a new one at desired price
        deleteAllOutstandingOrders(phil_B, 'ask')
        result = e.insert_order(phil_B, price=float(ask_B), side='ask', volume=volume, order_type='limit')

    #if we have updated our bid this time, we re-make all orders
    if bid_updated and position_b <= MAX_POSITIONS:
        #To update orders, we simply delete the old one and create a new one at desired price
        deleteAllOutstandingOrders(phil_B, 'bid')
        #we bid
        result = e.insert_order(phil_B, price=float(bid_B), side='bid', volume=volume, order_type='limit')
    
    # --------------------------------------------------------------------------------------- #
    # Below, we check if we currently have an inbalance in our positions. If we have an       #
    # inbalance, we buy or sell A (more liquid) to end with an overall holding of 0           #
    # --------------------------------------------------------------------------------------- #
  
    position_tot = position_b + position_a
    desired_volume = abs(position_tot)
    
    # We use IOC orders due to the high liquidity in this market. This prevents us
    # bidding/asking PHILIPS_A at any point with unfavourable prices
    
    # if our total position is positive, we want to sell in A (meeting a bid)
    if position_tot > 0:
        result = e.insert_order(phil_A, price=best_bid_A, side='ask', volume=desired_volume, order_type='ioc')
        print(f'We buy in B at {bid_B} and sell in A at {best_bid_A} with volume {desired_volume}',flush=True)

    # if our total position is negative, we want to buy in A (meet an ask)
    elif position_tot < 0:
        result = e.insert_order(phil_A, price=best_ask_A, side='bid', volume=desired_volume, order_type='ioc')
        print(f'We sell in B at {ask_B} and buy in A at {best_ask_A} with volume {desired_volume}',flush=True)
    
    # ------------------------------------------------------------------------ #
    # ------------------------- Delay ---------------------------------------- #
    # ------------------------------------------------------------------------ #
    
    # We introduce a delay, to give time for our limit orders for PHILIPS_B to 
    # be closed
    sleep(sleep_time)   
    
    # ------------------------------------------------------------------------ #
    # ------------------- Check outstandings ––––––––––-----------------–––––– #
    # ------------------------------------------------------------------------ #
    
    
    # Check if a trade occurred (i.e. there is an oustanding trade)
    outstanding_b = e.get_outstanding_orders(phil_B)
    has_outstanding_b_bid = False
    has_outstanding_b_ask = False
    
    # We iterate all our outstanding orders,
    # to check if we outstanding bids or asks
    for o in outstanding_b.values():
        if (o.side == 'bid'):
            has_outstanding_b_bid = True
        if (o.side == 'ask'):
            has_outstanding_b_ask = True
    # ------------------------------------------------------------------------ #
    # If we have no outstanding, then our bid has gone through. If our bid has #
    # gone through, we increase our spread by decreasing our further bids      #
    # ------------------------------------------------------------------------ #
    
    if(has_outstanding_b_bid == False): 
        bid_B -= delta * k
    # We repeat the same logic for our ask, increasing our spread
    if(has_outstanding_b_ask == False):
        ask_B += delta * k
    
    # ------------------------------------------------------------------------ #
    # -------------------------------- UNWINDING ----------------------------- #
    # ------------------------------------------------------------------------ #
    # Recalculate market values due to the change that has happened since last 
    # update
    bid_A, ask_A = downloadOrderBook(phil_A)
    bid_B_, ask_B_ = downloadOrderBook(phil_B)
    try:
        best_bid_A = bid_A[0].price 
        best_ask_A = ask_A[0].price
        cur_bid_B = bid_B_[0].price
        cur_ask_B = ask_B_[0].price
    except IndexError:
        return
    
    # If we have a positive B position, we look to unwind by selling B
    if position_b > 0 and position_a < 0:
        
        # We check all possible ask prices, and sell our B so long as the sale is profitable
        i = 0
        while cur_bid_B >= ask_A[i].price and i < len(ask_A):
            # We try to sell ALL B
            position_b=e.get_positions()[phil_B]
            position_a=e.get_positions()[phil_A]
            volume_unwinding = min(abs(bid_B_[0].volume), abs(ask_A[i].volume), abs(position_b), abs(position_a))  # best price
            if volume_unwinding <= 0: # Prevent impossible orders
                break
            result = e.insert_order(phil_B, price=float(cur_bid_B), side='ask', volume=volume_unwinding, order_type='ioc')
            result = e.insert_order(phil_A, price=float(ask_A[i].price), side='bid', volume=volume_unwinding, order_type='ioc')
            
            print(f'We unwind by selling in B at {cur_bid_B} and buying in A at {best_ask_A} at volume {volume_unwinding}',flush=True)
            printCurrentPositions()
                
            i+=1

    # If we currently have NEGATIVE B positions, we look to unwind by buying B
    if position_b < 0 and position_a > 0:
        # To unwind, we need to BUY B
        # So we desire the price we buy B (B ASK) to be lower than the price we can sell A (bid A)
        i = 0 
        while cur_ask_B <= bid_A[i].price and i < len(bid_A):
            position_b=e.get_positions()[phil_B]
            position_a=e.get_positions()[phil_A]
            # We try to buy ALL B
            volume_unwinding = min(abs(ask_B_[0].volume), abs(bid_A[i].volume), abs(position_b), abs(position_a))
            if volume_unwinding <= 0: # Prevent impossible orders
                break
            result = e.insert_order(phil_B, price=float(cur_ask_B), side='bid', volume=volume_unwinding, order_type='ioc')
            result = e.insert_order(phil_A, price=float(bid_A[i].price), side='ask', volume=volume_unwinding, order_type='ioc')
            
            print(f'We unwind by buying in B at {cur_ask_B} and selling in A at {best_bid_A} at volume {volume_unwinding}',flush=True)
            printCurrentPositions()
            
            i+=1

#--------------------------------------------------------#
#--------------------------------------------------------#
#--------------------------------------------------------#

def runLoop(algo,max_steps=None):
    """
    Runs our main algorithm loop
    
    Parameters
    ----------
    algo : func(t)
        Function pointer to our main algorithm loop. Function should take a single
        argument, t : Int, the current time step
        
    max_steps : int
        Max steps to run the function (if set to `None` it will run indefinitely)
        
    Returns
    -------
    None
    """

    if max_steps == None:
        t=0
        while True:
            algo(t)
            t+=1

    else:
        for t in range(max_steps):
            algo(t)

def main(sell_all=False):
    """
    Main function. Starts by removing outstanding orders from previous runs of 
    the bot runs, before starting our main loop.
    
    Parameters
    ----------
    sell_all : bool 
        If set to true, sells all and doesn't run any loop.
            Only to be used in case of emergency, closing all positions will close
            at any possible price, can result in drastic losses if there are mean 
            opportunists in the market.
    
    Returns
    --------
        None
    """
    
    if sell_all:
        closeAllPosition()
        printCurrentPositions()
        return
    
    try:
        #Delete any outstanding orders left from the previous run of the bot
        deleteAllOutstandingOrders(phil_A, 'all')
        deleteAllOutstandingOrders(phil_B, 'all')
        runLoop(mainLoop, None)
    except KeyboardInterrupt: # So we can safely stop loop through Ctrl+C
        pass
    return

if __name__ == '__main__':
    main(False)