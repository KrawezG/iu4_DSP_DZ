# validators.py

def validate_frequency(new_value):
    # Проверяем частоту
    try:
        frequency = float(new_value)
        if frequency <= 0:
            return False
        else:
            return True
    except ValueError:
        return False


def validate_time(new_value):
    # Проверяем время передачи данных
    try:
        frequency = float(new_value)
        if frequency <= 0:
            return False
        else:
            return True
    except ValueError:
        return False


def validate_data_length(new_value):
    # Проверяем длину данных
    try:
        length = int(new_value)
        if length <= 0:
            return False
        else:
            return True
    except ValueError:
        return False


def validate_hex_data(new_value):
    # Проверяем введеные символы данных
    for char in new_value:
        if char.lower() not in "0123456789abcdef":
            return False
    return True


def validate_noise_level(new_value):
    # Проверяем значение шума
    try:
        # Пробуем преобразовать новое значение в число
        level = int(new_value)
        # Проверяем, что число в диапазоне от 0 до 100
        if level < 0 or level > 100:
            return False
        else:
            return True
    except ValueError:
        return False


def validate_file_name_length(new_value):
    # Проверяем длину имени файла
    if len(new_value) <= 100:
        return True
    else:
        return False
