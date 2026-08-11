def create_counter():
    count = 0  # Переменная во внешней (Enclosing) области
    def increment():
        nonlocal count # Явно указываем, что переменная берется из уровня E (Enclosing)
        count += 1  # Пытаемся увеличить счетчик
        return count

    return increment

my_counter = create_counter()
print(my_counter())
print(my_counter())

my_counter_2 = create_counter()
print(my_counter_2())