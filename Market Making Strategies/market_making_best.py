#https://kollider.medium.com/build-a-crypto-market-making-bot-in-python-d71eeae2dcd7
#https://www.reddit.com/r/algotrading/comments/6q8dp6/market_making_theory_and_application_readings/
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order


class Trader:
    # PROFIT_TARGET = 1
    #best rn is order_volume = 4, risk adjustment = 0.12, half spread = 3
    RISK_ADJUSTMENT = 0.12
    ORDER_VOLUME = {"BANANAS" : 4, "PEARLS" : 5}
    HALF_SPREAD_SIZE = 3

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
                skew = -position * self.RISK_ADJUSTMENT

                # buy_quote = value + (skew - spread/2+0.01)
                # sell_quote = value + (skew + spread/2-0.01)
                buy_quote = value - self.HALF_SPREAD_SIZE + skew
                sell_quote = value + self.HALF_SPREAD_SIZE + skew
    
                orders.append(Order(product, buy_quote, self.ORDER_VOLUME[product]))
                # orders.append(Order(product, buy_quote-2, self.ORDER_VOLUME/2))
                orders.append(Order(product, sell_quote, -self.ORDER_VOLUME[product]))
                # orders.append(Order(product, sell_quote+2, -self.ORDER_VOLUME/2))

                print(f'position: {position}')

                result[product] = orders
        
        return result