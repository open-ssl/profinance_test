import sys

from datetime import date, datetime
from traceback import print_exception


def get_current_data_and_time():
    """
    Получение текущих дату и время в формате, удобном для логирования
    """
    data_for_file = date.today().strftime("%m-%d-%Y")
    time_for_file = datetime.now().strftime("%H:%M:%S")
    return data_for_file, time_for_file


def log_error_in_file():
    """
    Логирование ошибок в локальный файл в директории проекта
    """
    data_for_file, time_for_file = get_current_data_and_time()
    error_file = f'logs/error_log_{data_for_file}.txt'

    try:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        with open(error_file, 'a') as file:
            print('_______________________________________', file=file)
            print(f'Current time {time_for_file}', file=file)
            print_exception(exc_type, exc_value, exc_traceback, file=file)
            print('_______________________________________', file=file)
    except Exception as e:
        print(e)
