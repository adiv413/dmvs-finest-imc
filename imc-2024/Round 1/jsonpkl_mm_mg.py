#https://kollider.medium.com/build-a-crypto-market-making-bot-in-python-d71eeae2dcd7
#https://www.reddit.com/r/algotrading/comments/6q8dp6/market_making_theory_and_application_readings/
from typing import Dict, List, Any
from datamodel import OrderDepth, TradingState, Order
from math import floor
import jsonpickle

class Trader:

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}

        timestamp = state.timestamp

        if timestamp == 0:
            products = ["AMETHYSTS", "STARFRUIT"]
    
            ## MARKET MAKING PARAMETERS
            RISK_ADJUSTMENT = {"AMETHYSTS" : 0.1, "STARFRUIT" : 0.1}
            ORDER_VOLUME = {"AMETHYSTS" : 4, "STARFRUIT" : 5}
            HALF_SPREAD_SIZE = {"AMETHYSTS": 3, "STARFRUIT": 3}
            ############################

            ## MCGINLEY PARAMETERS
            prices = {
                "asks" : {}, 
                "bids" : {},
                "avg_prices" : {},
                "count" : {},
                "acceptable_price" : {
                    "AMETHYSTS" : 10000,
                    "STARFRUIT" : 5400
                } 
            }
            ############################

            ## POSITION SIZING PARAMS
            MM_POSITION_LIMIT = {"AMETHYSTS" : 10, "STARFRUIT" : 10}
            MM_POSITION = {"AMETHYSTS" : 0, "STARFRUIT" : 0}
            MM_LAST_ORDER_PRICE = {"AMETHYSTS" : {"BUY": 0, "SELL": 0}, "STARFRUIT" : {"BUY": 0, "SELL": 0}}
            ############################
            MCGINLEY_POSITION_LIMIT = {"AMETHYSTS" : 10, "STARFRUIT" : 10}
            MCGINLEY_POSITION = {"AMETHYSTS" : 0, "STARFRUIT" : 0}
            MCGINLEY_LAST_ORDER_PRICE = {"AMETHYSTS" : {"BUY": 0, "SELL": 0}, "STARFRUIT" : {"BUY": 0, "SELL": 0}}
            ############################
            LAST_TIMESTAMP = -100000
        else:
            traderData = jsonpickle.decode(state.traderData)
            products, RISK_ADJUSTMENT, ORDER_VOLUME, HALF_SPREAD_SIZE, prices, MM_POSITION_LIMIT, MM_POSITION, MM_LAST_ORDER_PRICE, MCGINLEY_POSITION_LIMIT, MCGINLEY_POSITION, MCGINLEY_LAST_ORDER_PRICE, LAST_TIMESTAMP = traderData

        for product in products:
            orders: list[Order] = []
            order_depth: OrderDepth = state.order_depths[product]

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

                ## CALCULATING THE POSITION SIZE OF MCGINLEY
                for trade in own_trades:
                    if trade.timestamp == LAST_TIMESTAMP:
                        if trade.buyer == "SUBMISSION" and trade.price == MCGINLEY_LAST_ORDER_PRICE[product]["BUY"]:
                            MCGINLEY_POSITION[product] += trade.quantity
                        elif trade.seller == "SUBMISSION" and trade.price == MCGINLEY_LAST_ORDER_PRICE[product]["SELL"]:
                            MCGINLEY_POSITION[product] -= trade.quantity
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

                ## MCGINLEY STRATEGY
                if state.timestamp != 0:
                    mcginley_price = prices["acceptable_price"][product]
                else:
                    mcginley_price = value

                if product not in prices["asks"]:
                    prices["asks"][product] = []
                if product not in prices["bids"]:
                    prices["bids"][product] = []
                
                prices["asks"][product].append(best_ask)
                prices["bids"][product].append(best_bid)

                n=12
                k=0.67
                curr_price = value

                # first iteration
                if product not in prices["avg_prices"]:
                    prices["avg_prices"][product] = [curr_price]
                    prices["acceptable_price"][product] = curr_price

                    # don't place orders in the first iteration
                    result[product] = orders
                    conversions = 0
                    traderData = jsonpickle.encode([products, RISK_ADJUSTMENT, ORDER_VOLUME, HALF_SPREAD_SIZE, prices, MM_POSITION_LIMIT, 
                                                    MM_POSITION, MM_LAST_ORDER_PRICE, MCGINLEY_POSITION_LIMIT, MCGINLEY_POSITION, MCGINLEY_LAST_ORDER_PRICE, LAST_TIMESTAMP])
                    return result, conversions, traderData

                mcginley_price = mcginley_price + (curr_price-mcginley_price)/(k * n * (curr_price/mcginley_price)**4)

                prices["acceptable_price"][product] = mcginley_price
                prices["avg_prices"][product].append(mcginley_price)
            
                acceptable_price = prices["acceptable_price"][product]
                ##############################

                ## MARKET MAKING ORDERS
                orders.append(Order(product, buy_quote, max(0,min(ORDER_VOLUME[product], MM_POSITION_LIMIT[product] - MM_POSITION[product]))))
                orders.append(Order(product, sell_quote, -max(0,min(ORDER_VOLUME[product], MM_POSITION_LIMIT[product] + MM_POSITION[product]))))
                MM_LAST_ORDER_PRICE[product] = {"BUY": buy_quote, "SELL": sell_quote}
                ##############################

                ## MCGINLEY ORDERS
                if best_ask < acceptable_price and best_ask != buy_quote: #second part of and is so that orders don't overlap, which lets me individually keep track of positions
                    # print("BUY", str(-best_ask_volume) + "x", best_ask)
                    orders.append(Order(product, best_ask, max(0,min(-best_ask_volume, MCGINLEY_POSITION_LIMIT[product] - MCGINLEY_POSITION[product]))))
                    MCGINLEY_LAST_ORDER_PRICE[product]["BUY"] = best_ask
                else:
                    MCGINLEY_LAST_ORDER_PRICE[product]["BUY"] = 0

                if best_bid > acceptable_price and best_bid != sell_quote: #second part of and is so that orders don't overlap, which lets me individually keep track of positions
                    # print("SELL", str(best_bid_volume) + "x", best_bid)
                    orders.append(Order(product, best_bid, -max(0,min(best_bid_volume, MCGINLEY_POSITION_LIMIT[product] + MCGINLEY_POSITION[product]))))
                    MCGINLEY_LAST_ORDER_PRICE[product]["SELL"] = best_bid
                else:
                    MCGINLEY_LAST_ORDER_PRICE[product]["SELL"] = 0
                ##############################
                
                ## PRINT STATS
                print(f'{product}:')
                
                try:
                    position = state.position[product]
                except:
                    position = 0
                
                print(f'Actual position: {position}')
                print('Estimated MM position: ', MM_POSITION[product])
                print('Estimated MCGINLEY position: ', MCGINLEY_POSITION[product])
                ##############################
                
                result[product] = orders

        LAST_TIMESTAMP = state.timestamp
        
        print('\n----------------------------------------------------------------------------------------------------\n')
        params = [products, RISK_ADJUSTMENT, ORDER_VOLUME, HALF_SPREAD_SIZE, prices, MM_POSITION_LIMIT, MM_POSITION, 
                  MM_LAST_ORDER_PRICE, MCGINLEY_POSITION_LIMIT, MCGINLEY_POSITION, MCGINLEY_LAST_ORDER_PRICE, LAST_TIMESTAMP]
        traderData = jsonpickle.encode(params) # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        conversions = 0

        return result, conversions, traderData