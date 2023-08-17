import pytest
import utils.helpers as hp

from config.binance_exchange import BinanceConfig
from unittest.mock import MagicMock
from utils.helpers import Symbol
from generic_test_data import (
    BTC_TEST_DATA, ETH_TEST_DATA,
    ETALON_BTC_COUNT_OPERATIONS, ETALON_ETH_COUNT_OPERATIONS,
    ETALON_BTC_AVG_PRICE, ETALON_ETH_AVG_PRICE,
    ETALON_BTC_QUANTITY, ETALON_ETH_QUANTITY
)


@pytest.fixture()
def enter_BTC_symbol():
    return [Symbol.BTC_USDT]


@pytest.fixture()
def enter_ETH_symbol():
    return [Symbol.BTC_USDT, Symbol.ETH_USDT]


def mock_binance_client(func):
    def inner_func(*args, **kwargs):
        hp.get_binance_client = MagicMock(return_value=None)
        hp.get_trades_info_for_symbol = MagicMock(return_value=BTC_TEST_DATA)
        return func(*args, **kwargs)

    return inner_func


def test_symbol_in_result_for_BTC(enter_BTC_symbol):
    """
    Тестируем, что входные тикеры находятся в результаты get_trades_info
    """
    hp.get_binance_client = MagicMock(return_value=None)
    hp.get_trades_info_for_symbol = MagicMock(return_value=BTC_TEST_DATA)
    trades_info = hp.get_trades_info(enter_BTC_symbol)
    assert list(trades_info.keys()) == enter_BTC_symbol


def test_correct_operations_for_BTC_symbols_in_result(enter_BTC_symbol):
    """
    Тестируем, что посчитанное количество операций для BTC тикера калькулируются правильно
    """
    hp.get_binance_client = MagicMock(return_value=None)
    hp.get_trades_info_for_symbol = MagicMock(return_value=BTC_TEST_DATA)
    trades_info = hp.get_trades_info(enter_BTC_symbol)
    history_for_BTC = hp.get_history_by_symbol_info(trades_info)
    assert history_for_BTC[Symbol.BTC_USDT].get(hp.Const.OPERATIONS_AMOUNT) == ETALON_BTC_COUNT_OPERATIONS


def test_correct_operations_for_ETH_symbols_in_result(enter_ETH_symbol):
    """
    Тестируем, что посчитанное количество операций для BTC тикера калькулируются правильно
    """
    hp.get_binance_client = MagicMock(return_value=None)
    hp.get_trades_info_for_symbol = MagicMock(return_value=ETH_TEST_DATA)
    trades_info = hp.get_trades_info(enter_ETH_symbol)
    history_for_ETH = hp.get_history_by_symbol_info(trades_info)
    assert history_for_ETH[Symbol.ETH_USDT].get(hp.Const.OPERATIONS_AMOUNT) == ETALON_ETH_COUNT_OPERATIONS


def test_correct_value_for_BTC_symbols_in_result(enter_BTC_symbol):
    """
    Тестируем, что посчитанное среднее значение для BTC тикера калькулируется правильно
    """
    hp.get_binance_client = MagicMock(return_value=None)
    hp.get_trades_info_for_symbol = MagicMock(return_value=BTC_TEST_DATA)
    trades_info = hp.get_trades_info(enter_BTC_symbol)
    history_for_BTC = hp.get_history_by_symbol_info(trades_info)
    assert history_for_BTC[Symbol.BTC_USDT].get(hp.Const.AVG_SYMBOL_PRICE) == BinanceConfig.safe_round_value(ETALON_BTC_AVG_PRICE)


def test_correct_value_for_ETH_symbols_in_result(enter_ETH_symbol):
    """
    Тестируем, что посчитанное среднее значение для ETH тикера калькулируется правильно
    """
    hp.get_binance_client = MagicMock(return_value=None)
    hp.get_trades_info_for_symbol = MagicMock(return_value=ETH_TEST_DATA)
    trades_info = hp.get_trades_info(enter_ETH_symbol)
    history_for_ETH = hp.get_history_by_symbol_info(trades_info)
    assert history_for_ETH[Symbol.ETH_USDT].get(hp.Const.AVG_SYMBOL_PRICE) == BinanceConfig.safe_round_value(ETALON_ETH_AVG_PRICE)


def test_correct_quantity_for_BTC_symbols_in_result(enter_BTC_symbol):
    """
    Тестируем, что посчитанное итоговое количество для BTC тикера калькулируется правильно
    """
    hp.get_binance_client = MagicMock(return_value=None)
    hp.get_trades_info_for_symbol = MagicMock(return_value=BTC_TEST_DATA)
    trades_info = hp.get_trades_info(enter_BTC_symbol)
    history_for_BTC = hp.get_history_by_symbol_info(trades_info)
    assert history_for_BTC[Symbol.BTC_USDT].get(hp.Const.AVG_SYMBOL_QUANTITY) == BinanceConfig.safe_round_value(ETALON_BTC_QUANTITY)


def test_correct_quantity_for_ETH_symbols_in_result(enter_ETH_symbol):
    """
    Тестируем, что посчитанное итоговое количество для ETH тикера калькулируется правильно
    """
    hp.get_binance_client = MagicMock(return_value=None)
    hp.get_trades_info_for_symbol = MagicMock(return_value=ETH_TEST_DATA)
    trades_info = hp.get_trades_info(enter_ETH_symbol)
    history_for_ETH = hp.get_history_by_symbol_info(trades_info)
    assert history_for_ETH[Symbol.ETH_USDT].get(hp.Const.AVG_SYMBOL_QUANTITY) == BinanceConfig.safe_round_value(ETALON_ETH_QUANTITY)
