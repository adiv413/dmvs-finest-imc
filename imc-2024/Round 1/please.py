#https://kollider.medium.com/build-a-crypto-market-making-bot-in-python-d71eeae2dcd7
#https://www.reddit.com/r/algotrading/comments/6q8dp6/market_making_theory_and_application_readings/
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import collections
from collections import defaultdict
import random
import math
import copy
import numpy as np


empty_dict = {"AMETHYSTS": 0, "STARFRUIT": 0}

def def_value():
    return copy.deepcopy(empty_dict)

INF = int(1e9)

class Trader:

    position = copy.deepcopy(empty_dict)
    POSITION_LIMIT = {"AMETHYSTS" : 20, "STARFRUIT" : 20}
    volume_traded = copy.deepcopy(empty_dict)

    starfruit_cache = []
    starfruit_dim = 4

    steps = 0

    def calc_next_price_starfruit(self):
        coeffs = [0.1929,  0.1965 ,  0.2635,  0.347]
        intercept = 0
        nxt_price = intercept
        for i, val in enumerate(self.starfruit_cache):
            nxt_price += val * coeffs[i]

        return int(round(nxt_price))
    
    def values_extract(self, order_dict, buy=0):
        tot_vol = 0
        best_val = -1
        mxvol = -1

        for ask, vol in order_dict.items():
            if(buy==0):
                vol *= -1
            tot_vol += vol
            if tot_vol > mxvol:
                mxvol = vol
                best_val = ask
        
        return tot_vol, best_val
    
    def compute_orders_amethysts(self, product, order_depth, acc_bid, acc_ask):
        orders: list[Order] = []
        osell = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
        obuy = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))

        sell_vol, best_sell_price = self.values_extract(osell)
        buy_vol, best_buy_price = self.values_extract(obuy, 1)

        curr_pos = self.position[product]

        mx_with_buy = -1

        for ask, vol in osell.items():
            if ((ask < acc_bid) or ((self.position[product] < 0) and (ask == acc_bid))) and curr_pos < self.POSITION_LIMIT['AMETHYSTS']:
                mx_with_buy = max(mx_with_buy, ask)
                order_for = min(-vol, self.POSITION_LIMIT[product] - curr_pos)
                curr_pos += order_for
                assert(order_for >= 0)
                orders.append(Order(product, ask, order_for))

        mprice_actual = (best_sell_price + best_buy_price) / 2
        mprice_pred = (acc_bid + acc_ask) / 2

        undercut_buy = best_buy_price + 1
        undercut_sell = best_sell_price - 1

        bid_price = min(undercut_buy, acc_bid - 1)
        sell_price = max(undercut_sell, acc_ask + 1)

        if (curr_pos < self.POSITION_LIMIT['AMETHYSTS']) and (self.position[product] < 0):
            num = min(20, self.POSITION_LIMIT['AMETHYSTS'] - curr_pos)
            orders.append(Order(product, min(undercut_buy + 1, acc_bid - 1), num))
            curr_pos += num

        if (curr_pos < self.POSITION_LIMIT['AMETHYSTS']) and (self.position[product] > 7.5):
            num = min(20, self.POSITION_LIMIT['AMETHYSTS'] - curr_pos)
            orders.append(Order(product, min(undercut_buy - 1, acc_bid - 1), num))
            curr_pos += num

        if curr_pos < self.POSITION_LIMIT['AMETHYSTS']:
            num = min(20, self.POSITION_LIMIT['AMETHYSTS'] - curr_pos)
            orders.append(Order(product, bid_price, num))
            curr_pos += num

        curr_pos = self.position[product]

        for bid, vol in obuy.items():
            if ((bid > acc_ask) or ((self.position[product] > 0) and (bid == acc_ask))) and curr_pos > -self.POSITION_LIMIT['AMETHYSTS']:
                order_for = max(-vol, -self.POSITION_LIMIT['AMETHYSTS'] - curr_pos)
                # order_for is a negative number denoting how much we will sell
                curr_pos += order_for
                assert(order_for <= 0)
                orders.append(Order(product, bid, order_for))

        if (curr_pos > -self.POSITION_LIMIT['AMETHYSTS']) and (self.position[product] > 0):
            num = max(-20, -self.POSITION_LIMIT['AMETHYSTS'] - curr_pos)
            orders.append(Order(product, max(undercut_sell - 1, acc_ask + 1), num))
            curr_pos += num

        if (curr_pos > -self.POSITION_LIMIT['AMETHYSTS']) and (self.position[product] < -7.5):
            num = max(-20, -self.POSITION_LIMIT['AMETHYSTS'] - curr_pos)
            orders.append(Order(product, max(undercut_sell + 1, acc_ask + 1), num))
            curr_pos += num

        if curr_pos > -self.POSITION_LIMIT['AMETHYSTS']:
            num = max(-20, -self.POSITION_LIMIT['AMETHYSTS'] - curr_pos)
            orders.append(Order(product, sell_price, num))
            curr_pos += num

        return orders
    
    def compute_orders_regression(self, product, order_depth, acc_bid, acc_ask, LIMIT):
        orders: list[Order] = []

        osell = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
        obuy = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))

        sell_vol, best_sell_pr = self.values_extract(osell)
        buy_vol, best_buy_pr = self.values_extract(obuy, 1)

        cpos = self.position[product]

        for ask, vol in osell.items():
            if ((ask <= acc_bid) or ((self.position[product]<0) and (ask == acc_bid+1))) and cpos < LIMIT:
                order_for = min(-vol, LIMIT - cpos)
                cpos += order_for
                assert(order_for >= 0)
                orders.append(Order(product, ask, order_for))

        undercut_buy = best_buy_pr + 1
        undercut_sell = best_sell_pr - 1

        bid_pr = min(undercut_buy, acc_bid) # we will shift this by 1 to beat this price
        sell_pr = max(undercut_sell, acc_ask)

        if cpos < LIMIT:
            num = LIMIT - cpos
            orders.append(Order(product, bid_pr, num))
            cpos += num
        
        cpos = self.position[product]

        for bid, vol in obuy.items():
            if ((bid >= acc_ask) or ((self.position[product]>0) and (bid+1 == acc_ask))) and cpos > -LIMIT:
                order_for = max(-vol, -LIMIT-cpos)
                # order_for is a negative number denoting how much we will sell
                cpos += order_for
                assert(order_for <= 0)
                orders.append(Order(product, bid, order_for))

        if cpos > -LIMIT:
            num = -LIMIT-cpos
            orders.append(Order(product, sell_pr, num))
            cpos += num

        return orders
    
    def compute_orders(self, product, order_depth, acc_bid, acc_ask):
        if product == 'AMETHYSTS':
            return self.compute_orders_amethysts(product, order_depth, acc_bid, acc_ask)
        if product == 'STARFRUIT':
            return self.compute_orders_regression(product, order_depth, acc_bid, acc_ask, self.POSITION_LIMIT[product])

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {'AMETHYSTS': [], 'STARFRUIT': []}

        for key, val in state.position.items():
            self.position[key] = val
        print()
        for key, val in self.position.items():
            print(f'{key} pos: {val}')

        timestamp = state.timestamp

        if len(self.starfruit_cache) == self.starfruit_dim:
            self.starfruit_cache.pop(0)

        _, bsell_starfruit = self.values_extract(collections.OrderedDict(sorted(state.order_depths['STARFRUIT'].sell_orders.items())))
        _, bbuy_starfruit = self.values_extract(collections.OrderedDict(sorted(state.order_depths['STARFRUIT'].buy_orders.items(), reverse=True)), 1)

        self.starfruit_cache.append((bsell_starfruit + bbuy_starfruit) / 2)

        INF = int(1e9)

        starfruit_lb = -INF
        starfruit_ub = INF

        if len(self.starfruit_cache) == self.starfruit_dim:
            starfruit_lb = self.calc_next_price_starfruit() - 1
            starfruit_ub = self.calc_next_price_starfruit() + 1

        amethysts_lb = 10000
        amethysts_ub = 10000

        acc_bid = {'AMETHYSTS': amethysts_lb, 'STARFRUIT': starfruit_lb}
        acc_ask = {'AMETHYSTS': amethysts_ub, 'STARFRUIT': starfruit_ub}

        self.steps += 1

        for product in ['AMETHYSTS', 'STARFRUIT']:
            order_depth: OrderDepth = state.order_depths[product]
            orders = self.compute_orders(product, order_depth, acc_bid[product], acc_ask[product])
            result[product] += orders

        return result, 0, "SAMPLE"