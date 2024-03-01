from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order


class Trader:

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}

        order_depth: OrderDepth = state.order_depths
        print("...")
        for product in ["PEARLS"]:
            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'PEARLS':
                orders: list[Order] = []


                # orders.append(Order(product, 10002, -1))
                # orders.append(Order(product, 10003, -1))
                # orders.append(Order(product, 10004, -1))
                

                # orders.append(Order(product, 9998, 1))
                # orders.append(Order(product, 9997, 1))
                # orders.append(Order(product, 9996, 1))
                price = 10000
                best_ask = min(order_depth[product].sell_orders.keys())
                best_ask_volume = order_depth[product].sell_orders[best_ask]
                best_bid = max(order_depth[product].buy_orders.keys())
                best_bid_volume = order_depth[product].buy_orders[best_bid]

                try:
                    position = state.positions[product]
                except:
                    position = 0
                if best_ask < price:
                    orders.append(Order(product, best_ask, -best_ask_volume))
                if best_bid > price:
                    orders.append(Order(product, best_bid, -best_bid_volume))

                
                result[product] = orders

                # Return the dict of orders
                # These possibly contain buy or sell orders for PEARLS
                # Depending on the logic above
        return result