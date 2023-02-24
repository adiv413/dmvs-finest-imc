from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

#this code will not execute any trades. It will just be inputted into the alg and will be used to download the data free of any intervention from our algorithm.
class Trader:

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():
            timestamp = state.timestamp
            order_depth: OrderDepth = state.order_depths[product]
            
            
        return result