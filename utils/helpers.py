from binance.client import Client
from binance.exceptions import BinanceRequestException, BinanceAPIException

from decimal import Decimal
from functools import partial
from time import sleep
from typing import List, AnyStr
from operator import add, sub, mul, truediv

from config.binance_exchange import (
    BinanceConfig,
    get_binance_client,
)
from utils.log_helpers import log_error_in_file


class UserMessages:
    HAVE_NO_INFO = "Have no info for Your account or Given pairs"
    HEADER = f"Your Binance account symbol info:"
    SYMBOL_ROW_INFO = "\n\n| Symbol: {} |\n\n| Operations amount: {} |\n| Total average symbol price: {} |\n| Total " \
                      "symbol amount: {} | "


class Symbol:
    BTC_USDT = 'BTCUSDT'
    ETH_USDT = 'ETHUSDT'


class Const:
    QTY = 'qty'
    TIME = 'time'
    PRICE = 'price'
    IS_BUYER = 'isBuyer'
    COMMISSION = 'commission'
    OPERATIONS_AMOUNT = "operations_count"
    AVG_SYMBOL_PRICE = "avg_symbol_price"
    AVG_SYMBOL_QUANTITY = "avg_symbol_quantity"


def get_trades_info(trade_symbols: List[AnyStr]):
    """
    Получение информации о всех сделках пользователя на Binance для определенного тикера
    1. Выгружаем все сделки пользователя по выбранному тикеру пока они есть
    Максимальный лимит выгрузки сделок, предоставляемый API - 1000
    1.1 Если количество выгруженных сделок = количеству лимита (могут быть более ранние сделки), то:
        Выгружаем пока не выгрузим все сделки по алгоритму
            - запоминаем таймстемп самой ранней сделки,
            - удаляем эту сделку из предыдущего массива, (т.к. она будет первой в новом выгружаемом объекте)
            - массив кладем в мапу постранично, где 0 страница последние сделки,
            - каждая следующая самые старые сделки - гарантируем консистентность данных

    Сделки расположены в порядке возрастания идентификаторов сделок (в выгрузке по возрастанию идентификаторов)

    :param trade_symbols: list[str] - массив пар для выгрузки информации
    :return: dict - имя пары + постраничная история операций завершенных сделок
    """
    binance_client = get_binance_client()
    trades_info = dict()
    for symbol in trade_symbols:
        need_load_extra_data, page_index, end_time = True, 0, None
        trades_info[symbol] = dict()
        try:
            while need_load_extra_data:
                # 1
                symbol_info = get_trades_info_for_symbol(binance_client, symbol, end_time)
                need_load_extra_data = len(symbol_info) == BinanceConfig.MAX_TRADES_REQUEST_LIMIT
                trades_info_for_symbol = trades_info.get(symbol)

                if need_load_extra_data:
                    # 1.1
                    first_trade_operation_in_resp = symbol_info[0]
                    end_time = first_trade_operation_in_resp.get(Const.TIME)
                    symbol_info = symbol_info[1:]

                trades_info_for_symbol[page_index] = symbol_info
                trades_info[symbol] = trades_info_for_symbol
                page_index += 1
        except BaseException as _:
            log_error_in_file()

    return trades_info


def get_trades_info_for_symbol(client: Client, symbol: str, end_time=None):
    """
    Получение торговой информации по паре с Binance
    :param client: (binance.Client) - API-клиент Binance
    :param symbol: (str) - пара для выгрузки данных
    :param end_time: (int / default: None) - timestamp для выгрузки старых данных сверх лимита запроса
    :return: (list[dict]) - массив торговых операций для пары
    """
    symbol_info = list()
    while True:
        """
        Binance API имеет ограничение в 1200 веса в минуту.
        Если его превысить вернется 429 ошибка. Возможно нарушение консистентности данных.
        Для избежания этого, обеспечим окно, между ближайшими запросами в 1 секунду для сброса API-таймаута
        """
        try:
            # limit is 500 as default. Max - 1000
            # use that API method, cause it shows real open/closed deals without intentions
            get_trades = partial(client.get_my_trades, symbol=symbol, limit=BinanceConfig.MAX_TRADES_REQUEST_LIMIT)
            symbol_info = get_trades(endTime=end_time) if end_time else get_trades()
        except BinanceRequestException as e:
            print(f"Got BinanceRequestException with "
                  f"Message: {e.message} \nduring request to Binance\n"
                  f"Possible resolving: Check internet connection")
            log_error_in_file()
        except BinanceAPIException as e:
            print(f"Got BinanceAPIException with "
                  f"Status code: {e.status_code}\n"
                  f"Message: {e.message} \nduring request to Binance\n"
                  f"Possible resolving: Check API authorization data")
            log_error_in_file()

            if e.status_code == BinanceConfig.API_LIMIT_STATUS_CODE:
                print(f"Sleep {BinanceConfig.SKIP_API_LIMIT_SLEEP_TIME} after reached BinanceAPIException"
                      f"for skipping API limit")
                sleep(BinanceConfig.SKIP_API_LIMIT_SLEEP_TIME)
                continue
        except Exception as _:
            log_error_in_file()
        break

    return symbol_info


def get_history_by_symbol_info(trades_info: dict):
    """
    Возвращает обьект торговой истории для данных исторических данных по тикерам
    :param trades_info - объект исторических данных по тикерам
    :return: dict - информация о торговой истории по тикерам
    """
    result_info = dict()

    for symbol, symbol_data in trades_info.items():
        result_info[symbol] = dict()
        operations_amount, avg_symbol_price, avg_symbol_quantity = 0, None, None

        # можно и не сортировать, но лишний раз гарантируем консистентность данных
        symbol_pages = list(sorted(symbol_data.keys()))[::-1]

        # Имеем страницы 0, 1, 2 (на меньшей странице более новые данные)
        while symbol_pages:
            page_num = symbol_pages.pop()
            page_symbol_data = symbol_data.get(page_num)
            operations_amount += len(page_symbol_data)

            for trade_operation in page_symbol_data:
                count_operation = BinanceConfig.get_count_operation(sub)
                operation_price = Decimal(trade_operation.get(Const.PRICE, 0))
                operation_qty = Decimal(trade_operation.get(Const.QTY, 0))
                operation_fee_qty = Decimal(trade_operation.get(Const.COMMISSION, 0))

                # True = buy, False = sell
                is_buy_operation: bool = trade_operation.get(Const.IS_BUYER)
                mul_count_operation = BinanceConfig.get_count_operation(mul)

                # комиссия для покупки считается по активу покупки, для продажи по активу продажи
                if is_buy_operation:
                    if not avg_symbol_price:
                        avg_symbol_price = operation_price
                        avg_symbol_quantity = sub(operation_qty, operation_fee_qty)
                        continue

                    count_operation = BinanceConfig.get_count_operation(add)

                    """
                    Комиссия списывается с текущего количества актива на балансе перед покупкой,
                    однако если баланс меньше чем необходимая сумма к списанию
                    комиссия списывается c количества актива в операции
                    """
                    if avg_symbol_quantity > operation_fee_qty:
                        avg_symbol_quantity = sub(avg_symbol_quantity, operation_fee_qty)
                    else:
                        operation_qty = sub(operation_qty, operation_fee_qty)

                    total_avg_symbol_amount = mul_count_operation(avg_symbol_price, avg_symbol_quantity)
                    total_operation_amount = mul_count_operation(operation_price, operation_qty)

                    total_sum = count_operation(total_avg_symbol_amount, total_operation_amount)
                    total_qty = count_operation(avg_symbol_quantity, operation_qty)

                    avg_symbol_price = truediv(total_sum, total_qty)

                avg_symbol_quantity = count_operation(avg_symbol_quantity, operation_qty)

        result_info[symbol] = {
            Const.OPERATIONS_AMOUNT: operations_amount,
            Const.AVG_SYMBOL_PRICE: BinanceConfig.safe_round_value(avg_symbol_price),
            Const.AVG_SYMBOL_QUANTITY: avg_symbol_quantity
        }

    return result_info
