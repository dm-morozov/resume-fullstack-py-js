def my_callback(num):
    # Коллбэк уже написан, он просто задает правила
    if num % 2 == 0:
        return "delete"      # Удаляем все четные
    elif num > 10:
        return "duplicate"   # Дублируем те, что больше 10
    else:
        return "ignore"      # Остальные игнорируем

def process_numbers(numbers, action_callback):
    for num in numbers[:]: # Создаем копию списка для безопасной итерации
        if action_callback(num) == "delete":
            numbers.remove(num)
        elif action_callback(num) == "duplicate":
            numbers.append(num)

# Тестовые данные
data = [1, 2, 3, 4, 15, 6]

process_numbers(data, my_callback)
print(data) 
# Ожидаемый результат: [1, 3, 15, 15] 
# (2, 4 и 6 удалились, 15 сдублировалось в конец)