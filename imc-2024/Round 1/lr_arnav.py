#https://kollider.medium.com/build-a-crypto-market-making-bot-in-python-d71eeae2dcd7
#https://www.reddit.com/r/algotrading/comments/6q8dp6/market_making_theory_and_application_readings/
from typing import Dict, List, Any
from datamodel import OrderDepth, TradingState, Order
from math import floor
import jsonpickle
import collections
from statistics import linear_regression
import collections
class Trader:

    products = ["AMETHYSTS", "STARFRUIT"]
    POSITION_LIMIT = {"AMETHYSTS": 20, "STARFRUIT": 20}

    AMETHYST_PRICE = 10000
    STARFRUIT_PRICE = -1
    
    def market_make_amethyst(self, product, order_depth, position):
        orders: list[Order] = []

        osell = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
        obuy = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))
        buyReserve = min(20, 20-position)
        sellReserve = max(-20, -20-position)
        ## Market Taking
        #BUYING
        print(f'Position: {position}')
        for sellOrder in osell:
            if sellOrder < self.AMETHYST_PRICE:
                orders.append(Order(product, sellOrder, min(buyReserve,-osell[sellOrder])))
                buyReserve -= min(buyReserve,-osell[sellOrder])
                print(f'Market Taking Buy Order at {sellOrder} with volume {min(buyReserve,-osell[sellOrder])}')
            elif sellOrder == self.AMETHYST_PRICE and position < 0:
                orders.append(Order(product, sellOrder, min(buyReserve,-osell[sellOrder])))
                buyReserve -= min(buyReserve,-osell[sellOrder])
                print(f'Market Taking Buy Order at {sellOrder} with volume {min(buyReserve,-osell[sellOrder])}')
               
        #BUYING

        #SELLING    
        for buyOrder in obuy:
            if buyOrder > self.AMETHYST_PRICE:
                orders.append(Order(product, buyOrder, max(sellReserve,-obuy[buyOrder])))
                sellReserve -= max(sellReserve,-obuy[buyOrder])
                print(f'Market Taking Sell Order at {buyOrder} with volume {max(sellReserve,-obuy[buyOrder])}')
            elif buyOrder == self.AMETHYST_PRICE and position > 0:
                orders.append(Order(product, buyOrder, max(sellReserve,-obuy[buyOrder])))
                sellReserve -= max(sellReserve,-obuy[buyOrder])
                print(f'Market Taking Sell Order at {buyOrder} with volume {max(sellReserve,-obuy[buyOrder])}')
               
        # SELLING

        print(f'Position: {position}')
        ###################################################################

        ## Market Making
        best_bid = list(obuy.keys())[0]
        best_ask = list(osell.keys())[0]
        #sell order
        orders.append(Order(product, max(best_ask-1, self.AMETHYST_PRICE+1), sellReserve))
        print(f'Market Making Sell Order at {max(best_ask-1, self.AMETHYST_PRICE+1)} with volume {sellReserve}')
        #buy order
        orders.append(Order(product, min(best_bid+1, self.AMETHYST_PRICE-1), buyReserve))
        print(f'Market Making Buy Order at {min(best_bid+1, self.AMETHYST_PRICE-1)} with volume {buyReserve}')
        ###################################################################
        
        return orders

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}

        timestamp = state.timestamp
        LR_LOOKBACK = 14

        if timestamp == 0:
    
            ## MARKET MAKING PARAMETERS
            RISK_ADJUSTMENT = {"AMETHYSTS" : 0.1, "STARFRUIT" : 0.1}
            ORDER_VOLUME = {"AMETHYSTS" : 4, "STARFRUIT" : 5}
            HALF_SPREAD_SIZE = {"AMETHYSTS": 3, "STARFRUIT": 3}
            ############################

            ## ALGO PARAMETERS
            prices = {
                "asks" : {}, 
                "bids" : {},
                "avg_prices" : {},
                "count" : {},
                "acceptable_price" : {
                    "AMETHYSTS" : 10000,
                    "STARFRUIT" : 5050
                } 
            }
            ############################

            ## POSITION SIZING PARAMS
            MM_POSITION_LIMIT = {"AMETHYSTS" : 20, "STARFRUIT" : 0}
            MM_POSITION = {"AMETHYSTS" : 0, "STARFRUIT" : 0}
            MM_LAST_ORDER_PRICE = {"AMETHYSTS" : {"BUY": 0, "SELL": 0}, "STARFRUIT" : {"BUY": 0, "SELL": 0}}
            ############################
            ALGO_POSITION_LIMIT = {"AMETHYSTS" : 0, "STARFRUIT" : 20}
            ALGO_POSITION = {"AMETHYSTS" : 0, "STARFRUIT" : 0}
            ALGO_LAST_ORDER_PRICE = {"AMETHYSTS" : {"BUY": 0, "SELL": 0}, "STARFRUIT" : {"BUY": 0, "SELL": 0}}
            ############################
            LAST_TIMESTAMP = -100000
            PREV_PRICES = []
            PREV_TIMESTAMPS = []

        else:
            traderData = jsonpickle.decode(state.traderData)
            RISK_ADJUSTMENT, ORDER_VOLUME, HALF_SPREAD_SIZE, prices, MM_POSITION_LIMIT, MM_POSITION, MM_LAST_ORDER_PRICE, ALGO_POSITION_LIMIT, ALGO_POSITION, ALGO_LAST_ORDER_PRICE, LAST_TIMESTAMP, PREV_PRICES, PREV_TIMESTAMPS = traderData

        for product in self.products:
            orders: list[Order] = []
            order_depth: OrderDepth = state.order_depths[product]

            if product == 'AMETHYSTS':
                try:
                    curr_position = state.position[product]
                except:
                    curr_position = 0

                if product == 'AMETHYSTS':
                    orders = self.market_make_amethyst(product, order_depth, curr_position)
                    result[product] = orders
                    continue

                result[product] = orders
            else:


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
                    osell = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
                    obuy = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))
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
                    if len(PREV_PRICES) < LR_LOOKBACK:
                        prices["avg_prices"][product] = [curr_price]
                        prices["acceptable_price"][product] = curr_price

                        # don't place orders in the first iteration
                        result[product] = orders
                        PREV_PRICES.append(curr_price)
                        PREV_TIMESTAMPS.append(state.timestamp)
                        return result, 0, jsonpickle.encode([RISK_ADJUSTMENT, ORDER_VOLUME, HALF_SPREAD_SIZE, prices, MM_POSITION_LIMIT, MM_POSITION, MM_LAST_ORDER_PRICE, ALGO_POSITION_LIMIT, ALGO_POSITION, ALGO_LAST_ORDER_PRICE, LAST_TIMESTAMP, PREV_PRICES, PREV_TIMESTAMPS])

                    PREV_PRICES.pop(0)
                    PREV_TIMESTAMPS.pop(0)

                    PREV_PRICES.append(curr_price)
                    PREV_TIMESTAMPS.append(state.timestamp)

                    m, b = linear_regression(PREV_TIMESTAMPS, PREV_PRICES)

                    next_time = state.timestamp + (PREV_TIMESTAMPS[-1] - PREV_TIMESTAMPS[-2])

                    acceptable_price = m * next_time + b

                    prices["acceptable_price"][product] = acceptable_price
                    prices["avg_prices"][product].append(acceptable_price)

                    ##############################

                    ## MARKET MAKING ORDERS
                    # orders.append(Order(product, buy_quote, max(0,min(ORDER_VOLUME[product], MM_POSITION_LIMIT[product] - MM_POSITION[product]))))
                    # orders.append(Order(product, sell_quote, -max(0,min(ORDER_VOLUME[product], MM_POSITION_LIMIT[product] + MM_POSITION[product]))))
                    MM_LAST_ORDER_PRICE[product] = {"BUY": buy_quote, "SELL": sell_quote}
                    ##############################

                    ## ALGO ORDERS
                    acc_bid, acc_ask = acceptable_price - 1, acceptable_price + 1
                    mx_with_buy = -1
                    curr_pos = ALGO_POSITION[product]
                    for ask, vol in osell.items():
                        if ((ask < acc_bid) or ((ALGO_POSITION[product] < 0) and (ask == acc_bid))) and curr_pos < ALGO_POSITION_LIMIT['AMETHYSTS']:
                            mx_with_buy = max(mx_with_buy, ask)
                            order_for = min(-vol, self.POSITION_LIMIT[product] - curr_pos)
                            curr_pos += order_for
                            assert(order_for >= 0)
                            orders.append(Order(product, ask, order_for))
                    undercut_buy = best_ask + 1
                    undercut_sell = best_bid - 1

                    bid_price = min(undercut_buy, acc_bid - 1)
                    sell_price = max(undercut_sell, acc_ask + 1)

                    if (curr_pos < ALGO_POSITION_LIMIT['AMETHYSTS']) and (ALGO_POSITION[product] < 0):
                        num = min(20, ALGO_POSITION_LIMIT['AMETHYSTS'] - curr_pos)
                        orders.append(Order(product, min(undercut_buy + 1, acc_bid - 1), num))
                        curr_pos += num

                    if (curr_pos < ALGO_POSITION_LIMIT['AMETHYSTS']) and (ALGO_POSITION[product] > 7.5):
                        num = min(20, ALGO_POSITION_LIMIT['AMETHYSTS'] - curr_pos)
                        orders.append(Order(product, min(undercut_buy - 1, acc_bid - 1), num))
                        curr_pos += num

                    if curr_pos < ALGO_POSITION_LIMIT['AMETHYSTS']:
                        num = min(20, ALGO_POSITION_LIMIT['AMETHYSTS'] - curr_pos)
                        orders.append(Order(product, bid_price, num))
                        curr_pos += num

                    curr_pos = ALGO_POSITION[product]
                    for bid, vol in obuy.items():
                        if ((bid > acc_ask) or ((ALGO_POSITION[product] > 0) and (bid == acc_ask))) and curr_pos > -ALGO_POSITION_LIMIT['AMETHYSTS']:
                            order_for = max(-vol, -ALGO_POSITION_LIMIT['AMETHYSTS'] - curr_pos)
                            # order_for is a negative number denoting how much we will sell
                            curr_pos += order_for
                            assert(order_for <= 0)
                            orders.append(Order(product, bid, order_for))

                    if (curr_pos > -ALGO_POSITION_LIMIT['AMETHYSTS']) and (ALGO_POSITION[product] > 0):
                        num = max(-20, -ALGO_POSITION_LIMIT['AMETHYSTS'] - curr_pos)
                        orders.append(Order(product, max(undercut_sell - 1, acc_ask + 1), num))
                        curr_pos += num

                    if (curr_pos > -ALGO_POSITION_LIMIT['AMETHYSTS']) and (ALGO_POSITION[product] < -7.5):
                        num = max(-20, -ALGO_POSITION_LIMIT['AMETHYSTS'] - curr_pos)
                        orders.append(Order(product, max(undercut_sell + 1, acc_ask + 1), num))
                        curr_pos += num

                    if curr_pos > -ALGO_POSITION_LIMIT['AMETHYSTS']:
                        num = max(-20, -ALGO_POSITION_LIMIT['AMETHYSTS'] - curr_pos)
                        orders.append(Order(product, sell_price, num))
                        curr_pos += num
                    ##############################
                    
                    ## PRINT STATS
                    print(f'{product}:')
                    
                    try:
                        position = state.position[product]
                    except:
                        position = 0
                    
                    print(f'Actual position: {position}')
                    print('Estimated MM position: ', MM_POSITION[product])
                    print('Estimated ALGO position: ', ALGO_POSITION[product])
                    ##############################
                    
                    result[product] = orders

        LAST_TIMESTAMP = state.timestamp
        
        print('\n----------------------------------------------------------------------------------------------------\n')
        params = [RISK_ADJUSTMENT, ORDER_VOLUME, HALF_SPREAD_SIZE, prices, MM_POSITION_LIMIT, MM_POSITION, 
                  MM_LAST_ORDER_PRICE, ALGO_POSITION_LIMIT, ALGO_POSITION, ALGO_LAST_ORDER_PRICE, LAST_TIMESTAMP, PREV_PRICES, PREV_TIMESTAMPS]
        traderData = jsonpickle.encode(params) # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        conversions = 0

        return result, conversions, traderData