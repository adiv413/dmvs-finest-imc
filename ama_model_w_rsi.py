from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

# Mean Reversion with Adaptive Moving Average (AMA), n = 10 (lookback 10 timesteps to adapt)
# https://help.cqg.com/cqgic/23/default.htm#!Documents/adaptivemovingaverageama.htm

class Trader:

    prices = {
        "asks" : {}, 
        "bids" : {},
        "avg_prices" : {},
        "count" : {},
        "avg_gains": {},
        "avg_losses": {},
        "acceptable_price" : {
            "PEARLS" : 10000,
            "BANANAS" : 4895
        } 
    }

    def calc_rsi(self, product, window=100):
        if len(self.prices["avg_prices"][product]) > 1:
            avg_gain = 0
            avg_loss = 0
            lower_lim = max(
                0, len(self.prices["avg_prices"][product]) - window)
            for i in range(lower_lim, len(self.prices["avg_prices"][product]) - 1):
                if self.prices["avg_prices"][product][i] < self.prices["avg_prices"][product][i + 1]:
                    avg_gain += self.prices["avg_prices"][product][i +
                                                                   1] - self.prices["avg_prices"][product][i]
                else:
                    avg_loss += self.prices["avg_prices"][product][i] - \
                        self.prices["avg_prices"][product][i + 1]
            avg_gain = avg_gain / len(self.prices["avg_prices"][product])
            avg_loss = avg_loss / len(self.prices["avg_prices"][product])
            if product not in self.prices["avg_gains"]:
                self.prices["avg_gains"][product] = []
            if product not in self.prices["avg_losses"]:
                self.prices["avg_losses"][product] = []

            #calculate rsi moving average
            if(avg_loss == 0):
                return 100
            else:
                rsi = 100 - (100 / (1 + avg_gain / avg_loss))

            self.prices["avg_gains"][product].append(avg_gain)
            self.prices["avg_losses"][product].append(avg_loss)
            return rsi



    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():
            order_depth: OrderDepth = state.order_depths[product]
            orders: list[Order] = []

            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0: # if there are orders in the market, recompute acceptable price
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
            rsi = self.calc_rsi(product, 10)
        
            # based on pricing, make orders
            if len(order_depth.sell_orders) > 0:
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]

                if best_ask < acceptable_price and rsi < 30:
                    print("BUY", str(-best_ask_volume) + "x", best_ask)
                    orders.append(Order(product, best_ask, -best_ask_volume))

            if len(order_depth.buy_orders) > 0:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                if best_bid > acceptable_price and rsi > 70:
                    print("SELL", str(best_bid_volume) + "x", best_bid)
                    orders.append(Order(product, best_bid, -best_bid_volume))

                print(f'{product}, {best_ask}, {best_ask_volume}, {best_bid}, {best_bid_volume}, {acceptable_price}')

            result[product] = orders

        return result
