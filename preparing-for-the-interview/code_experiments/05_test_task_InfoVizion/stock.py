"""Расчёт подневных товарных остатков на основании CSV-файлов движений."""

import csv
import logging
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

# Настраиваем логирование: выводим время, уровень лога (INFO/WARNING/ERROR) и сообщение
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


PATH_SOURCE = Path(__file__).parent
PATH_TRANS = PATH_SOURCE / "invent_trans"
PATH_STOCK = PATH_SOURCE / "stock"
EXPECTED_HEADER = [
    "item_id",
    "location_id",
    "trans_date",
    "qty",
    "cost_amount",
]


def load_initial_stock(file_path: Path) -> dict[tuple[str, str], list[Decimal]]:
    """Загрузить начальные товарные остатки из CSV-файла.

    Args:
        file_path: Путь к файлу начальных остатков.

    Returns:
        Словарь, в котором ключом является пара идентификаторов
        товара и подразделения, а значением — список из количества
        и себестоимости.

    Raises:
        FileNotFoundError: Если файл начальных остатков не найден.
        ValueError: Если заголовок или одна из строк файла некорректны.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Файл начальных остатков не найден: {file_path}")

    logger.info("Загрузка начальных остатков из файла: %s", file_path.name)

    data = {}
    with open(file_path, "r", newline="", encoding="utf-8") as file_handle:
        reader = csv.reader(file_handle, delimiter=";")

        header = next(reader, None)  # Пропускаем заголовок

        if header != EXPECTED_HEADER:
            raise ValueError(f"Некорректный заголовок файла {file_path.name}: {header}")

        # Порядок колонок задан условием, поэтому используем csv.reader
        # вместо DictReader и обращаемся к значениям строки по индексам.
        for row_number, row in enumerate(reader, start=2):
            if not row:  # Пропускаем пустые строки
                continue

            try:
                item_id = row[0]
                location_id = row[1]
                qty = Decimal(row[3])
                cost_amount = Decimal(row[4])

                # Проверка на конечность значений, например NaN или бесконечность
                if not qty.is_finite() or not cost_amount.is_finite():
                    raise ValueError(
                        f"Неконечное значение в строке {row_number}: "
                        f"qty={qty}, cost_amount={cost_amount}"
                    )

                data[(item_id, location_id)] = [qty, cost_amount]

            # Некорректное число вызывает InvalidOperation,
            # отсутствие обязательной колонки вызывает IndexError.
            except (InvalidOperation, IndexError) as error:
                raise ValueError(
                    f"Некорректная строка {row_number} в файле {file_path.name}: {row}"
                ) from error

    logger.info("Загружено товаров: %d", len(data))

    return data


def load_transactions_by_date(
    file_path: Path,
) -> dict[str, dict[tuple[str, str], list[Decimal]]]:
    """Загрузить и агрегировать товарные движения по датам.

    Операции с одинаковыми идентификаторами товара, подразделения
    и датой суммируются.

    Args:
        file_path: Путь к помесячному файлу товарных движений.

    Returns:
        Словарь операций по датам. Для каждой даты хранится словарь,
        ключом которого является пара item_id и location_id,
        а значением — суммарные количество и себестоимость.

    Raises:
        FileNotFoundError: Если файл движений не найден.
        ValueError: Если заголовок или одна из строк файла некорректны.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Файл транзакций не найден: {file_path}")

    logger.info("Загрузка транзакций из файла: %s", file_path.name)

    daily_transactions = {}
    with open(file_path, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")

        header = next(reader, None)
        if header != EXPECTED_HEADER:
            raise ValueError(f"Некорректный заголовок файла {file_path.name}: {header}")

        for row_number, row in enumerate(reader, start=2):
            if not row:
                continue

            try:
                item_id = row[0]
                location_id = row[1]
                trans_date = row[2]
                qty = Decimal(row[3])
                cost_amount = Decimal(row[4])

                # Проверка на конечность значений, например NaN или бесконечность
                if not qty.is_finite() or not cost_amount.is_finite():
                    raise ValueError(
                        f"Неконечное значение в строке {row_number}: "
                        f"qty={qty}, cost_amount={cost_amount}"
                    )

                if trans_date not in daily_transactions:
                    daily_transactions[trans_date] = {}

                if (item_id, location_id) not in daily_transactions[trans_date]:
                    daily_transactions[trans_date][(item_id, location_id)] = [
                        Decimal(0),
                        Decimal(0),
                    ]

                daily_transactions[trans_date][(item_id, location_id)][0] += qty
                daily_transactions[trans_date][(item_id, location_id)][1] += cost_amount

            except (InvalidOperation, IndexError) as error:
                raise ValueError(
                    f"Некорректная строка {row_number} в файле {file_path.name}: {row}"
                ) from error

    logger.info(
        "Транзакции сгруппированы по дням, всего дней: %d",
        len(daily_transactions),
    )

    return daily_transactions


def write_stock(
    file_path: Path, stock_db: dict[tuple[str, str], list[Decimal]], date_str: str
) -> None:
    """Записать остатки на конец дня в CSV-файл.

    Позиции сортируются по идентификаторам товара и подразделения.
    Строковые поля записываются в кавычках, числовые — без кавычек.

    Args:
        file_path: Путь к создаваемому CSV-файлу.
        stock_db: Остатки по товарам и подразделениям.
        date_str: Дата остатков в формате YYYY-MM-DD.
    """
    with open(file_path, "w", newline="", encoding="utf-8") as file_handle:
        # (item_id, location_id, trans_date) взяты в двойные кавычки,
        # а числа (qty, cost_amount) записаны без кавычек
        # Используется csv.QUOTE_NONNUMERIC, чтобы числа выводились без кавычек.
        writer = csv.writer(file_handle, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)

        writer.writerow(["item_id", "location_id", "trans_date", "qty", "cost_amount"])

        for (item_id, location_id), (qty, cost_amount) in sorted(stock_db.items()):
            # Целые Decimal приводим к int для компактности,
            # а дробные оставляем как точный Decimal
            qty_val = int(qty) if qty % 1 == 0 else qty
            cost_val = int(cost_amount) if cost_amount % 1 == 0 else cost_amount

            writer.writerow([item_id, location_id, date_str, qty_val, cost_val])

    logger.info(
        "Записан файл %s: %d позиций",
        file_path.name,
        len(stock_db),
    )


def apply_daily_transactions(
    stock: dict[tuple[str, str], list[Decimal]],
    daily_transactions: dict[tuple[str, str], list[Decimal]],
) -> None:
    """Применить операции дня к текущим товарным остаткам.

    Функция изменяет переданный словарь stock на месте. Для новой пары
    товара и подразделения начальный остаток принимается равным нулю.

    Args:
        stock: Изменяемый словарь текущих остатков.
        daily_transactions: Агрегированные операции за один день.
    """
    for key, (qty, cost_amount) in daily_transactions.items():
        # В key лежит кортеж (item_id, location_id)
        # Если позиции ещё нет в остатках, создаём её с нулевыми значениями.
        if key not in stock:
            stock[key] = [Decimal(0), Decimal(0)]

        stock[key][0] += qty
        stock[key][1] += cost_amount


def main() -> None:
    """Рассчитать и записать подневные остатки за заданный период."""
    # Начальная дата
    current_date = date(2025, 5, 1)

    end_date = date(2025, 7, 31)

    # Какой месяц сейчас загружен
    current_month_str = ""

    # Транзакции текущего месяца
    transactions = {}

    # Загружаем стартовые остатки на 30.04.2025
    file_path = PATH_STOCK.joinpath("stock_2025_04_30.csv")
    stock = load_initial_stock(file_path)

    # Проходимся по каждому дню
    while current_date <= end_date:
        year_month = current_date.strftime("%Y_%m")

        # Месяц сменился или это первая итерация - загружаем файл
        if year_month != current_month_str:
            file_name = f"invent_trans_{year_month}.csv"
            path_to_transactions = PATH_TRANS.joinpath(file_name)

            # Загружаем транзакции месяца
            transactions = load_transactions_by_date(path_to_transactions)

            current_month_str = year_month

        date_str = current_date.strftime("%Y-%m-%d")

        # Вытягиваем транзакции за сегодня, если их нет то пустой словарь
        daily_transactions = transactions.get(date_str, {})

        # Применяем транзакции к остаткам
        apply_daily_transactions(stock, daily_transactions)

        # Записываем остатки за текущий день
        file_date_str = current_date.strftime("%Y_%m_%d")
        path_to_stock = PATH_STOCK.joinpath(f"stock_{file_date_str}.csv")
        write_stock(path_to_stock, stock, date_str)

        # Увеличиваем день
        current_date += timedelta(days=1)

    logger.info("Загрузка и обработка данных завершены успешно")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Ошибка при обработке данных")
        raise
