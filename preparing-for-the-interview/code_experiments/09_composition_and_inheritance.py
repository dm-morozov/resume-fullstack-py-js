# Наследование — «является»


class Animal:
    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> str:
        return "Не издает звук"


class Dog(Animal):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    def speak(self) -> str:
        return "Гав-гав"

    def __str__(self) -> str:
        return f"{self.name} - это собака и она издает звук {self.speak()}"


dog = Dog("Масик")
print(dog)

# Композиция — «содержит» или «использует»


class Engine:
    def start(self) -> str:
        return "The engine as runnig"


class Car:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def start(self) -> str:
        return self.engine.start()


engine_for_car = Engine()
car = Car(engine_for_car)

print(car.start())
print(car.__dict__["engine"].start())

# Пример из реального приложения


class EmailService:
    def send(self, message: str) -> None:
        print(f"Email: {message}")


class User:
    def __init__(self, name: str, notification_service: EmailService) -> None:
        self.name = name
        self.notification_service = notification_service

    def notify(self, message: str) -> None:
        self.notification_service.send(message)


email_service = EmailService()
user = User("Dmitriy", email_service)

user.notify("Hello World")


class PaymentService:
    def pay(self, amount: float) -> str:
        return f"Оплачено: {amount} ₽"


class Order:
    def __init__(
        self,
        number: int,
        payment_service: PaymentService,
    ) -> None:
        self.number = number
        self.payment_service = payment_service
        self.is_paid = False

    def pay(self, amount: float) -> str:
        result = self.payment_service.pay(amount)
        self.is_paid = True
        return result


payment_service = PaymentService()
order = Order(101, payment_service)

print(order.pay(5_000))
print(order.is_paid)
print(order.__dict__)

# Ответь как на собеседовании:
#
# 1. Какое отношение между Order и PaymentService: наследование или композиция?
# Ответ: Композиция (в строгом смысле — агрегация, так как зависимость передается извне). Order «содержит» или «использует» PaymentService.
#
# 2. Где хранится объект PaymentService?
# Ответ: Внутри объекта order, в его атрибуте экземпляра `self.payment_service`.
#
# 3. Что происходит при выполнении order.pay(5_000)?
# Ответ: Вызывается метод `pay` класса `Order`. Внутри он делегирует работу `payment_service`, вызывая его метод `pay(amount)`.
# Затем состояние заказа `is_paid` меняется на True, и метод возвращает строку с результатом.
#
# 4. Что выведут три вызова print()?
# Ответ: 
# - `Оплачено: 5000 ₽`
# - `True`
# - `{'number': 101, 'payment_service': <__main__.PaymentService object at ...>, 'is_paid': True}`
#
# 5. Почему Order не должен наследоваться от PaymentService?
# Ответ: Между ними нет отношения «является» (is-a). Заказ не является платёжным сервисом. 
# Наследование нарушило бы логику предметной области и принцип единственной ответственности (SRP).
#
# 6. Какое преимущество даёт передача payment_service через конструктор?
# Ответ: Это внедрение зависимостей (Dependency Injection). Оно позволяет легко подменять 
# платёжный сервис (например, на StripeService, PayPalService или MockPaymentService в тестах), 
# не меняя код самого класса Order.
#
# 7. Как здесь проявляется делегирование?
# Ответ: Класс Order имеет метод `pay`, но он не реализует логику проведения платежа самостоятельно, 
# а делегирует (передаёт) эту задачу объекту `payment_service`.