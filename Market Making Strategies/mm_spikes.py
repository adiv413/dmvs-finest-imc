#https://kollider.medium.com/build-a-crypto-market-making-bot-in-python-d71eeae2dcd7
#https://www.reddit.com/r/algotrading/comments/6q8dp6/market_making_theory_and_application_readings/
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
from math import floor


class Trader:
    # PROFIT_TARGET = 1
    #BEST
    # RISK_ADJUSTMENT = {"BANANAS" : 0.12, "PEARLS" : 0.12}
    # ORDER_VOLUME = {"BANANAS" : 4, "PEARLS" : 5}
    # HALF_SPREAD_SIZE = {"BANANAS": 3, "PEARLS": 3}

    RISK_ADJUSTMENT = {"BANANAS" : 0.1, "PEARLS" : 0.1}
    ORDER_VOLUME = {"BANANAS" : 4, "PEARLS" : 5}
    HALF_SPREAD_SIZE = {"BANANAS": 2, "PEARLS": 3}
    MM_POSITION_LIMIT = {"BANANAS" : 10, "PEARLS" : 10}
    MM_POSITION = {"BANANAS" : 0, "PEARLS" : 0}
    MM_LAST_ORDER_PRICE = {"BANANAS" : {"BUY": 0, "SELL": 0}, "PEARLS" : {"BUY": 0, "SELL": 0}}
    LAST_TIMESTAMP = -100000

    SPIKE_WINDOW_SIZE = 7
    SPIKE_OUTLIERS = 5

    PRICES = {"BANANAS": [], "PEARLS": []}
    SPREADS = {"BANANAS": [], "PEARLS": []}

    def calc_ISMA(self): #this takes the last SPIKE_WINDOW_SIZE spreads and prices, and removes SPIKE_OUTLIERS prices that are associated with the lowest spreads

        prices = self.PRICES[-self.SPIKE_WINDOW_SIZE:]
        spreads = self.SPREADS[-self.SPIKE_WINDOW_SIZE:]
        #remove the prices associated with the lowest spreads
        prices = [x for _,x in sorted(zip(spreads,prices))]
        prices = prices[self.SPIKE_OUTLIERS:]
        #get the average of the remaining prices
        avg = sum(prices) / len(prices)
        return avg

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        print('\n')
        result = {}

        for product in state.order_depths.keys():
            orders: list[Order] = []
            order_depth: OrderDepth = state.order_depths[product]

            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                best_bid = max(order_depth.buy_orders.keys())

                best_ask = min(order_depth.sell_orders.keys())

                value = (best_ask + best_bid)/2
                spread = best_ask - best_bid

                self.PRICES[product].append(value)
                self.SPREADS[product].append(spread)

                try:
                    position = state.position[product]
                except:
                    position = 0
                skew = -position * self.RISK_ADJUSTMENT[product]

                # buy_quote = floor(value - self.HALF_SPREAD_SIZE[product] + skew)
                # sell_quote = floor(value + self.HALF_SPREAD_SIZE[product] + skew)

                # use spike_SMA as the price to center your spread around
                try:
                    spike_SMA = self.calc_ISMA()
                    value = spike_SMA
                except:
                    pass
                buy_quote = floor(value - self.HALF_SPREAD_SIZE[product] + skew)
                sell_quote = floor(value + self.HALF_SPREAD_SIZE[product] + skew)

    
                orders.append(Order(product, buy_quote, max(0,min(self.ORDER_VOLUME[product], self.MM_POSITION_LIMIT[product] - position))))
                orders.append(Order(product, sell_quote, -max(0,min(self.ORDER_VOLUME[product], self.MM_POSITION_LIMIT[product] + position))))

    
                print(f'{product}:')
                try:
                    own_trades = state.own_trades[product]
                    print(f'Own trades for {product}: {own_trades}')
                except:
                    own_trades = []
                for trade in own_trades:
                    if trade.timestamp == self.LAST_TIMESTAMP:
                        if trade.buyer == "SUBMISSION" and trade.price == self.MM_LAST_ORDER_PRICE[product]["BUY"]:
                            self.MM_POSITION[product] += trade.quantity
                        elif trade.seller == "SUBMISSION" and trade.price == self.MM_LAST_ORDER_PRICE[product]["SELL"]:
                            self.MM_POSITION[product] -= trade.quantity

                print('Actual position: ', position)
                print('Estimated MM position: ', self.MM_POSITION[product])

                self.MM_LAST_ORDER_PRICE[product] = {"BUY": buy_quote, "SELL": sell_quote}
                result[product] = orders

        self.LAST_TIMESTAMP = state.timestamp
        
        print('\n----------------------------------------------------------------------------------------------------\n')
        return result