from decimal import Decimal
from binance.client import Client

from config.base import BINANCE_API_KEY, BINANCE_API_SECRET_KEY


class BinanceConfig:
    MAX_TRADES_REQUEST_LIMIT = 1000
    API_LIMIT_STATUS_CODE = 429
    SKIP_API_LIMIT_SLEEP_TIME = 1
    VALUE_PRECISION_MIN = 2
    VALUE_PRECISION_MAX = 8

    @classmethod
    def safe_round_value(cls, value: float):
        """
        Безопасное округление позиции в зависимости от значения
        :param value: float - значение
        :return: value: Decimal
        """
        return round(value, cls.VALUE_PRECISION_MIN) if value > 1 else round(value, cls.VALUE_PRECISION_MAX)

    @staticmethod
    def get_count_operation(func):
        """
        Декоратор безопасного подсчета значений для операций Binance с округлением
        :param func: - математическая операция подсчета
        :return: дескриптор вызова функции математической операции
        """

        def inner_func(arg1, arg2):
            arg1 = Decimal(arg1)
            arg2 = Decimal(arg2)
            func_result = func(arg1, arg2)
            return BinanceConfig.safe_round_value(func_result)

        return inner_func


def get_binance_client(need_real_client=True):
    """
    Получение клиента бинанса
    :param need_real_client (bool) - нужен ли запуск на реальном токене
    :return: (binance.Client) - объект для работы с биржей Binance
    """
    if not need_real_client:
        # api_key и api_secret можно не передавать в качестве аргументов
        return Client()

    return Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET_KEY)
