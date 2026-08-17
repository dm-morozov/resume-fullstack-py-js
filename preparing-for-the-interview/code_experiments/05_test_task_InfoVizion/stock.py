from pathlib import Path
import csv 
import datetime
from pprint import pp
from itertools import islice

PATH_SOURCE = Path(__file__).parent
PATH_TRANS = PATH_SOURCE / 'invent_trans'
PATH_STOCK = PATH_SOURCE / 'stock'

def load_initial_stock(file_path: Path) -> dict:
    data = {}
    with open(file_path, 'r', newline='', encoding='utf-8') as file_handle:
        reader = csv.DictReader(file_handle, delimiter=';')

        for row in islice(reader, 3):
            data[(row['item_id'], row['location_id'])] = {
                'date': datetime.datetime.strptime(row['trans_date'], '%Y-%m-%d').date(),
                'quantity': float(row['qty']),
                'price': float(row['cost_amount'])
            }
    return data


def main() -> None:
    file_path = PATH_STOCK.joinpath('stock_2025_04_30.csv')
    initial_stock = load_initial_stock(file_path)
    pp(initial_stock)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f'Oops... Something wrong: {e}')
