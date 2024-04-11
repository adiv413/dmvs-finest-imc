from typing import Dict, List
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from math import floor
import collections
import jsonpickle
from typing import Any
import json

class Logger:
    def __init__(self) -> None:
        self.logs = ""
        self.max_log_length = 3750

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]], conversions: int, trader_data: str) -> None:
        base_length = len(self.to_json([
            self.compress_state(state, ""),
            self.compress_orders(orders),
            conversions,
            "",
            "",
        ]))

        # We truncate state.traderData, trader_data, and self.logs to the same max. length to fit the log limit
        max_item_length = (self.max_log_length - base_length) // 3

        print(self.to_json([
            self.compress_state(state, self.truncate(state.traderData, max_item_length)),
            self.compress_orders(orders),
            conversions,
            self.truncate(trader_data, max_item_length),
            self.truncate(self.logs, max_item_length),
        ]))

        self.logs = ""

    def compress_state(self, state: TradingState, trader_data: str) -> list[Any]:
        return [
            state.timestamp,
            trader_data,
            self.compress_listings(state.listings),
            self.compress_order_depths(state.order_depths),
            self.compress_trades(state.own_trades),
            self.compress_trades(state.market_trades),
            state.position,
            self.compress_observations(state.observations),
        ]

    def compress_listings(self, listings: dict[Symbol, Listing]) -> list[list[Any]]:
        compressed = []
        for listing in listings.values():
            compressed.append([listing["symbol"], listing["product"], listing["denomination"]])

        return compressed

    def compress_order_depths(self, order_depths: dict[Symbol, OrderDepth]) -> dict[Symbol, list[Any]]:
        compressed = {}
        for symbol, order_depth in order_depths.items():
            compressed[symbol] = [order_depth.buy_orders, order_depth.sell_orders]

        return compressed

    def compress_trades(self, trades: dict[Symbol, list[Trade]]) -> list[list[Any]]:
        compressed = []
        for arr in trades.values():
            for trade in arr:
                compressed.append([
                    trade.symbol,
                    trade.price,
                    trade.quantity,
                    trade.buyer,
                    trade.seller,
                    trade.timestamp,
                ])

        return compressed

    def compress_observations(self, observations: Observation) -> list[Any]:
        conversion_observations = {}
        for product, observation in observations.conversionObservations.items():
            conversion_observations[product] = [
                observation.bidPrice,
                observation.askPrice,
                observation.transportFees,
                observation.exportTariff,
                observation.importTariff,
                observation.sunlight,
                observation.humidity,
            ]

        return [observations.plainValueObservations, conversion_observations]

    def compress_orders(self, orders: dict[Symbol, list[Order]]) -> list[list[Any]]:
        compressed = []
        for arr in orders.values():
            for order in arr:
                compressed.append([order.symbol, order.price, order.quantity])

        return compressed

    def to_json(self, value: Any) -> str:
        return json.dumps(value, cls=ProsperityEncoder, separators=(",", ":"))

    def truncate(self, value: str, max_length: int) -> str:
        if len(value) <= max_length:
            return value

        return value[:max_length - 3] + "..."

logger = Logger()


class Trader:

    products = ["AMETHYSTS", "STARFRUIT"]
    POSITION_LIMIT = {"AMETHYSTS": 20, "STARFRUIT": 20}

    AMETHYST_PRICE = 10000
    STARFRUIT_PRICES_NO_SPIKE = []
    STARFRUIT_ORDER_QUANTITY = 10
    #idea - use some sort of scaling to reduce the amount of buying when position is net positive, and reduce amount of
    #selling when position is net negative. This will allow us to make trades on all the spikes while remaining
    # position neutral on average.
    def market_make_amethyst(self, product, order_depth, position):
        orders: list[Order] = []

        osell = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
        obuy = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))
        buyReserve = min(20, 20-position)
        sellReserve = max(-20, -20-position)
        ## Market Taking
        #BUYING
        print(f'Position: {position}')
        for sellOrder in osell:
            if sellOrder < self.AMETHYST_PRICE:
                orders.append(Order(product, sellOrder, min(buyReserve,-osell[sellOrder])))
                buyReserve -= min(buyReserve,-osell[sellOrder])
                print(f'Market Taking Buy Order at {sellOrder} with volume {min(buyReserve,-osell[sellOrder])}')
            elif sellOrder == self.AMETHYST_PRICE and position < 0:
                orders.append(Order(product, sellOrder, min(buyReserve,-osell[sellOrder])))
                buyReserve -= min(buyReserve,-osell[sellOrder])
                print(f'Market Taking Buy Order at {sellOrder} with volume {min(buyReserve,-osell[sellOrder])}')
               
        #BUYING

        #SELLING    
        for buyOrder in obuy:
            if buyOrder > self.AMETHYST_PRICE:
                orders.append(Order(product, buyOrder, max(sellReserve,-obuy[buyOrder])))
                sellReserve -= max(sellReserve,-obuy[buyOrder])
                print(f'Market Taking Sell Order at {buyOrder} with volume {max(sellReserve,-obuy[buyOrder])}')
            elif buyOrder == self.AMETHYST_PRICE and position > 0:
                orders.append(Order(product, buyOrder, max(sellReserve,-obuy[buyOrder])))
                sellReserve -= max(sellReserve,-obuy[buyOrder])
                print(f'Market Taking Sell Order at {buyOrder} with volume {max(sellReserve,-obuy[buyOrder])}')
               
        # SELLING

        print(f'Position: {position}')
        ###################################################################

        ## Market Making
        best_bid = list(obuy.keys())[0]
        best_ask = list(osell.keys())[0]
        #sell order
        orders.append(Order(product, max(best_ask-1, self.AMETHYST_PRICE+1), sellReserve))
        print(f'Market Making Sell Order at {max(best_ask-1, self.AMETHYST_PRICE+1)} with volume {sellReserve}')
        #buy order
        orders.append(Order(product, min(best_bid+1, self.AMETHYST_PRICE-1), buyReserve))
        print(f'Market Making Buy Order at {min(best_bid+1, self.AMETHYST_PRICE-1)} with volume {buyReserve}')
        ###################################################################
        
        return orders

    def compute_orders_starfruit(self, product, order_depth, position, period = 10):
        orders: list[Order] = []

        best_bid = max(order_depth.buy_orders.keys())
        best_ask = min(order_depth.sell_orders.keys())
        best_bid_volume = order_depth.buy_orders[best_bid]
        best_ask_volume = order_depth.sell_orders[best_ask]
        spread = best_ask - best_bid
        price = (best_ask + best_bid) / 2

        if spread > 4:
            if len(self.STARFRUIT_PRICES_NO_SPIKE) < period:
                self.STARFRUIT_PRICES_NO_SPIKE.append(price)
            else:
                self.STARFRUIT_PRICES_NO_SPIKE.pop(0)
                self.STARFRUIT_PRICES_NO_SPIKE.append(price)


        if len(self.STARFRUIT_PRICES_NO_SPIKE) == period:
            MA = sum(self.STARFRUIT_PRICES_NO_SPIKE) / len(self.STARFRUIT_PRICES_NO_SPIKE)
            if best_ask < MA:
                orders.append(Order(product, best_ask, min(20,-best_ask_volume)))
                # orders.append(Order(product, best_ask, self.STARFRUIT_ORDER_QUANTITY))
                # orders.append(Order(product, best_ask, 1))
            if best_bid > MA:
                orders.append(Order(product, best_bid, max(-20,-best_bid_volume)))
                # orders.append(Order(product, best_bid, -2*self.STARFRUIT_ORDER_QUANTITY))
                # orders.append(Order(product, best_bid, -1))``

        # print(position)
        return orders

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}

        timestamp = state.timestamp
        if timestamp !=0:
            traderData = jsonpickle.decode(state.traderData)
            self.STARFRUIT_PRICES_NO_SPIKE = traderData

        for product in self.products:
            orders: list[Order] = []
            order_depth: OrderDepth = state.order_depths[product]
            try:
                position = state.position[product]
            except:
                position = 0

            # if product == 'AMETHYSTS':
            #     orders = self.market_make_amethyst(product, order_depth, position)
            #     result[product] = orders
            #     continue

            if product == 'STARFRUIT':
                orders = self.compute_orders_starfruit(product, order_depth, position)
                result[product] = orders
                continue

            result[product] = orders

        
        print('\n----------------------------------------------------------------------------------------------------\n')
        traderData = [self.STARFRUIT_PRICES_NO_SPIKE,] # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        conversions = 0
        traderData = jsonpickle.encode(traderData)

        logger.flush(state, result, conversions, traderData)

        return result, conversions, traderData