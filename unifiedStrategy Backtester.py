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
    pearlsBananas = False
    pinasCoconuts = False
    mayberries = False
    diving_gear = False
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
            try:
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
            except:
                if product == "PINA_COLADAS" or product == "COCONUTS":
                    self.pinasCoconuts = False
                elif product in ["BAGUETTE", "UKULELE", "DIP", "PICNIC_BASKET"]:
                    self.baskets = False
                elif product == "DIVING_GEAR":
                    self.diving_gear = False
                elif product == "BERRIES":
                    self.mayberries = False
                elif product in ["PEARLS", "BANANAS"]:
                    self.pearlsBananas = False

            

            try:
                position = state.position[product]
            except:
                position = 0


            if product in ["PEARLS", "BANANAS"] and self.pearlsBananas:

                n=12
                k=0.67
                value = self.stats["avg_prices"][product][-1]
                curr_price = value

                ## MCGINLEY STRATEGY
                if state.timestamp != 0:
                    mcginley_price = self.stats["acceptable_price"][product]
                else:
                    mcginley_price = value
                

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

            if product == "BERRIES" and self.mayberries:
                 # BUY at timestep of 300k, sell at timestep of 500k
                # logger.print(self.timestep)
                long, short, close = 300000, 500000, 750000
                if(timestep >= long and timestep < short):
                    orders.append(Order("BERRIES", best_ask, self.POSITION_LIMIT[product] - position))
                    # logger.print("BUYING BUYING BUYING")
                    # print(f'BUYING: Current position = {position}')
                elif(timestep >= short and timestep < close):
                    orders.append(Order("BERRIES", best_bid, -(min(self.POSITION_LIMIT[product], self.POSITION_LIMIT[product] + position))))
                    # logger.print("I AM IN THE RANGE")
                    # print(f'SELLING: Current position = {position}')
                elif timestep >= close:
                    orders.append(Order("BERRIES", best_bid, -position))
                    # logger.print("I AM IN THE RANGE")
                    # print(f'SELLING: Current position = {position}')
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
                        print("DOLPHIN SIGHTING: SHORT")
                        print("delta: ", delta)
                    elif delta > self.DELTA_LIMIT:
                        self.DOLPHIN_MODE = "NEW_LONG"
                        print("DOLPHIN SIGHTING: LONG")
                        print("delta: ", delta)

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


        if self.pinasCoconuts:
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
            elif self.MODE == "PINA_HOLD" and currentLogVal > logAvg or self.MODE == "COCO_HOLD" and currentLogVal < logAvg:
                self.MODE = "NEUTRAL"
            elif self.MODE == "LONG_PINA" and currentLogVal > logAvg - self.STANDARD_DEVIATIONS*logStd:
                self.MODE = "PINA_HOLD"
            elif self.MODE == "LONG_COCO" and currentLogVal < logAvg + self.STANDARD_DEVIATIONS*logStd:
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
                
                pina_market_order_size = min(-pina_ask_volume, self.POSITION_LIMIT["PINA_COLADAS"] - max(0,pinaPosition)) * pinaPrice
                coco_market_order_size = min(coco_bid_volume, self.POSITION_LIMIT["COCONUTS"] + min(0, cocoPosition)) * cocoPrice
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

                pina_market_order_size = min(pina_bid_volume, self.POSITION_LIMIT["PINA_COLADAS"] + min(0, pinaPosition)) * pinaPrice
                coco_market_order_size = min(-coco_ask_volume, self.POSITION_LIMIT["COCONUTS"] - max(0,cocoPosition)) * cocoPrice
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
            # print(f'pina position value: {pinaPosition*pinaPrice}, coco position value: {cocoPosition*cocoPrice}, net position value: {pinaPosition*pinaPrice + cocoPosition*cocoPrice}')

        if self.baskets:
            baguettePrice = self.stats["avg_prices"]["BAGUETTE"][-1]
            dipPrice = self.stats["avg_prices"]["DIP"][-1]
            ukulelePrice = self.stats["avg_prices"]["UKULELE"][-1]
            basketPrice = self.stats["avg_prices"]["PICNIC_BASKET"][-1]
            proxyBasketPrice = 2*baguettePrice + 4*dipPrice + ukulelePrice

            try:
                baguettePosition = state.position["BAGUETTE"]
            except:
                baguettePosition = 0
            try:
                dipPosition = state.position["DIP"]
            except:
                dipPosition = 0
            try:
                ukulelePosition = state.position["UKULELE"]
            except:
                ukulelePosition = 0
            try:
                basketPosition = state.position["PICNIC_BASKET"]
            except:
                basketPosition = 0
            proxyBasketPosition = (baguettePosition/2 + dipPosition/4 + ukulelePosition)/7

            currentLogVal = log(basketPrice/proxyBasketPrice)
            logAvg = 0.005088082667016638
            logStd = 0.0016822947277079987
            proxy_basket_positioncap = 70

            baguetteOrders: List[Order] = []
            dipOrders: List[Order] = []
            ukuleleOrders: List[Order] = []
            basketOrders: List[Order] = []

            if currentLogVal > logAvg + self.BASKET_STDS*logStd:
                self.BASKET_MODE = "LONG_PROXY"
            elif currentLogVal < logAvg - self.BASKET_STDS*logStd:
                self.BASKET_MODE = "LONG_BASKET"
            elif self.BASKET_MODE == "LONG_PROXY" and currentLogVal < logAvg + self.BASKET_STDS*logStd:
                self.BASKET_MODE = "HOLD_PROXY"
            elif self.BASKET_MODE == "LONG_BASKET" and currentLogVal > logAvg - self.BASKET_STDS*logStd:
                self.BASKET_MODE = "HOLD_BASKET"
            
            overall_position_deficit = basketPosition*basketPrice + baguettePosition*baguettePrice + dipPosition*dipPrice + ukulelePosition*ukulelePrice
            perfect_position_ratios = {"BAGUETTE": 2/7, "DIP": 4/7, "UKULELE": 1/7}
            total_position = baguettePosition + dipPosition + ukulelePosition
            if total_position == 0:
                position_ratio_deficits = {"BAGUETTE": 0, "DIP": 0, "UKULELE": 0}
            else:
                position_ratios = {"BAGUETTE": baguettePosition/total_position, "DIP": dipPosition/total_position, "UKULELE": ukulelePosition/total_position}
                position_ratio_deficits = {"BAGUETTE": perfect_position_ratios["BAGUETTE"] - position_ratios["BAGUETTE"], "DIP": perfect_position_ratios["DIP"] - position_ratios["DIP"], "UKULELE": perfect_position_ratios["UKULELE"] - position_ratios["UKULELE"]}

            if self.BASKET_MODE == "LONG_BASKET":
                # print("LONG BASKET SHORT PROXY")
                basket_ask = self.stats["asks"]["PICNIC_BASKET"][-1]
                basket_ask_volume = self.stats["askVolumes"]["PICNIC_BASKET"][-1]
                proxy_bid_volume = min(self.stats["bidVolumes"]["BAGUETTE"][-1]/2, self.stats["bidVolumes"]["DIP"][-1]/4, self.stats["bidVolumes"]["UKULELE"][-1])

                basket_market_order_size = min(-basket_ask_volume, self.POSITION_LIMIT["PICNIC_BASKET"] - max(0, basketPosition)) * basketPrice
                proxy_market_order_size = min(proxy_bid_volume, proxy_basket_positioncap + min(0, proxyBasketPosition)) * proxyBasketPrice
                market_order_size = min(basket_market_order_size, proxy_market_order_size)
                basket_adj_order = round((market_order_size - overall_position_deficit/2) / basketPrice)
                proxy_adj_order = round((-market_order_size + overall_position_deficit/2) / proxyBasketPrice)
                basketOrders.append(Order("PICNIC_BASKET", basket_ask, basket_adj_order))

                print(f'basket_adj_order: {basket_adj_order}')

                try:
                    productAdjustments = {key: value/abs(value) for key, value in position_ratio_deficits.items()}
                except:
                    productAdjustments = {"BAGUETTE": 0, "DIP": 0, "UKULELE": 0}
                
                baguetteOrders.append(Order("BAGUETTE", self.stats["bids"]["BAGUETTE"][-1], 2*proxy_adj_order + productAdjustments["BAGUETTE"]))
                dipOrders.append(Order("DIP", self.stats["bids"]["DIP"][-1], 4*proxy_adj_order + productAdjustments["DIP"]))
                ukuleleOrders.append(Order("UKULELE", self.stats["bids"]["UKULELE"][-1], proxy_adj_order + productAdjustments["UKULELE"]))

            elif self.BASKET_MODE == "LONG_PROXY":
                # print("SHORT BASKET LONG PROXY")
                basket_bid = self.stats["bids"]["PICNIC_BASKET"][-1]
                basket_bid_volume = self.stats["bidVolumes"]["PICNIC_BASKET"][-1]
                proxy_ask_volume = min(self.stats["askVolumes"]["BAGUETTE"][-1]/2, self.stats["askVolumes"]["DIP"][-1]/4, self.stats["askVolumes"]["UKULELE"][-1])

                basket_market_order_size = min(basket_bid_volume, self.POSITION_LIMIT["PICNIC_BASKET"] + min(0, basketPosition)) * basketPrice
                proxy_market_order_size = min(-proxy_ask_volume, proxy_basket_positioncap - max(0, proxyBasketPosition)) * proxyBasketPrice
                market_order_size = min(basket_market_order_size, proxy_market_order_size)
                basket_adj_order = round((-market_order_size - overall_position_deficit/2) / basketPrice)
                proxy_adj_order = round((market_order_size + overall_position_deficit/2) / proxyBasketPrice)
                basketOrders.append(Order("PICNIC_BASKET", basket_bid, basket_adj_order))

                try:
                    productAdjustments = {key: value/abs(value) for key, value in position_ratio_deficits.items()}
                except:
                    productAdjustments = {"BAGUETTE": 0, "DIP": 0, "UKULELE": 0}

                baguetteOrders.append(Order("BAGUETTE", self.stats["asks"]["BAGUETTE"][-1], 2*proxy_adj_order + productAdjustments["BAGUETTE"]))
                dipOrders.append(Order("DIP", self.stats["asks"]["DIP"][-1], 4*proxy_adj_order + productAdjustments["DIP"]))
                ukuleleOrders.append(Order("UKULELE", self.stats["asks"]["UKULELE"][-1], proxy_adj_order + productAdjustments["UKULELE"]))

            # print(f'Basket position value: {basketPosition*basketPrice}')
            # print(f'Basket position: {basketPosition}')
            # print(f'Proxy basket position value: {baguettePosition*baguettePrice + dipPosition*dipPrice + ukulelePosition*ukulelePrice}')
            # print(f'perfect_position_ratios: {2/7}, {4/7}, {1/7}')
            # try:
            #     print(f'position_ratios: {baguettePosition/total_position}, {dipPosition/total_position}, {ukulelePosition/total_position}')
            # except:
            #     print(f'position_ratios: {0}, {0}, {0}')
            
            
            result["PICNIC_BASKET"] = basketOrders
            result["BAGUETTE"] = baguetteOrders
            result["DIP"] = dipOrders
            result["UKULELE"] = ukuleleOrders

        self.LAST_TIMESTAMP = state.timestamp
        self.pinasCoconuts = True
        self.baskets = True
        self.diving_gear = True
        self.mayberries = True
        self.pearlsBananas = True
        # print('\n----------------------------------------------------------------------------------------------------\n')
        return result