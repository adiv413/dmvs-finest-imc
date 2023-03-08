from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

# Mean Reversion with Adaptive Moving Average (AMA), n = 10 (lookback 10 timesteps to adapt)
# https://help.cqg.com/cqgic/23/default.htm#!Documents/adaptivemovingaverageama.htm

class Trader:

    WINDOW_SIZE = 10
    PRICES = {"BANANAS" : [], "PEARLS" : []}
    POSITION_LIMIT = {"BANANAS" : 20, "PEARLS" : 20}
    AMA = {"BANANAS" : -1, "PEARLS" : -1}

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}

        for product in state.order_depths.keys():
            order_depth: OrderDepth = state.order_depths[product]
            orders: list[Order] = []

            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0: # if there are orders in the market, recompute acceptable price
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                spot_price = (best_ask + best_bid) / 2

                try:
                    position = state.position[product]
                except:
                    position = 0

                self.PRICES[product].append(spot_price)
                
                num_prices = len(self.PRICES[product])
                lookback = min(num_prices, self.WINDOW_SIZE)

                direction = self.PRICES[product][-1] - self.PRICES[product][-lookback]
                volatility = sum([abs(self.PRICES[product][-i] - self.PRICES[product][-(i+1)]) for i in range(1, lookback)])

                volatility = 0 if volatility == 0 else volatility

                efficiency_ratio = abs(direction / volatility)

                fast_ema_ratio = 2 / (2+1)
                slow_ema_ratio = 2 / (30+1)
                scaling_constant = efficiency_ratio * (fast_ema_ratio - slow_ema_ratio) + slow_ema_ratio
                scaling_constant = scaling_constant**2

                if self.AMA[product] == -1: #first iteration
                    self.AMA[product] = spot_price
                    return result
                
                self.AMA[product] = scaling_constant * (spot_price - self.AMA[product]) + self.AMA[product]

                if best_ask < self.AMA[product]:
                    # print("BUY", str(-best_ask_volume) + "x", best_ask)
                    orders.append(Order(product, best_ask, max(0,min(-best_ask_volume, self.POSITION_LIMIT[product] - position))))
                elif best_bid > self.AMA[product]:
                    # print("SELL", str(best_bid_volume) + "x", best_bid)
                    orders.append(Order(product, best_bid, min(0,max(best_bid_volume, -self.POSITION_LIMIT[product] - position))))        
                
                print(f'price for {product} is {spot_price}, ama is {self.AMA[product]}')

            result[product] = orders

        return result