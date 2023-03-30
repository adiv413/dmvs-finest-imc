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


                orders.append(Order(product, 10002, -1))
                orders.append(Order(product, 10003, -1))
                orders.append(Order(product, 10004, -1))
                

                orders.append(Order(product, 9998, 1))
                orders.append(Order(product, 9997, 1))
                orders.append(Order(product, 9996, 1))

                
                result[product] = orders

                # Return the dict of orders
                # These possibly contain buy or sell orders for PEARLS
                # Depending on the logic above
        return result