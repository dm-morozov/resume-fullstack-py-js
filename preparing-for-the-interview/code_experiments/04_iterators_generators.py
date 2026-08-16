my_list = [10, 20, 30, 40]

# 1. Получаем итератор (создаем закладку для этого списка)
my_iterator = iter(my_list)

try:
    # 2. Просим элементы по одному
    print(next(my_iterator))
    print(next(my_iterator))
    print(next(my_iterator))
    print(next(my_iterator))

    # 3. Элементы закончились. Что будет дальше?
    print(next(my_iterator))
except StopIteration:
    print("У объекта не осталось элементов")


# Что под капотом делает цикл for

my_iter = iter(my_list)

while True:
    try:
        item = (next(my_iter))
        print(item)
    except StopIteration:
        break


class MyCounter:
    def __init__(self, limit):
        self.limit = limit
        self.current = 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= self.limit:
            result = self.current
            self.current += 1
            return result
        else:
            raise StopIteration


counter = MyCounter(3)

try:
    while True:
        print(next(counter))
except StopIteration:
    print("Последовательность закончилась", end="\n\n")

print("Начинаем цикл for", end="\n")

counter2 = MyCounter(3)

for count in counter2:
    print(count)


# Генераторы

print('\n', 'Генератор: ', end='\n')

def my_counter_generator(limit):
    current = 1
    while current <= limit:
        yield current
        current +=1


for count in my_counter_generator(3):
    print(count)