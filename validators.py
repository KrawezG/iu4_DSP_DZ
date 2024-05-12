# validators.py

def validate_frequency(new_value):
    try:
        # Пробуем преобразовать новое значение в число
        frequency = float(new_value)
        # Проверяем, что число положительное
        if frequency <= 0:
            return False
        else:
            return True
    except ValueError:
        # Если не удалось преобразовать в число, возвращаем False
        return False

def validate_time(new_value):
    try:
        # Пробуем преобразовать новое значение в число
        frequency = float(new_value)
        # Проверяем, что число положительное
        if frequency <= 0:
            return False
        else:
            return True
    except ValueError:
        # Если не удалось преобразовать в число, возвращаем False
        return False

def validate_data_length(new_value):
    try:
        # Пробуем преобразовать новое значение в число
        length = int(new_value)
        # Проверяем, что число положительное
        if length <= 0:
            return False
        else:
            return True
    except ValueError:
        # Если не удалось преобразовать в число, возвращаем False
        return False

def validate_hex_data(new_value):
    # Проверяем, что все символы нового значения являются допустимыми для шестнадцатеричной системы счисления
    for char in new_value:
        if char.lower() not in "0123456789abcdef":
            return False
    return True

def validate_noise_level(new_value):
    try:
        # Пробуем преобразовать новое значение в число
        level = int(new_value)
        # Проверяем, что число в диапазоне от 0 до 100
        if level < 0 or level > 100:
            return False
        else:
            return True
    except ValueError:
        # Если не удалось преобразовать в число, возвращаем False
        return False

def validate_file_name_length(new_value):
    # Проверяем длину нового значения
    if len(new_value) <= 100:
        return True
    else:
        return False
