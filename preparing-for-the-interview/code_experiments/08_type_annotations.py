"""Примеры использования аннотаций типов."""


def calculate_total(price: float, quantity: int) -> float:
    """Вычисляет общую стоимость."""
    return price * quantity


def find_product(
    product_id: int,
    products: dict[int, str],
) -> str | None:
    return products.get(product_id)


products: dict[int, str] = {
    1: "Телефон",
    2: "Ноутбук",
}

product = find_product(3, products)
print(product)

# Какого типа должен быть product_id? - int
# Что означает dict[int, str]? - key int, value str
# Почему функция возвращает str | None? - потому что get это метод безопасного вывода value по key, если ключ не найдет тогда None, но ошибки не будет. Можно переопределить, если написать .get(str, 'Такого элемента нет')
# Какое значение будет в переменной product? -
# Запретит ли сам Python вызвать find_product("1", products)?
