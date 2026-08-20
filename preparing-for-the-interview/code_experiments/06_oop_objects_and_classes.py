# Определи результат каждого print:


class User:
    role = "guest"

    def __init__(self, name):
        self.name = name


user1 = User("Дмитрий")
user2 = User("Анна")


user1.role = "admin"
User.role = "member"


print(user1.role)
print(user2.role)
print(User.role)


print(user1.__dict__)
print(user2.__dict__)

# И отдельно объясни:

# Почему изменение User.role не повлияло на user1.role?
# Откуда user2 получает значение role?
# Где физически находятся name и role у каждого объекта?


# Ответ
#
# Результат выполнения:
#
# admin
# member
# member
# {'name': 'Дмитрий', 'role': 'admin'}
# {'name': 'Анна'}
#
# 1. Почему изменение User.role не повлияло на user1.role?
#
# После присваивания user1.role = "admin" атрибут role появился непосредственно
# в пространстве имён объекта user1. При обращении к user1.role Python сначала
# ищет атрибут в самом объекте и только затем — в его классе. Поэтому значение
# "admin" объекта user1 перекрывает новое значение User.role == "member".
#
# 2. Откуда user2 получает значение role?
#
# В объекте user2 собственного атрибута role нет. Поэтому Python продолжает
# поиск в классе User и находит там User.role == "member".
#
# 3. Где находятся name и role?
#
# Атрибуты экземпляров хранятся в их словарях __dict__:
#
# user1.__dict__ == {"name": "Дмитрий", "role": "admin"}
# user2.__dict__ == {"name": "Анна"}
#
# Атрибут класса хранится в пространстве имён класса:
#
# User.__dict__["role"] == "member"
#
# Таким образом:
# - name у каждого пользователя находится в __dict__ соответствующего объекта;
# - собственный role есть только у user1;
# - user2 получает role из User, потому что в user2.__dict__ такого ключа нет.


class User:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Привет, {self.name}!"


user = User("Дмитрий")
print(user.greet())
print(User.greet(user))


class User:
    role = "User"

    @classmethod
    def show_role(cls):
        return cls.role


print(User.show_role())
user1 = User()
print(user1.show_role())


class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    @classmethod
    def from_string(cls, raw_data):
        name, age = raw_data.split(",")
        return cls(name, int(age))


user1 = User("Дмитрий", 35)
user2 = User.from_string("Dmitriy,35")
print(user1.name, user1.age)
print(user2.name, user2.age)


class Admin(User):
    pass


admin = Admin.from_string("Иван,40")
print(admin.name, admin.age)

# Статический метод — @staticmethod


class User:
    @staticmethod
    def is_valid_age(age):
        return 0 <= age <= 120


print(User.is_valid_age(35))


class User:
    def __init__(self, name, age):
        if not self.is_valid_age(age):
            raise ValueError("Некорректный возраст")

        self.name = name
        self.age = age

    @staticmethod
    def is_valid_age(age):
        return 0 <= age <= 120


user = User("Dmitriy", 35)


# Что выведет этот код?


class Product:
    category = "general"

    def __init__(self, name):

        self.name = name

    def show(self):
        return self.name, self.category

    @classmethod
    def change_category(cls, new_category):
        cls.category = new_category

    @staticmethod
    def normalize_name(name):
        return name.strip().title()


product1 = Product("Телефон")
product2 = Product("Ноутбук")


product1.category = "personal"
Product.change_category("electronics")


print(product1.show())  # "Телефон", "personal"
print(product2.show())  # "Ноутбук", "electronics"
print(Product.category)  # "electronics"
print(Product.normalize_name("  умные ЧАСЫ  "))  # Умные Часы

# Ответь:

# Что выведут четыре print?
# Почему product1.category не изменился после change_category()?
# Какой объект передаётся в self внутри product2.show()?
# Что передаётся в cls внутри Product.change_category()?


# Как работает property


class Product:
    def __init__(self, price):
        self.price = price

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if not isinstance(value, (float, int)):
            raise TypeError("Цена должна быть числом")

        if value < 0:
            raise ValueError("Цена не может быть отрицательным числом")

        self._price = value


product = Product(50_000)
print(product.price)

product.price = 40000
print(product.price)


class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    @property
    def celsius(self):
        print("Работает getter")
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        print("Работает setter")

        if value < -273.15:
            raise ValueError("Температура ниже абсолютного нуля")

        self._celsius = value


temperature = Temperature(20)

print(temperature.__dict__)
print(temperature.celsius)

temperature.celsius = 30

print(temperature.__dict__)
print(temperature.celsius)
