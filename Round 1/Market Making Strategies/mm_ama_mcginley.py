#https://kollider.medium.com/build-a-crypto-market-making-bot-in-python-d71eeae2dcd7
#https://www.reddit.com/r/algotrading/comments/6q8dp6/market_making_theory_and_application_readings/
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
from math import floor


class Trader:

    ## MARKET MAKING PARAMETERS
    RISK_ADJUSTMENT = {"BANANAS" : 0.1, "PEARLS" : 0.1} 
    ORDER_VOLUME = {"BANANAS" : 4, "PEARLS" : 4}
    HALF_SPREAD_SIZE = {"BANANAS": 3, "PEARLS": 3}

    ############################
    ## MCGINLEY PARAMETERS
    prices = {
        "asks" : {}, 
        "bids" : {},
        "avg_prices" : {},
        "avg_ama_prices" : {},
        "count" : {},
        "acceptable_price" : {
            "PEARLS" : 10000,
            "BANANAS" : 4895
        },
        "acceptable_ama_price" : {
            "PEARLS" : 10000,
            "BANANAS" : 4895
        } 
    }
    ## POSITION SIZING PARAMS
    MM_POSITION_LIMIT = {"BANANAS" : 9, "PEARLS" : 9}
    MM_POSITION = {"BANANAS" : 0, "PEARLS" : 0}
    MM_LAST_ORDER_PRICE = {"BANANAS" : {"BUY": 0, "SELL": 0}, "PEARLS" : {"BUY": 0, "SELL": 0}}
    ############################
    MCGINLEY_POSITION_LIMIT = {"BANANAS" : 5, "PEARLS" : 5}
    MCGINLEY_POSITION = {"BANANAS" : 0, "PEARLS" : 0}
    MCGINLEY_LAST_ORDER_PRICE = {"BANANAS" : {"BUY": 0, "SELL": 0}, "PEARLS" : {"BUY": 0, "SELL": 0}}
    ############################
    AMA_POSITION_LIMIT = {"BANANAS" : 6, "PEARLS" : 6}
    AMA_POSITION = {"BANANAS" : 0, "PEARLS" : 0}
    AMA_LAST_ORDER_PRICE = {"BANANAS" : {"BUY": 0, "SELL": 0}, "PEARLS" : {"BUY": 0, "SELL": 0}}
    LAST_TIMESTAMP = -100000

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}

        for product in state.order_depths.keys():
            orders: list[Order] = []
            order_depth: OrderDepth = state.order_depths[product]

            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                ##GET TRADES
                try:
                    own_trades = state.own_trades[product]
                except:
                    own_trades = []
                try:
                    position = state.position[product]
                except:
                    position = 0
                ## CALCULATING THE POSITION SIZE OF MARKET MAKING
                for trade in own_trades:
                    if trade.timestamp == self.LAST_TIMESTAMP:
                        if trade.buyer == "SUBMISSION" and trade.price == self.MM_LAST_ORDER_PRICE[product]["BUY"]:
                            self.MM_POSITION[product] += trade.quantity
                        elif trade.seller == "SUBMISSION" and trade.price == self.MM_LAST_ORDER_PRICE[product]["SELL"]:
                            self.MM_POSITION[product] -= trade.quantity
                        elif trade.buyer == "SUBMISSION" and trade.price == self.MCGINLEY_LAST_ORDER_PRICE[product]["BUY"]:
                            self.MCGINLEY_POSITION[product] += trade.quantity
                        elif trade.seller == "SUBMISSION" and trade.price == self.MCGINLEY_LAST_ORDER_PRICE[product]["SELL"]:
                            self.MCGINLEY_POSITION[product] -= trade.quantity
                        
                self.AMA_POSITION[product] = position - self.MCGINLEY_POSITION[product] - self.MM_POSITION[product]

                ##############################
                ## CALCULATING STATS
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                best_ask_volume = order_depth.sell_orders[best_ask]
                value = (best_ask + best_bid)/2
                ##############################
                ## MARKET MAKING STRATEGY
                pos = self.MM_POSITION[product] + self.AMA_POSITION[product]
                skew = round(-pos * self.RISK_ADJUSTMENT[product]) if self.AMA_POSITION[product] == 0 \
                    else round(-pos * self.RISK_ADJUSTMENT[product] * max((1 - self.AMA_POSITION[product] / 8), 0.01))
                buy_quote = floor(value - self.HALF_SPREAD_SIZE[product] + skew)
                sell_quote = floor(value + self.HALF_SPREAD_SIZE[product] + skew)
                ##############################

                

                if product not in self.prices["asks"]:
                    self.prices["asks"][product] = []
                if product not in self.prices["bids"]:
                    self.prices["bids"][product] = []
                
                self.prices["asks"][product].append(best_ask)
                self.prices["bids"][product].append(best_bid)

                n = 10
                get_avg_price = lambda x : (self.prices["asks"][product][x] + self.prices["bids"][product][x]) / 2 # gets average price at index
                curr_price = (best_ask + best_bid) / 2 

                # first iteration
                if product not in self.prices["avg_ama_prices"]:
                    self.prices["avg_ama_prices"][product] = [curr_price]
                    self.prices["acceptable_ama_price"][product] = curr_price

                    # don't place orders in the first iteration
                    result[product] = orders
                    return result
                
                i = len(self.prices["avg_ama_prices"][product]) - 1 # index of current price
                n_lookback_index = max(i - n, 0) # make sure we don't accidentally lookback into the negative indices

                direction = curr_price - get_avg_price(n_lookback_index) # today's price - price n bars back
                volatility = sum([abs(get_avg_price(j) - get_avg_price(j - 1)) for j in range(i, n_lookback_index, -1)])
                
                if volatility == 0:
                    efficiency_ratio = 0
                else:
                    efficiency_ratio = abs(direction / volatility)

                fast_ema_ratio = 2 / (2 + 1) # 2 / (k + 1) where k is small bucket (2 by default)
                slow_ema_ratio = 2 / (30 + 1) # 2 / (l + 1) where l is large bucket (30 by default)
                scaling_constant = (efficiency_ratio * (fast_ema_ratio - slow_ema_ratio) + slow_ema_ratio) ** 2

                curr_average = scaling_constant * (curr_price - self.prices["acceptable_ama_price"][product]) + self.prices["acceptable_ama_price"][product]

                self.prices["acceptable_ama_price"][product] = curr_average
                self.prices["avg_ama_prices"][product].append(curr_average)

                self.ama_order = 0

                # set acceptable price
                acceptable_ama_price = self.prices["acceptable_ama_price"][product]

                ## MCGINLEY STRATEGY
                mcginley_price = self.prices["acceptable_price"][product]

                n=10
                k=0.6
                curr_price = value

                # first iteration
                if product not in self.prices["avg_prices"]:
                    self.prices["avg_prices"][product] = [curr_price]
                    self.prices["acceptable_price"][product] = curr_price

                    # don't place orders in the first iteration
                    result[product] = orders
                    return result

                mcginley_price = mcginley_price + (curr_price-mcginley_price)/(k * n * (curr_price/mcginley_price)**4)

                self.prices["acceptable_price"][product] = mcginley_price
                self.prices["avg_prices"][product].append(mcginley_price)
            
                acceptable_price = self.prices["acceptable_price"][product]
                ##############################

                ## MARKET MAKING ORDERS
                orders.append(Order(product, buy_quote, max(0,min(self.ORDER_VOLUME[product], self.MM_POSITION_LIMIT[product] - self.MM_POSITION[product]))))
                orders.append(Order(product, sell_quote, -max(0,min(self.ORDER_VOLUME[product], self.MM_POSITION_LIMIT[product] + self.MM_POSITION[product]))))
                
                print("MM BUY", str(max(0,min(self.ORDER_VOLUME[product], self.MM_POSITION_LIMIT[product] - self.MM_POSITION[product]))) + "x", buy_quote)
                print("MM SELL", str(-max(0,min(self.ORDER_VOLUME[product], self.MM_POSITION_LIMIT[product] + self.MM_POSITION[product]))) + "x", sell_quote)

                self.MM_LAST_ORDER_PRICE[product] = {"BUY": buy_quote, "SELL": sell_quote}
                ##############################

                ama_buy = False
                ama_sell = False

                ## AMA ORDERS
                if best_ask < acceptable_ama_price and best_ask != buy_quote: #second part of and is so that orders don't overlap, which lets me individually keep track of positions
                    print("AMA BUY", str(max(0,min(-best_ask_volume, self.AMA_POSITION_LIMIT[product] - self.AMA_POSITION[product]))) + "x", best_ask)
                    orders.append(Order(product, best_ask, max(0,min(-best_ask_volume, self.AMA_POSITION_LIMIT[product] - self.AMA_POSITION[product]))))
                    self.AMA_LAST_ORDER_PRICE[product]["BUY"] = best_ask
                    ama_buy = True
                else:
                    self.AMA_LAST_ORDER_PRICE[product]["BUY"] = 0

                if best_bid > acceptable_ama_price and best_bid != sell_quote: #second part of and is so that orders don't overlap, which lets me individually keep track of positions
                    print("AMA SELL", str(-max(0,min(best_bid_volume, self.AMA_POSITION_LIMIT[product] + self.AMA_POSITION[product]))) + "x", best_bid)
                    orders.append(Order(product, best_bid, -max(0,min(best_bid_volume, self.AMA_POSITION_LIMIT[product] + self.AMA_POSITION[product]))))
                    self.AMA_LAST_ORDER_PRICE[product]["SELL"] = best_bid
                    ama_sell = True
                else:
                    self.AMA_LAST_ORDER_PRICE[product]["SELL"] = 0

                ## MCGINLEY ORDERS
                if best_ask < acceptable_price and best_ask != buy_quote and not ama_buy: #second part of and is so that orders don't overlap, which lets me individually keep track of positions
                    print("MCGINLEY BUY", str(max(0,min(-best_ask_volume, self.MCGINLEY_POSITION_LIMIT[product] - self.MCGINLEY_POSITION[product]))) + "x", best_ask)
                    orders.append(Order(product, best_ask, max(0,min(-best_ask_volume, self.MCGINLEY_POSITION_LIMIT[product] - self.MCGINLEY_POSITION[product]))))
                    self.MCGINLEY_LAST_ORDER_PRICE[product]["BUY"] = best_ask
                else:
                    self.MCGINLEY_LAST_ORDER_PRICE[product]["BUY"] = 0

                if best_bid > acceptable_price and best_bid != sell_quote and not ama_sell: #second part of and is so that orders don't overlap, which lets me individually keep track of positions
                    print("MCGINLEY SELL", str(-max(0,min(best_bid_volume, self.MCGINLEY_POSITION_LIMIT[product] + self.MCGINLEY_POSITION[product]))) + "x", best_bid)
                    orders.append(Order(product, best_bid, -max(0,min(best_bid_volume, self.MCGINLEY_POSITION_LIMIT[product] + self.MCGINLEY_POSITION[product]))))
                    self.MCGINLEY_LAST_ORDER_PRICE[product]["SELL"] = best_bid
                else:
                    self.MCGINLEY_LAST_ORDER_PRICE[product]["SELL"] = 0
                ##############################                
                

                print(f'{product}:')
                
                try:
                    position = state.position[product]
                except:
                    position = 0
                
                print(f'Actual position: {position}')
                print('Estimated MM position: ', self.MM_POSITION[product])
                print('Estimated MCGINLEY position: ', self.MCGINLEY_POSITION[product])
                print('Estimated AMA position: ', self.AMA_POSITION[product])
                
                result[product] = orders

        self.LAST_TIMESTAMP = state.timestamp
        
        print('\n----------------------------------------------------------------------------------------------------\n')
        return result