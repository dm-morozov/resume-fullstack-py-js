def process_data(number, items):
    """
    Функция принимает число и список, изменяет только список, т.к
    число неизменяемый тип данных, 
    а список изменяемый тип данных и ничего не возвращает
    :param number: это число
    :param items: это список
    :return: ничего не возвращает
    """
    number +=10
    items.append(4)

a=5
b=[1,2,3]
process_data(a,b)
print(a)
print(b)

def add_employee(name, team=[]):
    """
    Функция принимает имя и список, добавляет имя в список и возвращает список
    :param name: это имя
    :param team: это список
    :return: это список
    """
    team.append(name)
    return team

print(add_employee("Иван"))
print(add_employee("Анна", ["Сергей", "Мария"]))
print(add_employee("Петр"))

def add_employee_right(name, team=None):
    """
    Функция принимает имя и список, добавляет имя сотрудника
    в список и возвращает обновленный список.
    Если список не передан, создается новый список.
    :param name: это имя
    :param team: это список
    :return: это список
    """
    if team is None:
        team = []
    team.append(name)
    return team

print(add_employee_right("Иван"))
print(add_employee_right("Анна", ["Сергей", "Мария"]))
print(add_employee_right("Петр"))