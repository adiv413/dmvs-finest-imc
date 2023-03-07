#https://kollider.medium.com/build-a-crypto-market-making-bot-in-python-d71eeae2dcd7
#https://www.reddit.com/r/algotrading/comments/6q8dp6/market_making_theory_and_application_readings/
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order, Trade


class Trader:
    # PROFIT_TARGET = 1
    #BEST
    # RISK_ADJUSTMENT = {"BANANAS" : 0.12, "PEARLS" : 0.12}
    # ORDER_VOLUME = {"BANANAS" : 4, "PEARLS" : 5}
    # HALF_SPREAD_SIZE = {"BANANAS": 3, "PEARLS": 3}

    RISK_ADJUSTMENT = {"BANANAS" : 0.12, "PEARLS" : 0.12}
    ORDER_VOLUME = {"BANANAS" : 4, "PEARLS" : 5}
    HALF_SPREAD_SIZE = {"BANANAS": 3, "PEARLS": 3}
    POSITION = {"BANANAS" : 0, "PEARLS" : 0}
    ORDER_COUNT = {"BANANAS" : 0, "PEARLS" : 0}
    LAST_OWN_TRADE = {"BANANAS" : 0, "PEARLS" : 0}

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        print('\n')
        result = {}
        for product in state.order_depths.keys():
            orders: list[Order] = []
            order_depth: OrderDepth = state.order_depths[product]

            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:

                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                value = (best_ask + best_bid)/2
                try:
                    position = state.position[product]
                except:
                    position = 0
                skew = -position * self.RISK_ADJUSTMENT[product]

                # buy_quote = value + (skew - spread/2+0.01)
                # sell_quote = value + (skew + spread/2-0.01)
                buy_quote = value - self.HALF_SPREAD_SIZE[product] + skew
                sell_quote = value + self.HALF_SPREAD_SIZE[product] + skew
    
                orders.append(Order(product, buy_quote, self.ORDER_VOLUME[product]))
                orders.append(Order(product, sell_quote, -self.ORDER_VOLUME[product]))

                try:
                    own_trades = state.own_trades[product]
                    if len(own_trades) > 0 and str(own_trades) != self.LAST_OWN_TRADE[product]:
                        for trade in own_trades:
                            if trade.buyer == "SUBMISSION":
                                self.ORDER_COUNT[product] += 1
                                self.POSITION[product] += trade.quantity
                            elif trade.seller == "SUBMISSION":
                                self.ORDER_COUNT[product] += 1
                                self.POSITION[product] -= trade.quantity
                    self.LAST_OWN_TRADE[product] = str(own_trades)
                except:
                    pass

                #ANALYTICS
                try:
                    print(f'own trades for {product}: {state.own_trades[product]}')
                    print(f'buyer: {state.own_trades[product][0].buyer}, seller: {state.own_trades[product][0].seller}')
                except:
                    print(f'no trades for {product}')
                
                print(f'market trades for {product}: {state.market_trades[product]}')

                print('\n')
                print(f'actual position for {product}: {position}')
                print(f'estimated position for {product}: {self.POSITION[product]}')
                print('\n')

                print(f'buy order for {product} at {buy_quote} with volume {self.ORDER_VOLUME[product]}')
                print(f'sell order for {product} at {sell_quote} with volume {-self.ORDER_VOLUME[product]}')

                order_success_pct = self.ORDER_COUNT[product] / ((state.timestamp/100)+1)
                print(f'order success rate for {product}: {order_success_pct}')


                result[product] = orders
        
        print('\n----------------------------------------------------------------------------------------------------\n')
        return result