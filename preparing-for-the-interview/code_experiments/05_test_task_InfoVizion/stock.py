from pathlib import Path
import csv 
import logging
from datetime import date, timedelta

# Настраиваем логирование: выводим время, уровень лога (INFO/WARNING/ERROR) и сообщение
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


PATH_SOURCE = Path(__file__).parent
PATH_TRANS = PATH_SOURCE / 'invent_trans'
PATH_STOCK = PATH_SOURCE / 'stock'

def load_initial_stock(file_path: Path) -> dict[tuple[str, str], list[float]]:
    """
    Загружает начальные остатки товаров.
    Возвращает словарь с ключом (item_id, location_id) и значением [qty, cost_amount].
    """

    if not file_path.exists():
        logging.error(f"Файл начальных остатков не найден: {file_path}")
        raise FileNotFoundError(f"Не найден файл: {file_path}")

    logging.info(f"Загрузка начальных остатков из файла: {file_path.name}")

    data = {}
    with open(file_path, 'r', newline='', encoding='utf-8') as file_handle:
        reader = csv.reader(file_handle, delimiter=';')

        next(reader)  # Пропускаем заголовок
        
        # Не использовал DictReader для экономии памяти и скорости
        # так же убрал data из dict для экономии памяти, она не нужна в расчетах в рамках одного дня

        for row in reader:
            if not row:  # Пропускаем пустые строки
                continue

            try:
                item_id = row[0]
                location_id = row[1]
                qty = float(row[3])
                cost_amount = float(row[4])

                if qty < 0:
                    logging.warning(
                        f"Обнаружено отрицательное количество товара: {qty}"
                    )
                
                data[(item_id, location_id)] = [qty, cost_amount]
                
            except (ValueError, IndexError) as e:
                logging.warning(
                    f"Пропущена некорректная строка в файле остатков {file_path.name}: {row}. Ошибка: {e}"
                )
                continue
                
    logging.info(f"Загружено товаров: {len(data)}")

    return data


def load_transactions_by_date(file_path: Path) -> dict[str, dict[tuple[str,str], list[float]]]:
    """
    {
        "2025-05-01": {
            ("Товар_А", "Склад_Б"): [суммарное_кол-во, суммарная_стоимость]
        },
        "2025-05-02": { ... }
    } 
    """
    
    if not file_path.exists():
        logging.error(f"Файл транзакций не найден: {file_path}")
        raise FileNotFoundError(f"Не найден файл: {file_path}")

    logging.info(f"Загрузка транзакций из файла: {file_path.name}")

    daily_transactions = {}
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader)

        for row in reader:
            if not row:
                continue

            try:
                item_id = row[0]
                location_id = row[1]
                trans_date = row[2]
                qty = float(row[3])
                cost_amount = float(row[4])

                if trans_date not in daily_transactions:
                    daily_transactions[trans_date] = {}
                
                if (item_id, location_id) not in daily_transactions[trans_date]:
                    daily_transactions[trans_date][(item_id, location_id)] = [0.0, 0.0]

                daily_transactions[trans_date][(item_id, location_id)][0] += qty
                daily_transactions[trans_date][(item_id, location_id)][1] += cost_amount

            except (ValueError, IndexError) as e:
                logging.warning(
                    f"Пропущена некорректная строка в файле транзакций {file_path.name}: {row}. Ошибка: {e}"
                )
                continue
    
    logging.info(f"Загружено транзакций: {len(daily_transactions)}")

    return daily_transactions


def write_stock(file_path: Path, stock_db: dict[tuple[str, str], list[float]], date_str: str) -> None:

    logging.info(f"Сохранение остатков товаров началось.")
    
    with open(file_path, 'w', newline='', encoding='utf-8') as file_handle:

        # (item_id, location_id, trans_date) взяты в двойные кавычки, а числа (qty, cost_amount) записаны без кавычек
        # Используется csv.QUOTE_NONNUMERIC, чтобы числа выводились без кавычек.
        writer = csv.writer(file_handle, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)

        writer.writerow(["item_id", "location_id", "trans_date", "qty", "cost_amount"])

        #     "2025-05-01": {
        #         ("Товар_А", "Склад_Б"): [суммарное_кол-во, суммарная_стоимость]
        #     },
        #    ...
        for (item_id, location_id), (qty, cost_amount) in sorted(stock_db.items()):
            # Фильтрация нулей (с учетом погрешности), оставить отрицательные
            if abs(qty) < 1e-7:
                continue

            qty_val = int(qty) if qty.is_integer() else round(qty, 4)
            cost_val = int(cost_amount) if cost_amount.is_integer() else round(cost_amount, 2)

            writer.writerow([
                item_id,
                location_id,
                date_str,
                qty_val,
                cost_val
            ])
    
    logging.info(f"Записан файл {file_path.name}")

def apply_daily_transactions(stock: dict[tuple[str, str], list[float]], daily_transactions: dict[tuple[str, str], list[float]]) -> None:
    for key, (qty, cost_amount) in daily_transactions.items():

        # В key лежит кортеж (item_id, location_id)
        # Делаем проверку: а лежал ли данный товар на складе
        if key not in stock:
            stock[key] = [0.0, 0.0]

        stock[key][0] += qty
        stock[key][1] += cost_amount
    

def main() -> None:
    # Начальная дата
    current_date = date(2025,5,1)

    end_date = date(2025, 7, 31)

    # Какой месяц сейчас загружен
    current_month_str = ""

    # Транзакции текущего месяца
    transactions = {}

    # Загружаем стартовые остатки на 30.04.2025
    file_path = PATH_STOCK.joinpath('stock_2025_04_30.csv')
    stock = load_initial_stock(file_path)

    # Проходимся по каждому дню
    while current_date <= end_date:
        year_month = current_date.strftime('%Y_%m')

        # Месяц сменился или это первая итерация - загружаем файл
        if year_month != current_month_str:
            file_name = f'invent_trans_{year_month}.csv'
            path_to_transactions = PATH_TRANS.joinpath(file_name)

            # Загружаем транзакции месяца
            transactions = load_transactions_by_date(path_to_transactions)

            current_month_str = year_month

        
        date_str = current_date.strftime('%Y-%m-%d')

        # Вытягиваем транзакции за сегодня, если их нет то пустой словарь
        daily_transactions = transactions.get(date_str, {})

        # Применяем транзакции к остаткам
        apply_daily_transactions(stock, daily_transactions)

        # Записываем остатки за текущий день
        file_date_str = current_date.strftime('%Y_%m_%d')
        path_to_stock = PATH_STOCK.joinpath(f'stock_{file_date_str}.csv')
        write_stock(path_to_stock, stock, date_str)

        # Увеличиваем день
        current_date += timedelta(days=1)
    
    logging.info(f"Загрузка и обработка данных завершены успешно")    
        
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f'Oops... Something wrong: {e}')
