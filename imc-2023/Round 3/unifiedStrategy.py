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
    ############################

    ## LEVERS
    pearlsBananas = True
    pinasCoconuts = True
    mayberries = True
    diving_gear = True

    ### PEARLS AND BANANAS
    ## MARKET MAKING PARAMETERS
    RISK_ADJUSTMENT = {"BANANAS" : 0.1, "PEARLS" : 0.1}
    ORDER_VOLUME = {"BANANAS" : 4, "PEARLS" : 5}
    HALF_SPREAD_SIZE = {"BANANAS": 2, "PEARLS": 3}
    ############################
    ## POSITION SIZING PARAMS
    MM_POSITION_LIMIT = {"BANANAS" : 8, "PEARLS" : 10}
    MM_POSITION = {"BANANAS" : 0, "PEARLS" : 0}
    MM_LAST_ORDER_PRICE = {"BANANAS" : {"BUY": 0, "SELL": 0}, "PEARLS" : {"BUY": 0, "SELL": 0}}
    ############################
    MCGINLEY_POSITION_LIMIT = {"BANANAS" : 12, "PEARLS" : 10}
    MCGINLEY_POSITION = {"BANANAS" : 0, "PEARLS" : 0,}
    MCGINLEY_LAST_ORDER_PRICE = {"BANANAS" : {"BUY": 0, "SELL": 0}, "PEARLS" : {"BUY": 0, "SELL": 0}}
    ############################
    LAST_TIMESTAMP = -100000
    ############################

    ### PINA COLADAS AND COCONUTS
    POSITION_LIMIT = {"PINA_COLADAS": 300, "COCONUTS": 600, "BERRIES": 250, "DIVING_GEAR": 50}

    MODE = "NEUTRAL" #the three modes are NEUTRAL, LONG_PINA, and LONG_COCO, PINA_HOLD, and COCO_HOLD
    STANDARD_DEVIATIONS = 0.5
    ############################

    ### DOLPHINS AND GOGGLES
    LAST_DOLPHIN_SIGHTING = -1
    DOLPHIN_WINDOW1 = 100
    DOLPHIN_WINDOW2 = 200
    DOLPHIN_MODE = "NEUTRAL"
    DELTA_LIMIT = 5
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


            if product in ["PEARLS", "BANANAS"] and self.pearlsBananas:
                ##GET TRADES
                try:
                    own_trades = state.own_trades[product]
                except:
                    own_trades = []
                ##############################

                ## CALCULATING THE POSITION SIZE OF MARKET MAKING
                for trade in own_trades:
                    if trade.timestamp == self.LAST_TIMESTAMP:
                        if trade.buyer == "SUBMISSION" and trade.price == self.MM_LAST_ORDER_PRICE[product]["BUY"]:
                            self.MM_POSITION[product] += trade.quantity
                        elif trade.seller == "SUBMISSION" and trade.price == self.MM_LAST_ORDER_PRICE[product]["SELL"]:
                            self.MM_POSITION[product] -= trade.quantity
                ##############################

                ## CALCULATING THE POSITION SIZE OF MCGINLEY
                for trade in own_trades:
                    if trade.timestamp == self.LAST_TIMESTAMP:
                        if trade.buyer == "SUBMISSION" and trade.price == self.MCGINLEY_LAST_ORDER_PRICE[product]["BUY"]:
                            self.MCGINLEY_POSITION[product] += trade.quantity
                        elif trade.seller == "SUBMISSION" and trade.price == self.MCGINLEY_LAST_ORDER_PRICE[product]["SELL"]:
                            self.MCGINLEY_POSITION[product] -= trade.quantity
                ##############################

                ## CALCULATING STATS
                best_bid = self.stats["bids"][product][-1]
                best_ask = self.stats["asks"][product][-1]
                best_bid_volume = self.stats["bidVolumes"][product][-1]
                best_ask_volume = self.stats["askVolumes"][product][-1]
                value = self.stats["avg_prices"][product][-1]
                ##############################

                ## MARKET MAKING STRATEGY
                skew = -self.MM_POSITION[product] * self.RISK_ADJUSTMENT[product]
                buy_quote = floor(value - self.HALF_SPREAD_SIZE[product] + skew)
                sell_quote = floor(value + self.HALF_SPREAD_SIZE[product] + skew)
                ##############################

                ## MCGINLEY STRATEGY
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

                    ## MARKET MAKING ORDERS
                    orders.append(Order(product, buy_quote, max(0,min(self.ORDER_VOLUME[product], self.MM_POSITION_LIMIT[product] - self.MM_POSITION[product]))))
                    orders.append(Order(product, sell_quote, -max(0,min(self.ORDER_VOLUME[product], self.MM_POSITION_LIMIT[product] + self.MM_POSITION[product]))))
                    self.MM_LAST_ORDER_PRICE[product] = {"BUY": buy_quote, "SELL": sell_quote}
                    ##############################

                    ## MCGINLEY ORDERS
                    if best_ask < acceptable_price and best_ask != buy_quote: #second part of and is so that orders don't overlap, which lets me individually keep track of positions
                        # print("BUY", str(-best_ask_volume) + "x", best_ask)
                        orders.append(Order(product, best_ask, max(0,min(-best_ask_volume, self.MCGINLEY_POSITION_LIMIT[product] - self.MCGINLEY_POSITION[product]))))
                        self.MCGINLEY_LAST_ORDER_PRICE[product]["BUY"] = best_ask
                    else:
                        self.MCGINLEY_LAST_ORDER_PRICE[product]["BUY"] = 0

                    if best_bid > acceptable_price and best_bid != sell_quote: #second part of and is so that orders don't overlap, which lets me individually keep track of positions
                        # print("SELL", str(best_bid_volume) + "x", best_bid)
                        orders.append(Order(product, best_bid, -max(0,min(best_bid_volume, self.MCGINLEY_POSITION_LIMIT[product] + self.MCGINLEY_POSITION[product]))))
                        self.MCGINLEY_LAST_ORDER_PRICE[product]["SELL"] = best_bid
                    else:
                        self.MCGINLEY_LAST_ORDER_PRICE[product]["SELL"] = 0
                    ##############################
                    
                    result[product] = orders

            if product == "BERRIES" and self.mayberries:
                 # BUY at timestep of 300k, sell at timestep of 500k
                # logger.print(self.timestep)
                start, end = 300000, 500000
                if(timestep >= start and timestep < end):
                    orders.append(Order("BERRIES", best_ask, self.POSITION_LIMIT[product] - position))
                    # logger.print("BUYING BUYING BUYING")
                    print(f'BUYING: Current position = {position}')
                elif(timestep >= end):
                    orders.append(Order("BERRIES", best_bid, -(min(self.POSITION_LIMIT[product], self.POSITION_LIMIT[product] + position))))
                    # logger.print("I AM IN THE RANGE")
                    print(f'SELLING: Current position = {position}')
                result["BERRIES"] = orders

            if product == "DIVING_GEAR" and self.diving_gear:
                print(f'Dolphin sighting: {state.observations["DOLPHIN_SIGHTINGS"]}')
                # print(f'Diving Gear Mid Price: {self.stats["avg_prices"][product][-1]}')
                dSighting = state.observations["DOLPHIN_SIGHTINGS"]
                delta = dSighting - self.LAST_DOLPHIN_SIGHTING
                # print(f'Delta: {delta}')
                if self.COUNT >= self.DOLPHIN_WINDOW2:
                    MA1 = sum(self.stats["avg_prices"][product][-self.DOLPHIN_WINDOW1:])/self.DOLPHIN_WINDOW1
                    MA2 = sum(self.stats["avg_prices"][product][-self.DOLPHIN_WINDOW2:])/self.DOLPHIN_WINDOW2
                    # print(f'MA1: {MA1}')
                    # print(f'MA2: {MA2}')
                    if delta < -self.DELTA_LIMIT:
                        self.DOLPHIN_MODE = "NEW_SHORT"
                    elif delta > self.DELTA_LIMIT:
                        self.DOLPHIN_MODE = "NEW_LONG"

                    if self.DOLPHIN_MODE == "NEW_SHORT" and MA1 < MA2:
                        self.DOLPHIN_MODE = "SHORT"
                    elif self.DOLPHIN_MODE == "SHORT" and MA1 > MA2:
                        self.DOLPHIN_MODE = "NEUTRAL"
                    elif self.DOLPHIN_MODE == "NEW_LONG" and MA1 > MA2:
                        self.DOLPHIN_MODE = "LONG"
                    elif self.DOLPHIN_MODE == "LONG" and MA1 < MA2:
                        self.DOLPHIN_MODE = "NEUTRAL"
                    
                    # if self.COUNT > 500:
                    #     self.DOLPHIN_MODE = "NEW_LONG"
                    # if self.COUNT > 600:
                    #     self.DOLPHIN_MODE = "NEUTRAL"
                    # if self.COUNT > 700:
                    #     self.DOLPHIN_MODE = "NEW_SHORT"
                    # if self.COUNT > 800:
                    #     self.DOLPHIN_MODE = "NEUTRAL"
                    
                    if self.DOLPHIN_MODE == "NEW_SHORT" or self.DOLPHIN_MODE == "SHORT":
                        # print("SHORTING: Current position = ", position)
                        orders.append(Order("DIVING_GEAR", best_bid, -(min(self.POSITION_LIMIT[product], self.POSITION_LIMIT[product] + position))))      
                    elif self.DOLPHIN_MODE == "NEW_LONG" or self.DOLPHIN_MODE == "LONG":
                        # print("LONGING: Current position = ", position)
                        orders.append(Order("DIVING_GEAR", best_ask, self.POSITION_LIMIT[product] - position))
                    elif self.DOLPHIN_MODE == "NEUTRAL":
                        if position > 0:
                            # print("SELLING: Current position = ", position)
                            orders.append(Order("DIVING_GEAR", best_bid, -position))
                        elif position < 0:
                            # print("BUYING: Current position = ", position)
                            orders.append(Order("DIVING_GEAR", best_ask, -position))
                self.LAST_DOLPHIN_SIGHTING = dSighting
                result["DIVING_GEAR"] = orders


        if self.pearlsBananas:
            cocoPrice = self.stats["avg_prices"]["COCONUTS"][-1]
            pinaPrice = self.stats["avg_prices"]["PINA_COLADAS"][-1]

            try:
                cocoPosition = state.position["COCONUTS"]
            except:
                cocoPosition = 0
            try:
                pinaPosition = state.position["PINA_COLADAS"]
            except:
                pinaPosition = 0

            #calculate the log average price of pinaPrics/cocoPrices
            currentLogVal = log(pinaPrice / cocoPrice)
            logAvg = 0.6288272247232621
            #calculate the standard deviation of logValues
            logStd =  0.002382788768726835

            pinaOrders: List[Order] = []
            cocoOrders: List[Order] = []
            
            if currentLogVal > logAvg + self.STANDARD_DEVIATIONS*logStd:
                self.MODE = "LONG_COCO"
            elif currentLogVal < logAvg - self.STANDARD_DEVIATIONS*logStd:
                self.MODE = "LONG_PINA"
            elif self.MODE == "PINA_HOLD" and currentLogVal > logAvg or self.MODE == "LONG_COCO" and currentLogVal < logAvg:
                self.MODE = "NEUTRAL"
            elif self.MODE == "LONG_PINA" and currentLogVal < logAvg + self.STANDARD_DEVIATIONS*logStd:
                self.MODE = "PINA_HOLD"
            elif self.MODE == "LONG_COCO" and currentLogVal > logAvg - self.STANDARD_DEVIATIONS*logStd:
                self.MODE = "COCO_HOLD"
            # print("--------------------")
            # print(self.MODE)

            position_deficit = pinaPosition*pinaPrice + cocoPosition*cocoPrice

            #print the coco ask volumes and the coco bid volumes

            if self.MODE == "LONG_PINA": #long pina, short coco
                pina_ask = self.stats["asks"]["PINA_COLADAS"][-1]
                pina_ask_volume = self.stats["askVolumes"]["PINA_COLADAS"][-1]
                coco_bid = self.stats["bids"]["COCONUTS"][-1]
                coco_bid_volume = self.stats["bidVolumes"]["COCONUTS"][-1]

                # print(f'Pina ask: {pina_ask}, Pina ask volume: {pina_ask_volume}, Coco bid: {coco_bid}, Coco bid volume: {coco_bid_volume}')
                # print(f'Pina position: {pinaPosition}, Coco position: {cocoPosition}')

                pina_market_order_size = min(-pina_ask_volume, self.POSITION_LIMIT["PINA_COLADAS"] - pinaPosition) * pinaPrice
                coco_market_order_size = min(coco_bid_volume, self.POSITION_LIMIT["COCONUTS"] + cocoPosition) * cocoPrice
                market_order_size = min(pina_market_order_size, coco_market_order_size)
                pina_adj_order = round((market_order_size - position_deficit/2)/pinaPrice)
                coco_adj_order = round((market_order_size - position_deficit/2)/cocoPrice)

                # print(f'Pina adj order: {pina_adj_order}, Coco adj order: {coco_adj_order}, market order size: {market_order_size}, position deficit: {position_deficit}')
                
                pinaOrders.append(Order("PINA_COLADAS", pina_ask, pina_adj_order))
                # print(f'Pina colada BUY order placed at quantity {pina_adj_order}, seashell amount {pina_adj_order*pinaPrice}, and current pina seashell position {pinaPosition*pinaPrice}, order price {pina_ask}')
                cocoOrders.append(Order("COCONUTS", coco_bid, -coco_adj_order))
                # print(f'Coconut SELL order placed at quantity {coco_adj_order}, seashell amount {coco_adj_order*cocoPrice}, and current coconut seashell position {cocoPosition*cocoPrice}, order price {coco_bid}')

            elif self.MODE == "LONG_COCO": #long coco, short pina
                pina_bid = self.stats["bids"]["PINA_COLADAS"][-1]
                pina_bid_volume = self.stats["bidVolumes"]["PINA_COLADAS"][-1]
                coco_ask = self.stats["asks"]["COCONUTS"][-1]
                coco_ask_volume = self.stats["askVolumes"]["COCONUTS"][-1]

                pina_market_order_size = min(pina_bid_volume, self.POSITION_LIMIT["PINA_COLADAS"] + pinaPosition) * pinaPrice
                coco_market_order_size = min(-coco_ask_volume, self.POSITION_LIMIT["COCONUTS"] - cocoPosition) * cocoPrice
                market_order_size = min(pina_market_order_size, coco_market_order_size)
                pina_adj_order = round((market_order_size - position_deficit/2)/pinaPrice)
                coco_adj_order = round((market_order_size - position_deficit/2)/cocoPrice)

                pinaOrders.append(Order("PINA_COLADAS", pina_bid, -pina_adj_order))
                # print(f'Pina colada SELL order placed at quantity {pina_adj_order}, seashell amount {pina_adj_order*pinaPrice}, and current pina seashell position {pinaPosition*pinaPrice}')
                cocoOrders.append(Order("COCONUTS", coco_ask, coco_adj_order))
                # print(f'Coconut BUY order placed at quantity {coco_adj_order}, seashell amount {coco_adj_order*cocoPrice}, and current coconut seashell position {cocoPosition*cocoPrice}')

            elif self.MODE == "NEUTRAL": #sell everything to 0
                if pinaPosition > 0:
                    pinaOrders.append(Order("PINA_COLADAS", self.stats["bids"]["PINA_COLADAS"][-1], -pinaPosition))
                    # print(f'Pina colada SELL order placed at quantity {-pinaPosition}, price {self.stats["bids"]["PINA_COLADAS"][-1]}')
                elif pinaPosition < 0:
                    pinaOrders.append(Order("PINA_COLADAS", self.stats["asks"]["PINA_COLADAS"][-1], -pinaPosition))
                    # print(f'Pina colada BUY order placed at quantity {-pinaPosition}, price {self.stats["asks"]["PINA_COLADAS"][-1]}')
                if cocoPosition > 0:
                    cocoOrders.append(Order("COCONUTS", self.stats["bids"]["COCONUTS"][-1], -cocoPosition))
                    # print(f'Coconut SELL order placed at quantity {-cocoPosition}, price {self.stats["bids"]["COCONUTS"][-1]}')
                elif cocoPosition < 0:
                    cocoOrders.append(Order("COCONUTS", self.stats["asks"]["COCONUTS"][-1], -cocoPosition))
                    # print(f'Coconut BUY order placed at quantity {-cocoPosition}, price {self.stats["asks"]["COCONUTS"][-1]}')

            result["PINA_COLADAS"] = pinaOrders
            result["COCONUTS"] = cocoOrders    
            print(f'pina position value: {pinaPosition*pinaPrice}, coco position value: {cocoPosition*cocoPrice}, net position value: {pinaPosition*pinaPrice + cocoPosition*cocoPrice}')

        self.LAST_TIMESTAMP = state.timestamp
        # print('\n----------------------------------------------------------------------------------------------------\n')
        return result