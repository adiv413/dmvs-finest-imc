from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

# Commodity Channel Index (CCI) with RSI for sanity check, period = 10
# https://www.daytradetheworld.com/trading-blog/cci-commodity-channel-index/

class Trader:

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

    ma_indexed = []
    tp_indexed = []
    cci_indexed = []

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
            n = 10
            

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

                if i != 0: 
                    period_high = max([get_avg_price(j) for j in range(n_lookback_index, i)]) #highest price across past n timesteps
                    period_low = min([get_avg_price(j) for j in range(n_lookback_index, i)]) #lowest price across past n timesteps
                else:
                    period_high = 1000
                    period_low = 1000

                typical_price = (period_high + period_low + curr_price)/3
                self.tp_indexed.append(typical_price)
                self.ma_indexed.append(curr_average)

                #print(f"I: {i} Period: {n_lookback_index}")
                #print(f"TP size: {len(self.tp_indexed)} MA size: {len(self.ma_indexed)}")
                #print(f"TP array: {self.tp_indexed}")
                #for j in range(n_lookback_index, i):
                    #print("j", j)
                #print("output", [self.tp_indexed[j] for j in range(n_lookback_index, i)])
                mean_deviation = sum([abs(self.tp_indexed[j] - self.ma_indexed[j]) for j in range(n_lookback_index, i)])/(i+1)
                print(f"mean_deviation: {mean_deviation}")
                if mean_deviation == 0:
                    mean_deviation = 1
                cci = (typical_price - curr_average)/(0.015 * mean_deviation)
                self.cci_indexed.append(cci)

            # set acceptable price
            acceptable_price = self.prices["acceptable_price"][product]

            # based on pricing, make orders
            if len(order_depth.sell_orders) > 0:
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]

                if best_ask < acceptable_price+1 and self.cci_indexed[i] - self.cci_indexed[i-1] > 50:
                #if self.cci_indexed[i] - self.cci_indexed[i-5] > 50:
                    print("BUY", str(-best_ask_volume) + "x", best_ask)
                    orders.append(Order(product, best_ask, -best_ask_volume))

            if len(order_depth.buy_orders) > 0:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                if best_bid > acceptable_price-1 and self.cci_indexed[i-1] - self.cci_indexed[i] > 50:
                #if self.cci_indexed[i] - self.cci_indexed[i-5] < -50:
                    print("SELL", str(best_bid_volume) + "x", best_bid)
                    orders.append(Order(product, best_bid, -best_bid_volume))

                print(f'{product}, {best_ask}, {best_ask_volume}, {best_bid}, {best_bid_volume}, {acceptable_price}')

            result[product] = orders

        return result