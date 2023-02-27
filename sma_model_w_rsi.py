from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

# Mean Reversion with Simple Moving Average (SMA)

class Trader:

    prices = {
        "avg_prices" : {},
        "acceptable_price" : {} ,
        "avg_gains" : {},
        "avg_losses" : {}
    }
    def calc_rsi(self, product, window = 100):
        if len(self.prices["avg_prices"][product]) > 1:
            avg_gain = 0
            avg_loss = 0
            lower_lim = max(0, len(self.prices["avg_prices"][product]) - window)
            for i in range(lower_lim, len(self.prices["avg_prices"][product]) - 1):
                if self.prices["avg_prices"][product][i] < self.prices["avg_prices"][product][i + 1]:
                    avg_gain += self.prices["avg_prices"][product][i + 1] - self.prices["avg_prices"][product][i]
                else:
                    avg_loss += self.prices["avg_prices"][product][i] - self.prices["avg_prices"][product][i + 1]
            avg_gain = avg_gain / len(self.prices["avg_prices"][product])
            avg_loss = avg_loss / len(self.prices["avg_prices"][product])
            if product not in self.prices["avg_gains"]:
                self.prices["avg_gains"][product] = []
            if product not in self.prices["avg_losses"]:
                self.prices["avg_losses"][product] = []

            window = min(window, len(self.prices["avg_gains"][product]))
            #calculate rsi moving average 
            if len(self.prices["avg_gains"][product]) == 0:
                self.prices["avg_gains"][product].append(avg_gain)
                self.prices["avg_losses"][product].append(avg_loss)
                return 100 - (100  / (1 + (avg_gain / avg_loss)))

            curr_gain, curr_loss = 0,0
            if self.prices["avg_prices"][product][-1] < self.prices["avg_prices"][product][-2]:
                curr_gain = self.prices["avg_prices"][product][-2] - self.prices["avg_prices"][product][-1]
            else:
                curr_loss = self.prices["avg_prices"][product][-1] - self.prices["avg_prices"][product][-2]
            if window * self.prices["avg_gains"][product][-1] + curr_loss == 0:
                rsi = 100
            else:
                rsi = 100 - (100 / (1 + ((window * self.prices["avg_gains"][product][-1] + curr_gain) / (window * self.prices["avg_losses"][product][-1] + curr_loss))))

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

                curr_price = (best_ask + best_bid) / 2 

                if product not in self.prices["avg_prices"]:
                    self.prices["avg_prices"][product] = []

                self.prices["avg_prices"][product].append(curr_price)
                self.prices["acceptable_price"][product] = sum(self.prices["avg_prices"][product]) / len(self.prices["avg_prices"][product])

                # set acceptable price
                acceptable_price = self.prices["acceptable_price"][product]

                rsi = self.calc_rsi(product, 20)
                min_rsi, max_rsi = 30, 70

                # based on pricing, make orders
                if rsi < min_rsi:
                    print("BUY", str(-best_ask_volume) + "x", best_ask)
                    orders.append(Order(product, best_ask, -best_ask_volume))

                if rsi > max_rsi:
                    print("SELL", str(best_bid_volume) + "x", best_bid)
                    orders.append(Order(product, best_bid, -best_bid_volume))

                print(f'{product}, {best_ask}, {best_ask_volume}, {best_bid}, {best_bid_volume}, {acceptable_price}')

                result[product] = orders

        return result
