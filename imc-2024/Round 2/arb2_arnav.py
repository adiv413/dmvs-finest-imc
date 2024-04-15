#https://kollider.medium.com/build-a-crypto-market-making-bot-in-python-d71eeae2dcd7
#https://www.reddit.com/r/algotrading/comments/6q8dp6/market_making_theory_and_application_readings/
from typing import Dict, List, Any
from datamodel import OrderDepth, TradingState, Order
from math import floor
import jsonpickle
import collections
from statistics import linear_regression
class Trader:

    def values_extract(self, order_dict, buy=0):
        tot_vol = 0
        best_val = -1
        mxvol = -1

        for ask, vol in order_dict.items():
            if(buy==0):
                vol *= -1
            tot_vol += vol
            if tot_vol > mxvol:
                mxvol = vol
                best_val = ask
        
        return tot_vol, best_val
    
    def market_make_amethyst(self, product, order_depth, position):
        orders: list[Order] = []
        AMETHYST_PRICE = 10000


        osell = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
        obuy = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))
        buyReserve = min(20, 20 - position)
        sellReserve = max(-20, -20 - position)

        ###################################################################
        ## Market Taking
        #BUYING
        print(f'Position: {position}')
        for sellOrder in osell:
            if sellOrder < AMETHYST_PRICE:
                orders.append(Order(product, sellOrder, min(buyReserve,-osell[sellOrder])))
                buyReserve -= min(buyReserve, -osell[sellOrder])
                print(f'Market Taking Buy Order at {sellOrder} with volume {min(buyReserve, -osell[sellOrder])}')
            elif sellOrder == AMETHYST_PRICE and position < 0:
                orders.append(Order(product, sellOrder, min(buyReserve, -osell[sellOrder])))
                buyReserve -= min(buyReserve, -osell[sellOrder])
                print(f'Market Taking Buy Order at {sellOrder} with volume {min(buyReserve, -osell[sellOrder])}')

        #SELLING    
        for buyOrder in obuy:
            if buyOrder > AMETHYST_PRICE:
                orders.append(Order(product, buyOrder, max(sellReserve, -obuy[buyOrder])))
                sellReserve -= max(sellReserve, -obuy[buyOrder])
                print(f'Market Taking Sell Order at {buyOrder} with volume {max(sellReserve, -obuy[buyOrder])}')
            elif buyOrder == AMETHYST_PRICE and position > 0:
                orders.append(Order(product, buyOrder, max(sellReserve, -obuy[buyOrder])))
                sellReserve -= max(sellReserve, -obuy[buyOrder])
                print(f'Market Taking Sell Order at {buyOrder} with volume {max(sellReserve, -obuy[buyOrder])}')

        print(f'Position: {position}')
        ###################################################################
        ## Market Making
        best_bid = list(obuy.keys())[0]
        best_ask = list(osell.keys())[0]
        #BUYING
        orders.append(Order(product, min(best_bid + 1, AMETHYST_PRICE - 1), buyReserve))
        print(f'Market Making Buy Order at {min(best_bid + 1, AMETHYST_PRICE - 1)} with volume {buyReserve}')
        #SELLING
        orders.append(Order(product, max(best_ask - 1, AMETHYST_PRICE + 1), sellReserve))
        print(f'Market Making Sell Order at {max(best_ask - 1, AMETHYST_PRICE + 1)} with volume {sellReserve}')
        ###################################################################
        
        return orders

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}

        timestamp = state.timestamp
        LR_LOOKBACK = {"STARFRUIT": 12, "ORCHIDS": 12}
        products = ["AMETHYSTS", "STARFRUIT", "ORCHIDS"]
        storage_cost = 0.1


        if timestamp == 0:
            buys = []
    
            ## MARKET MAKING PARAMETERS
            RISK_ADJUSTMENT = {"AMETHYSTS" : 0.1, "STARFRUIT" : 0.1, "ORCHIDS": 0.1}
            ORDER_VOLUME = {"AMETHYSTS" : 4, "STARFRUIT" : 5, "ORCHIDS": 5}
            HALF_SPREAD_SIZE = {"AMETHYSTS": 3, "STARFRUIT": 3, "ORCHIDS": 3}
            ############################

            ## ALGO PARAMETERS
            prices = {
                "asks" : {}, 
                "bids" : {},
                "avg_prices" : {},
                "count" : {},
                "acceptable_price" : {
                    "AMETHYSTS" : 10000,
                    "STARFRUIT" : 5050,
                    "ORCHIDS": 1200
                } 
            }
            ############################

            ## POSITION SIZING PARAMS
            MM_POSITION_LIMIT = {"AMETHYSTS" : 20, "STARFRUIT" : 0, "ORCHIDS": 0}
            MM_POSITION = {"AMETHYSTS" : 0, "STARFRUIT" : 0, "ORCHIDS": 0}
            MM_LAST_ORDER_PRICE = {"AMETHYSTS" : {"BUY": 0, "SELL": 0}, 
                                   "STARFRUIT" : {"BUY": 0, "SELL": 0},
                                   "ORCHIDS": {"BUY": 0, "SELL": 0}}
            ############################
            ALGO_POSITION_LIMIT = {"AMETHYSTS" : 0, "STARFRUIT" : 20, "ORCHIDS": 100}
            ALGO_POSITION = {"AMETHYSTS" : 0, "STARFRUIT" : 0, "ORCHIDS": 0}
            ALGO_LAST_ORDER_PRICE = {"AMETHYSTS" : {"BUY": 0, "SELL": 0}, 
                                   "STARFRUIT" : {"BUY": 0, "SELL": 0},
                                   "ORCHIDS": {"BUY": 0, "SELL": 0}}
            ############################
            LAST_TIMESTAMP = -100000
            PREV_PRICES = {"STARFRUIT": [], "ORCHIDS": []}
            PREV_TIMESTAMPS = {"STARFRUIT": [], "ORCHIDS": []}

        else:
            traderData = jsonpickle.decode(state.traderData)
            RISK_ADJUSTMENT, ORDER_VOLUME, HALF_SPREAD_SIZE, prices, MM_POSITION_LIMIT, MM_POSITION, MM_LAST_ORDER_PRICE, ALGO_POSITION_LIMIT, ALGO_POSITION, ALGO_LAST_ORDER_PRICE, LAST_TIMESTAMP, PREV_PRICES, PREV_TIMESTAMPS, buys = traderData

        for product in products:
            orders: list[Order] = []
            order_depth: OrderDepth = state.order_depths[product]

            if product == 'AMETHYSTS':
                try:
                    curr_position = state.position[product]
                except:
                    curr_position = 0

                orders = self.market_make_amethyst(product, order_depth, curr_position)
                result[product] = orders
            if product == 'STARFRUIT':
                if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                    ##GET TRADES
                    try:
                        own_trades = state.own_trades[product]
                    except:
                        own_trades = []
                    ##############################

                    ## CALCULATING THE POSITION SIZE OF MARKET MAKING
                    for trade in own_trades:
                        if trade.timestamp == LAST_TIMESTAMP:
                            if trade.buyer == "SUBMISSION" and trade.price == MM_LAST_ORDER_PRICE[product]["BUY"]:
                                MM_POSITION[product] += trade.quantity
                            elif trade.seller == "SUBMISSION" and trade.price == MM_LAST_ORDER_PRICE[product]["SELL"]:
                                MM_POSITION[product] -= trade.quantity
                    ##############################

                    ## CALCULATING THE POSITION SIZE OF ALGO
                    for trade in own_trades:
                        if trade.timestamp == LAST_TIMESTAMP:
                            if trade.buyer == "SUBMISSION" and trade.price == ALGO_LAST_ORDER_PRICE[product]["BUY"]:
                                ALGO_POSITION[product] += trade.quantity
                            elif trade.seller == "SUBMISSION" and trade.price == ALGO_LAST_ORDER_PRICE[product]["SELL"]:
                                ALGO_POSITION[product] -= trade.quantity
                    ##############################

                    ## CALCULATING STATS
                    best_bid = max(order_depth.buy_orders.keys())
                    best_ask = min(order_depth.sell_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    value = (best_ask + best_bid)/2
                    ##############################

                    ## MARKET MAKING STRATEGY
                    skew = -MM_POSITION[product] * RISK_ADJUSTMENT[product]
                    buy_quote = floor(value - HALF_SPREAD_SIZE[product] + skew)
                    sell_quote = floor(value + HALF_SPREAD_SIZE[product] + skew)
                    ##############################

                    ## ALGO STRATEGY

                    if product not in prices["asks"]:
                        prices["asks"][product] = []
                    if product not in prices["bids"]:
                        prices["bids"][product] = []
                    
                    prices["asks"][product].append(best_ask)
                    prices["bids"][product].append(best_bid)

                    curr_price = value

                    # first n iterations
                    if len(PREV_PRICES[product]) < LR_LOOKBACK[product]:
                        prices["avg_prices"][product] = [curr_price]
                        prices["acceptable_price"][product] = curr_price

                        # don't place orders in the first iteration
                        result[product] = orders
                        PREV_PRICES[product].append(curr_price)
                        PREV_TIMESTAMPS[product].append(state.timestamp)
                        continue

                    PREV_PRICES[product].pop(0)
                    PREV_TIMESTAMPS[product].pop(0)

                    PREV_PRICES[product].append(curr_price)
                    PREV_TIMESTAMPS[product].append(state.timestamp)

                    m, b = linear_regression(PREV_TIMESTAMPS[product], PREV_PRICES[product])

                    next_time = state.timestamp + (PREV_TIMESTAMPS[product][-1] - PREV_TIMESTAMPS[product][-2])

                    acceptable_price = m * next_time + b

                    prices["acceptable_price"][product] = acceptable_price
                    prices["avg_prices"][product].append(acceptable_price)

                    ##############################
                
                    try:
                        position = state.position[product]
                    except:
                        position = 0

                    osell = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
                    obuy = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))

                    acc_bid = acceptable_price-1
                    acc_ask = acceptable_price+1
                    LIMIT = ALGO_POSITION_LIMIT[product]

                    '''best_buy_pr = max(order_depth.buy_orders.keys())
                    best_sell_pr = min(order_depth.sell_orders.keys())
                    buy_vol = order_depth.buy_orders[best_bid]
                    sell_vol = order_depth.sell_orders[best_ask]'''
                    sell_vol, best_sell_pr = self.values_extract(osell)
                    buy_vol, best_buy_pr = self.values_extract(obuy, 1)

                    cpos = position

                    for ask, vol in osell.items():
                        if ((ask <= acc_bid) or ((position<0) and (ask == acc_bid+1))) and cpos < LIMIT:
                            order_for = min(-vol, LIMIT - cpos)
                            cpos += order_for
                            assert(order_for >= 0)
                            orders.append(Order(product, round(ask), order_for))

                    undercut_buy = best_buy_pr + 1
                    undercut_sell = best_sell_pr - 1

                    bid_pr = min(undercut_buy, acc_bid) # we will shift this by 1 to beat this price
                    sell_pr = max(undercut_sell, acc_ask)

                    if cpos < LIMIT:
                        num = LIMIT - cpos
                        orders.append(Order(product, round(bid_pr), num))
                        cpos += num
                    
                    cpos = position

                    for bid, vol in obuy.items():
                        if ((bid >= acc_ask) or ((position>0) and (bid+1 == acc_ask))) and cpos > -LIMIT:
                            order_for = max(-vol, -LIMIT-cpos)
                            # order_for is a negative number denoting how much we will sell
                            cpos += order_for
                            assert(order_for <= 0)
                            orders.append(Order(product, round(bid), order_for))

                    if cpos > -LIMIT:
                        num = -LIMIT-cpos
                        orders.append(Order(product, round(sell_pr), num))
                        cpos += num

                    
                    
                    ## PRINT STATS
                    print(f'{product}:')
                    
                    print(f'Actual position: {position}')
                    print('Estimated MM position: ', MM_POSITION[product])
                    print('Estimated ALGO position: ', ALGO_POSITION[product])
                    ##############################
                    
                    result[product] = orders

            if product == 'ORCHIDS':
                if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                    dt = state.timestamp - LAST_TIMESTAMP

                    try:
                        position = state.position[product]
                    except:
                        position = 0
                    
                    ##GET TRADES
                    try:
                        own_trades = state.own_trades[product]
                    except:
                        own_trades = []

                    ## CALCULATING STATS
                    best_bid = max(order_depth.buy_orders.keys())
                    best_ask = min(order_depth.sell_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    value = (best_ask + best_bid)/2

                    conv_ask = state.observations.conversionObservations[product].askPrice
                    conv_bid = state.observations.conversionObservations[product].bidPrice
                    transport_fees = state.observations.conversionObservations[product].transportFees
                    export_tariff = state.observations.conversionObservations[product].exportTariff
                    import_tariff = state.observations.conversionObservations[product].importTariff

                    ##############################

                    # LOCAL TRADING (todo?)

                    ##############################


                    total_conversions = 0
                        
                    ##############################

                    # FOREIGN MARKET TRADING (todo)

                    ##############################



                    ##############################

                    # AUTOMATIC CONVERSIONS 

                    ##############################

                    # look at position depreciation and see if we need to sell off orchids this timestep
                    sell_orders = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
                    buy_orders = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))

                    # do currency arb, so if we have a long position in orchids, we can sell it off to the conversion market
                    if position > 0:
                        total_conversions = position
                    
                    # for every sell order in the order book, check if it is cheaper than the buy order in the conversion market + fees
                    for ask, vol in sell_orders.items():
                        acceptable_price = conv_bid + transport_fees + import_tariff
                        if acceptable_price < ask:
                            total_conversions -= vol
                            # also fill the sell order
                            orders.append(Order(product, ask, -vol))
                        else:
                            break
                    # for every buy order in the order book, check if it is more expensive than the sell order in the conversion market + fees
                    for bid, vol in buy_orders.items():
                        acceptable_price = conv_ask + transport_fees + export_tariff
                        if acceptable_price > bid:
                            # total_conversions += vol (don't do this, should sell in the next time step once product is aquired)
                            # also fill the buy order
                            orders.append(Order(product, bid, vol))
                        else:
                            break
                    

                    # if total_conversions == 0: # we didn't trade internationally this timestep
                    #     while len(buys) != 0:
                    #         acceptable_price = conv_ask + (state.timestamp - buys[0][0]) / dt * storage_cost - transport_fees / buys[0][2] - export_tariff / buys[0][2]
                    #         if acceptable_price > buys[0][1]:
                    #             total_conversions += buys[0][2]
                    #             buys.pop(0)
                    #         else:
                    #             break

                    #     total_conversions = -total_conversions # sell off position
                    
                    ## PRINT STATS
                    print(f'{product}:')
                    
                    print(f'Actual position: {position}')
                    print('Estimated MM position: ', MM_POSITION[product])
                    print('Estimated ALGO position: ', ALGO_POSITION[product])
                    ##############################
                    
                    result[product] = orders

        LAST_TIMESTAMP = state.timestamp
        
        print('\n----------------------------------------------------------------------------------------------------\n')
        params = [RISK_ADJUSTMENT, ORDER_VOLUME, HALF_SPREAD_SIZE, prices, MM_POSITION_LIMIT, MM_POSITION, 
                  MM_LAST_ORDER_PRICE, ALGO_POSITION_LIMIT, ALGO_POSITION, ALGO_LAST_ORDER_PRICE, LAST_TIMESTAMP, PREV_PRICES, PREV_TIMESTAMPS, buys]
        traderData = jsonpickle.encode(params) # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.

        return result, total_conversions, traderData