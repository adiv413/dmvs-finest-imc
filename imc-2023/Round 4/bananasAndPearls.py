from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order


class Trader:

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

    ### PEARLS AND BANANAS
    LAST_TIMESTAMP = -100000
    POSITION_LIMIT = {"BANANAS" : 20, "PEARLS": 20, "PINA_COLADAS": 300, "COCONUTS": 600, "BERRIES": 250, "DIVING_GEAR": 50, "BAGUETTE": 150, "DIP": 300, "UKULELE": 70, "PICNIC_BASKET": 70}
    COUNT = 0

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        result = {}
        order_depth: OrderDepth = state.order_depths
        self.COUNT += 1

        for product in state.order_depths.keys():
            if product in ["BANANAS", "PEARLS"]:
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

                best_bid = self.stats["bids"][product][-1]
                best_ask = self.stats["asks"][product][-1]
                best_bid_volume = self.stats["bidVolumes"][product][-1]
                best_ask_volume = self.stats["askVolumes"][product][-1]
                value = self.stats["avg_prices"][product][-1]

                if state.timestamp != 0:
                    mcginley_price = self.stats["acceptable_price"][product]
                else:
                    mcginley_price = value

                if product not in self.stats["asks"]:
                    self.stats["asks"][product] = []
                if product not in self.stats["bids"]:
                    self.stats["bids"][product] = []
                
                self.stats["asks"][product].append(best_ask)
                self.stats["bids"][product].append(best_bid)

                n=12
                k=0.67
                curr_price = value

                # first iteration
                if self.COUNT == 1:
                    self.stats["acceptable_price"][product] = curr_price
                    # don't place orders in the first iteration
                    result[product] = orders
                else:
                    mcginley_price = mcginley_price + (curr_price-mcginley_price)/(k * n * (curr_price/mcginley_price)**4)

                    self.stats["acceptable_price"][product] = mcginley_price
                
                    acceptable_price = self.stats["acceptable_price"][product]
                    ##############################

                    ## MCGINLEY ORDERS
                    if best_ask < acceptable_price: #second part of and is so that orders don't overlap, which lets me individually keep track of positions
                        # print("BUY", str(-best_ask_volume) + "x", best_ask)
                        orders.append(Order(product, best_ask, max(0,min(-best_ask_volume, self.POSITION_LIMIT[product] - position))))
                    

                    if best_bid > acceptable_price: #second part of and is so that orders don't overlap, which lets me individually keep track of positions
                        # print("SELL", str(best_bid_volume) + "x", best_bid)
                        orders.append(Order(product, best_bid, -max(0,min(best_bid_volume, self.POSITION_LIMIT[product] + position))))
                    
                    ##############################
                    
                    result[product] = orders
        return result