#https://kollider.medium.com/build-a-crypto-market-making-bot-in-python-d71eeae2dcd7
#https://www.reddit.com/r/algotrading/comments/6q8dp6/market_making_theory_and_application_readings/
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order


class Trader:
    # PROFIT_TARGET = 1
    #BEST
    # RISK_ADJUSTMENT = {"BANANAS" : 0.12, "PEARLS" : 0.12}
    # ORDER_VOLUME = {"BANANAS" : 4, "PEARLS" : 5}
    # HALF_SPREAD_SIZE = {"BANANAS": 3, "PEARLS": 3}

    RISK_ADJUSTMENT = {"BANANAS" : 0.12, "PEARLS" : 0.12}
    ORDER_VOLUME = {"BANANAS" : 4, "PEARLS" : 4}
    HALF_SPREAD_SIZE = {"BANANAS": 3, "PEARLS": 3}

    POSITION_LIMIT = {"BANANAS" : 10, "PEARLS" : 10}

    prices = {
        "asks" : {}, 
        "bids" : {},
        "avg_prices" : {},
        "count" : {},
        "acceptable_price" : {
            "PEARLS" : 10000,
            "BANANAS" : 4895
        } 
    }
    
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}
        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():
            orders: list[Order] = []
            # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
            order_depth: OrderDepth = state.order_depths[product]

            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                best_bid = max(order_depth.buy_orders.keys())

                best_ask = min(order_depth.sell_orders.keys())

                value = (best_ask + best_bid)/2
                spread = best_ask - best_bid
                try:
                    position = state.position[product]
                except:
                    position = 0
                skew = -position * self.RISK_ADJUSTMENT[product]

                # buy_quote = value + (skew - spread/2+0.01)
                # sell_quote = value + (skew + spread/2-0.01)
                buy_quote = value - self.HALF_SPREAD_SIZE[product] + skew
                sell_quote = value + self.HALF_SPREAD_SIZE[product] + skew
    
                orders.append(Order(product, buy_quote, self.ORDER_VOLUME[product]))
                orders.append(Order(product, sell_quote, -self.ORDER_VOLUME[product]))

                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]

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
                if product not in self.prices["avg_prices"]:
                    self.prices["avg_prices"][product] = [curr_price]
                    self.prices["acceptable_price"][product] = curr_price

                    # don't place orders in the first iteration
                    result[product] = orders
                    return result
                
                i = len(self.prices["avg_prices"][product]) - 1 # index of current price
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

                curr_average = scaling_constant * (curr_price - self.prices["acceptable_price"][product]) + self.prices["acceptable_price"][product]

                self.prices["acceptable_price"][product] = curr_average
                self.prices["avg_prices"][product].append(curr_average)

            # set acceptable price
            acceptable_price = self.prices["acceptable_price"][product]

            try: 
                position = state.position[product]
            except:
                position = 0
            # based on pricing, make orders
            if len(order_depth.sell_orders) > 0:
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]

                if best_ask < acceptable_price:
                    print("BUY", str(-best_ask_volume) + "x", best_ask)
                    orders.append(Order(product, best_ask, max(0,min(-best_ask_volume, self.POSITION_LIMIT[product] - position))))

            if len(order_depth.buy_orders) > 0:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                if best_bid > acceptable_price:
                    print("SELL", str(best_bid_volume) + "x", best_bid)
                    orders.append(Order(product, best_bid, -max(0,min(best_bid_volume, self.POSITION_LIMIT[product] + position))))

                print(f'{product}, {best_ask}, {best_ask_volume}, {best_bid}, {best_bid_volume}, {acceptable_price}')

            result[product] = orders
        
        return result