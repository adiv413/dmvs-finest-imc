#https://kollider.medium.com/build-a-crypto-market-making-bot-in-python-d71eeae2dcd7
#https://www.reddit.com/r/algotrading/comments/6q8dp6/market_making_theory_and_application_readings/
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
from math import floor, log


class Trader:

    ### MEMORY
    stats = {
        "asks" : {}, 
        "bids" : {},
        "avg_prices" : {},
        "acceptable_price" : {
            "PEARLS" : -1,
            "BANANAS" : -1,
        } ,
        "bidVolumes" : {},
        "askVolumes" : {},
    }

    COUNT = 0
    POSITION_LIMIT = {"BANANAS": 20, "PEARLS": 20, "PINA_COLADAS": 300, "COCONUTS": 600, "BERRIES": 250, "DIVING_GEAR": 50, "BAGUETTE": 150, "DIP": 300, "UKULELE": 70, "PICNIC_BASKET": 70}

    ############################

    ## LEVERS
    pearlsBananas = True
    pinasCoconuts = True
    mayberries = True
    diving_gear = True
    baskets = True

    ### PEARLS AND BANANAS
    LAST_TIMESTAMP = -100000
    ############################

    ### PINA COLADAS AND COCONUTS

    MODE = "NEUTRAL" #the three modes are NEUTRAL, LONG_PINA, and LONG_COCO, PINA_HOLD, and COCO_HOLD
    STANDARD_DEVIATIONS = 0.5
    ############################

    ### DOLPHINS AND GOGGLES
    LAST_DOLPHIN_SIGHTING = -1
    DOLPHIN_WINDOW1 = 100
    DOLPHIN_WINDOW2 = 200
    DOLPHIN_MODE = "NEUTRAL"
    DELTA_LIMIT = 6
    ############################

    ### BASKETS
    BASKET_MODE = "NEUTRAL"
    BASKET_STDS = 1
    ############################



    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}

        order_depth: OrderDepth = state.order_depths
        self.COUNT += 1
        print("...")
        for product in state.order_depths.keys():
            orders: list[Order] = []
            best_ask = min(order_depth[product].sell_orders.keys())
            best_ask_volume = order_depth[product].sell_orders[best_ask]
            best_bid = max(order_depth[product].buy_orders.keys())
            best_bid_volume = order_depth[product].buy_orders[best_bid]
            timestep = state.timestamp

            if product not in self.stats["asks"].keys():
                self.stats["asks"][product] = []
                self.stats["bids"][product] = []
                self.stats["avg_prices"][product] = []
                self.stats["askVolumes"][product] = []
                self.stats["bidVolumes"][product] = []
            self.stats["asks"][product].append(best_ask)
            self.stats["bids"][product].append(best_bid)
            self.stats["avg_prices"][product].append((best_ask + best_bid)/2)
            self.stats["askVolumes"][product].append(best_ask_volume)
            self.stats["bidVolumes"][product].append(best_bid_volume)
            # if the length is > 250, remove the first element
            if len(self.stats["asks"][product]) > 250:
                self.stats["asks"][product].pop(0)
                self.stats["bids"][product].pop(0)
                self.stats["avg_prices"][product].pop(0)
                self.stats["askVolumes"][product].pop(0)
                self.stats["bidVolumes"][product].pop(0)

            try:
                position = state.position[product]
            except:
                position = 0

            buy = False #experiment with not including this
            sell = False


            if product in ["PEARLS", "BANANAS"] and self.pearlsBananas and product in state.market_trades:
                trades = state.market_trades[product]
                for trade in trades: # TODO: experiment with fixed quantities
                    if not buy and trade.buyer in ["Paris", "Pablo", "Gary"]: # these guys make bad trades, so sell to them
                        orders.append(Order(product, trade.price, -max(0,min(1, self.POSITION_LIMIT[product] + position))))
                        print("SELL", str(-max(0,min(1, self.POSITION_LIMIT[product] + position))) + "x", trade.price)
                        buy = True
                    elif not sell and trade.seller in ["Paris", "Pablo", "Gary"]: # these guys make bad trades, so buy to them
                        orders.append(Order(product, trade.price, max(0,min(1, self.POSITION_LIMIT[product] - position))))
                        print("BUY", str(max(0,min(1, self.POSITION_LIMIT[product] - position))) + "x", trade.price)
                        sell = True
                # n=12
                # k=0.67
                # value = self.stats["avg_prices"][product][-1]
                # curr_price = value

                # ## MCGINLEY STRATEGY
                # if state.timestamp != 0:
                #     mcginley_price = self.stats["acceptable_price"][product]
                # else:
                #     mcginley_price = value
                

                # n=12
                # k=0.67
                # curr_price = value

                # # first iteration
                # if self.COUNT == 1:
                #     self.stats["acceptable_price"][product] = curr_price
                #     # don't place orders in the first iteration
                #     result[product] = orders
                # else:
                #     mcginley_price = mcginley_price + (curr_price-mcginley_price)/(k * n * (curr_price/mcginley_price)**4)

                #     self.stats["acceptable_price"][product] = mcginley_price
                
                #     acceptable_price = self.stats["acceptable_price"][product]
                #     ##############################

    

                #     ## MCGINLEY ORDERS
                #     if best_ask < acceptable_price: #second part of and is so that orders don't overlap, which lets me individually keep track of positions
                #         # print("BUY", str(-best_ask_volume) + "x", best_ask)
                #         orders.append(Order(product, best_ask, max(0,min(-best_ask_volume, self.POSITION_LIMIT[product] - position))))

                #     if best_bid > acceptable_price: #second part of and is so that orders don't overlap, which lets me individually keep track of positions
                #         # print("SELL", str(best_bid_volume) + "x", best_bid)
                #         orders.append(Order(product, best_bid, -max(0,min(best_bid_volume, self.POSITION_LIMIT[product] + position))))
                #     ##############################
                    
                result[product] = orders

        self.LAST_TIMESTAMP = state.timestamp
        # print('\n----------------------------------------------------------------------------------------------------\n')
        return result