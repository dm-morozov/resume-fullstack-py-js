from pathlib import Path

PATH_SOURCE = Path(__file__).parent
PATH_TRANS = PATH_SOURCE / 'invent_trans'
PATH_STOCK = PATH_SOURCE / 'stock'

def load_initial_stock(file_path: Path) -> dict:
    pass


def main() -> None:
    pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print('Oops... Something wrong!')
