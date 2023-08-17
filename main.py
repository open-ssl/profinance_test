from typing import List, AnyStr

from utils.helpers import (
    UserMessages, Symbol, Const, get_trades_info, get_history_by_symbol_info
)


def main_logic(trade_symbols: List[AnyStr]):
    """
    Запуск логики приложения
    Если с активом не было операций конвертации, то операции покупки и продажи отражают реальную историю изменения актива
    Ситуация подсчета истории актива с учетом конвертации, лежит за рамками реализуемой мной задачи
    :param: trades_symbols list[str] объект тикеров для выгрузки информации
    """

    trades_info: dict = get_trades_info(trade_symbols)

    history_by_symbol_info: dict = get_history_by_symbol_info(trades_info)

    if not history_by_symbol_info:
        print(UserMessages.HAVE_NO_INFO)
        return

    result_msg = UserMessages.HEADER
    for symbol_name, symbol_info in history_by_symbol_info.items():
        result_msg += UserMessages.SYMBOL_ROW_INFO.format(
            symbol_name,
            symbol_info.get(Const.OPERATIONS_AMOUNT),
            symbol_info.get(Const.AVG_SYMBOL_PRICE),
            symbol_info.get(Const.AVG_SYMBOL_QUANTITY),
        )

    # можно также напечатать в файл или online-spreadsheet
    print(result_msg)

    return history_by_symbol_info


if __name__ == '__main__':
    print("Start application")
    """
    Binance API doesn't support getting ALL historical data without symbol name.

    There are two ways to get all info about trading history
    
    1. Get info about account, pick all symbols from there and looking for all operations for that tickers. 
    The amount of the asset may be negligible, no reason to count average price for them.   
    
    2. Get info by particular symbol name.
    
    I picked second one, so, if you want to get more info about another tickers you should expand that object
    """

    trades_symbols = [Symbol.BTC_USDT, Symbol.ETH_USDT]
    main_logic(trades_symbols)
