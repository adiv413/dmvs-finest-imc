# THIS IS THE FILE YOU TRADE WITH. DATAMODEL.PY SHOWS THE DATA STRUCTURES THAT EACH TIMESTEP WILL USE>

# The Python code below is the minimum code that is required in a submission file:
# 1. The "datamodel" imports at the top. Using the typing library is optional.
# 2. A class called "Trader", this class name should not be changed.
# 3. A run function that takes a tradingstate as input and outputs a "result" dict.

from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

class Trader:

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        result = {}

        for product in state.order_depths.keys():
            if product == "PEARLS":
                order_depth: OrderDepth = state.order_depths[product]

        return result