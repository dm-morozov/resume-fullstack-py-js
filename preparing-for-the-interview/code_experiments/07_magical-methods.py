"""Примеры использования магических методов (dunder methods) в Python."""

from dataclasses import dataclass


class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __str__(self):
        return f"Пользователь с именем {self.name}"

    def __repr__(self):
        return f"User(name={self.name!r}, age={self.age!r})"


user = User("Dmitriy", 35)
print(user)
print(repr(user))

users = [User("Anna", 30), User("Marina", 31)]
print(users)  # Выведет через __repr__


class Team:
    def __init__(self, members):
        self.members = members

    def __len__(self):
        return len(self.members)


team = Team(["Aline", "Pavel", "Airat"])

print(len(team))


class Product:
    """Товар с понятным строковым представлением и поддержкой сравнения."""

    def __init__(self, name, price):
        self.name = name
        self.price = price

    def __repr__(self):
        return f"Product(name={self.name!r}, price={self.price!r})"

    def __str__(self):
        return f"{self.name}: {self.price} грн"

    def __eq__(self, other):
        if not isinstance(other, Product):
            return NotImplemented
        return self.name == other.name and self.price == other.price

    def __lt__(self, other):
        if not isinstance(other, Product):
            return NotImplemented
        return self.price < other.price


phone = Product("Телефон", 30_000)
laptop = Product("Ноутбук", 50_000)
another_phone = Product("Телефон", 30_000)

print(phone)  # Вызывает __str__.
print(repr(phone))  # Вызывает __repr__.
print(phone == another_phone)  # Вызывает __eq__: True.
print(phone < laptop)  # Вызывает __lt__: True.


class Vector:
    """Двумерный вектор с операциями сложения и умножения на число."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vector(x={self.x}, y={self.y})"

    def __add__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, number):
        if not isinstance(number, (int, float)):
            return NotImplemented
        return Vector(self.x * number, self.y * number)

    def __rmul__(self, number):
        return self * number


vector1 = Vector(2, 3)
vector2 = Vector(4, 1)

print(vector1 + vector2)  # Vector(x=6, y=4)
print(vector1 * 3)  # Vector(x=6, y=9)
print(3 * vector1)  # Вызывает __rmul__: Vector(x=6, y=9)


class Playlist:
    """Объект, который ведёт себя как контейнер."""

    def __init__(self, tracks):
        self._tracks = list(tracks)

    def __len__(self):
        return len(self._tracks)

    def __getitem__(self, index):
        return self._tracks[index]

    def __contains__(self, track):
        return track in self._tracks

    def __iter__(self):
        return iter(self._tracks)


playlist = Playlist(["Intro", "Python Song", "Finale"])

print(len(playlist))  # Вызывает __len__: 3.
print(playlist[1])  # Вызывает __getitem__: Python Song.
print("Intro" in playlist)  # Вызывает __contains__: True.

for track in playlist:  # Вызывает __iter__.
    print(track)


class Multiplier:
    """Экземпляр класса можно вызывать как обычную функцию."""

    def __init__(self, factor):
        self.factor = factor

    def __call__(self, value):
        return value * self.factor


double = Multiplier(2)
print(double(10))  # Вызывает __call__: 20.


# Магические методы вызываются встроенными операциями Python:
# str(obj)       -> obj.__str__()
# repr(obj)      -> obj.__repr__()
# len(obj)       -> obj.__len__()
# left + right   -> left.__add__(right)
# left == right  -> left.__eq__(right)
# obj[index]     -> obj.__getitem__(index)
# item in obj    -> obj.__contains__(item)
# obj()          -> obj.__call__()
#
# Обычно их не вызывают напрямую: пишут len(obj), а не obj.__len__().


# Создание dataclass


@dataclass
class Product:
    name: str
    price: float
    quantity: int = 0


product = Product("Мороженое", 155.9, 2)
product1 = Product("Мороженое", "Дорого", 2)

print(product)
print(product1)
