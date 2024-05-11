import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog

def open_modulator():
    modulation_order = modulation_order_var.get()
    carrier_frequency = carrier_frequency_entry.get()
    sampling_frequency = sampling_frequency_entry.get()
    transmission_time = transmission_time_entry.get()
    data_length = data_length_entry.get()
    data = data_entry.get()
    noise_level = noise_level_entry.get()
    file_name = file_name_entry.get()

    messagebox.showinfo("Режим Модулятора",
        f"Порядок демодулятора: {modulation_order}\n"
        f"Частота несущей: {carrier_frequency}\n"
        f"Частота дискретизации: {sampling_frequency}\n"
        f"Время передачи: {transmission_time}\n"
        f"Число данных: {data_length}\n"
        f"Данные: {data}\n"
        f"Уровень шума: {noise_level}\n"
        f"Имя файла: {file_name}")


def open_demodulator(file_name):


    messagebox.showinfo("Режим Демодулятора", f"Выбранный файл: {file_name}")

def create_modulation_order_options():
    return ['1', '2', '3', '4']
def open_file_dialog():
    file_name = filedialog.askopenfilename()
    file_name_entry.delete(0, tk.END)
    file_name_entry.insert(0, file_name)

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

def qam_mod():
    def show_modulator_fields():
        modulator_frame.pack(pady=10)
        demodulator_frame.pack_forget()
        #select_mode_button.config(command=open_modulator)

    def show_demodulator_fields():
        modulator_frame.pack_forget()
        demodulator_frame.pack(pady=10)
        #select_mode_button.config(command=open_demodulator)

    # Создание главного окна
    root = tk.Tk()
    root.title("Выбор режима")

    mode_var = tk.StringVar(root, "Модулятор")

    # Фрейм для выбора режима
    mode_frame = tk.Frame(root)
    mode_frame.pack(pady=10)

    mode_selector = ttk.Combobox(mode_frame, textvariable=mode_var, values=["Модулятор", "Демодулятор"])
    mode_selector.pack(padx=5, pady=5)

    # Фрейм для параметров модулятора
    modulator_frame = tk.Frame(root)

    # Порядок демодулятора
    modulation_order_label = tk.Label(modulator_frame, text="Порядок демодулятора:")
    modulation_order_label.grid(row=0, column=0, padx=5, pady=5)

    modulation_order_var = tk.StringVar(root)
    modulation_order_var.set("1")  # Устанавливаем значение по умолчанию

    modulation_order_option_menu = ttk.Combobox(modulator_frame, textvariable=modulation_order_var, values=create_modulation_order_options())
    modulation_order_option_menu.grid(row=0, column=1, padx=5, pady=5)

    # Частота несущей
    carrier_frequency_label = tk.Label(modulator_frame, text="Частота несущей:")
    carrier_frequency_label.grid(row=1, column=0, padx=5, pady=5)

    carrier_frequency_entry = tk.Entry(modulator_frame, validate="key",
                                       validatecommand=(root.register(validate_frequency), "%P"))
    carrier_frequency_entry.grid(row=1, column=1, padx=5, pady=5)

    # Частота дискретизации
    sampling_frequency_label = tk.Label(modulator_frame, text="Частота дискретизации:")
    sampling_frequency_label.grid(row=2, column=0, padx=5, pady=5)

    sampling_frequency_entry = tk.Entry(modulator_frame, validate="key",
                                       validatecommand=(root.register(validate_frequency), "%P"))
    sampling_frequency_entry.grid(row=2, column=1, padx=5, pady=5)

    # Время передачи
    transmission_time_label = tk.Label(modulator_frame, text="Время передачи:")
    transmission_time_label.grid(row=3, column=0, padx=5, pady=5)

    transmission_time_entry = tk.Entry(modulator_frame, validate="key",
                                        validatecommand=(root.register(validate_time), "%P"))
    transmission_time_entry.grid(row=3, column=1, padx=5, pady=5)

    # Число данных
    data_length_label = tk.Label(modulator_frame, text="Число данных:")
    data_length_label.grid(row=4, column=0, padx=5, pady=5)

    data_length_entry = tk.Entry(modulator_frame, validate="key",
                                 validatecommand=(root.register(validate_data_length), "%P"))
    data_length_entry.grid(row=4, column=1, padx=5, pady=5)

    # Данные
    data_label = tk.Label(modulator_frame, text="Данные (16-ричное представление):")
    data_label.grid(row=5, column=0, padx=5, pady=5)

    data_entry = tk.Entry(modulator_frame, validate="key",
                          validatecommand=(root.register(validate_hex_data), "%P"))
    data_entry.grid(row=5, column=1, padx=5, pady=5)

    # Уровень шума
    noise_level_label = tk.Label(modulator_frame, text="Уровень шума (от 0 до 100):")
    noise_level_label.grid(row=6, column=0, padx=5, pady=5)

    noise_level_entry = tk.Entry(modulator_frame, validate="key",
                                 validatecommand=(root.register(validate_noise_level), "%P"))
    noise_level_entry.grid(row=6, column=1, padx=5, pady=5)

    # Фрейм для выбора файла
    demodulator_frame = tk.Frame(root)

    # Надпись для выбора файла
    file_name_label = tk.Label(demodulator_frame, text="Выберите файл:")
    file_name_label.grid(row=0, column=0, padx=5, pady=5)

    # Поле для отображения выбранного файла
    file_name_entry = tk.Entry(demodulator_frame, state="readonly")
    file_name_entry.grid(row=0, column=1, padx=5, pady=5)

    # Кнопка для выбора файла
    select_file_button = tk.Button(demodulator_frame, text="Обзор...", command=open_file_dialog)
    select_file_button.grid(row=0, column=2, padx=5, pady=5)

    # Привязка действий к изменению режима
    mode_var.trace_add("write", lambda *args: (show_modulator_fields() if mode_var.get() == "Модулятор" else show_demodulator_fields()))

    # Кнопка для открытия окна выбора режима
    do_modulator_button = tk.Button(modulator_frame, text="Выполнить 1", command=open_modulator)
    do_modulator_button.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

    # Кнопка для открытия окна выбора режима
    do_demodulator_button = tk.Button(demodulator_frame, text="Выполнить 2", command=open_demodulator(file_name_entry.get()))
    do_demodulator_button.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

    # Запуск главного цикла обработки событий
    root.mainloop()

if __name__ == "__main__":
    qam_mod()
