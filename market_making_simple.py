#https://kollider.medium.com/build-a-crypto-market-making-bot-in-python-d71eeae2dcd7
#https://www.reddit.com/r/algotrading/comments/6q8dp6/market_making_theory_and_application_readings/
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order


class Trader:
    PROFIT_TARGET = 1
    RISK_ADJUSTMENT = 0.5

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

            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0 and product == "BANANAS":
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_volume = order_depth.buy_orders[best_bid]
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_volume = order_depth.sell_orders[best_ask]
                average_volume = (best_bid_volume + best_ask_volume)/2
                print(best_ask_volume, best_bid_volume)
                value = (best_ask + best_bid)/2
                spread = best_ask - best_bid
                if spread <=7:
                    try:
                        position = state.position[product]
                    except:
                        position = 0
                    skew = -position * self.RISK_ADJUSTMENT

                    buy_quote = value + skew - spread/2+0.01
                    sell_quote = value + skew + spread/2-0.01
        
                    orders.append(Order(product, buy_quote, average_volume))
                    orders.append(Order(product, sell_quote, -average_volume))               
                    result[product] = orders
        print("own trades: ", state.own_trades)
        
        return result