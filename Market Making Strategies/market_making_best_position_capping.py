#https://kollider.medium.com/build-a-crypto-market-making-bot-in-python-d71eeae2dcd7
#https://www.reddit.com/r/algotrading/comments/6q8dp6/market_making_theory_and_application_readings/
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order


class Trader:
    # PROFIT_TARGET = 1
    #BEST
    # RISK_ADJUSTMENT = {"BANANAS" : 0.12, "PEARLS" : 0.12}
    # ORDER_VOLUME = {"BANANAS" : 4, "PEARLS" : 5}
    # HALF_SPREAD_SIZE = {"BANANAS": 3, "PEARLS": 3}

    RISK_ADJUSTMENT = {"BANANAS" : 0.12, "PEARLS" : 0.12}
    ORDER_VOLUME = {"BANANAS" : 4, "PEARLS" : 5}
    HALF_SPREAD_SIZE = {"BANANAS": 3, "PEARLS": 3}
    POSITION_LIMIT = {"BANANAS" : 10, "PEARLS" : 10}
    
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        print('\n')
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
                skew = -position * self.RISK_ADJUSTMENT[product]

                # buy_quote = value + (skew - spread/2+0.01)
                # sell_quote = value + (skew + spread/2-0.01)
                buy_quote = value - self.HALF_SPREAD_SIZE[product] + skew
                sell_quote = value + self.HALF_SPREAD_SIZE[product] + skew
    
                #max(0,min(-best_ask_volume, self.POSITION_LIMIT[product] - position))
                orders.append(Order(product, buy_quote, max(0,min(self.ORDER_VOLUME[product], self.POSITION_LIMIT[product] - position))))
                #-max(0,min(best_bid_volume, self.POSITION_LIMIT[product] + position))
                orders.append(Order(product, sell_quote, -max(0,min(self.ORDER_VOLUME[product], self.POSITION_LIMIT[product] + position))))

                # print(f'position: {position}')'
                # try:
                #     print(f'own trades for {product}: {state.own_trades[product]}')
                # except:
                #     print(f'no trades for {product}')

                print(f'net position for {product}: {position}')

                # print('\n')   

                # print(f'buy order for {product} at {buy_quote} with volume {self.ORDER_VOLUME[product]}')
                # print(f'sell order for {product} at {sell_quote} with volume {-self.ORDER_VOLUME[product]}')

                result[product] = orders
        
        print('\n----------------------------------------------------------------------------------------------------\n')
        return result