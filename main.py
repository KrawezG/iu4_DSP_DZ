import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
import numpy as np
import matplotlib.pyplot as plt


def start_modulator(data_dict):
    for key, value in data_dict.items():
        print(key + ":", value)

    blocks, array = process_data(data_dict)
    for block in blocks:
        print(block)

    print("\nArray:")
    print(array)

    sine_wave, cosine_wave, combined_signal = generate_signals(array, float(data_dict['carrier_frequency']),
                                                               float(data_dict['sampling_frequency']),
                                                               float(data_dict['noise_level']))

    # Построение графиков
    plt.figure(figsize=(14, 7))

    plt.subplot(3, 1, 1)
    plt.plot(sine_wave, label='Sine Wave')
    plt.title('Sine Wave')
    plt.legend()

    plt.subplot(3, 1, 2)
    plt.plot(cosine_wave, label='Cosine Wave', color='orange')
    plt.title('Cosine Wave')
    plt.legend()

    plt.subplot(3, 1, 3)
    plt.plot(combined_signal, label='Combined Signal', color='green')
    plt.title('Combined Signal')
    plt.legend()

    plt.tight_layout()
    plt.show()


def hex_to_binary(hex_string):
    """Функция для конвертации строки шестнадцатеричных чисел в двоичный вид."""
    binary_data = ''.join(format(int(char, 16), '04b') for char in hex_string)
    return binary_data


def split_binary_data(binary_data, block_length):
    """Функция для разбиения двоичных данных на блоки длины block_length."""
    blocks = [binary_data[i:i + block_length] for i in range(0, len(binary_data), block_length)]

    # Проверка последнего блока
    if len(blocks[-1]) < block_length:
        blocks[-1] = blocks[-1].rjust(block_length, '0')

    return blocks


def process_data(data_dict):
    """Функция для обработки данных, извлеченных из словаря."""
    modulation_scheme = (data_dict['modulation_order'])
    carrier_frequency = float(data_dict['carrier_frequency'])
    sampling_frequency = float(data_dict['sampling_frequency'])
    transmission_time = float(data_dict['transmission_time'])
    data_length = data_dict['data_length']
    data = data_dict['data']
    noise_level = float(data_dict['noise_level'])
    file_name = data_dict['file_name']

    # Получение длины блока на основе схемы модуляции
    block_length = get_block_length(modulation_scheme)
    if block_length == 0:
        raise ValueError(f"Неизвестная схема модуляции: {modulation_scheme}")

    # Конвертация шестнадцатеричных данных в двоичный вид
    binary_data = hex_to_binary(data)

    # Разбиваем двоичные данные на блоки длины block_length
    blocks = split_binary_data(binary_data, block_length)

    # Создаем массив с числом элементов, равным произведению частоты дискретизации на время передачи
    num_elements = int(sampling_frequency * transmission_time)
    array = [[0, 0]] * num_elements  # Инициализируем массив нулями

    # Получаем коэффициенты для данной схемы модуляции
    coefficients = get_encoding_coefficients(modulation_scheme)

    print(coefficients)

    # Заполняем массив коэффициентами
    segment_length = num_elements // len(blocks)
    for i, block in enumerate(blocks):
        decimal_value = int(block, 2)
        for j in range(segment_length):
            index = i * segment_length + j
            if index < num_elements:
                array[index] = coefficients[str(decimal_value)]

    return blocks, array


def generate_signals(array, carrier_frequency, sampling_frequency, noise_level):
    """Функция для генерации синусоидальных и косинусоидальных сигналов с добавлением шума и их суммирования."""
    num_elements = len(array)
    t = np.linspace(0, num_elements / sampling_frequency, num_elements)

    # Разделение array на два массива коэффициентов
    coefficients1 = np.array([coeff[0] for coeff in array])
    coefficients2 = np.array([coeff[1] for coeff in array])

    # Генерация синусоиды и косинусоиды с использованием несущей частоты
    sine_wave = np.sin(2 * np.pi * carrier_frequency * t) * coefficients1
    cosine_wave = np.cos(2 * np.pi * carrier_frequency * t) * coefficients2

    # Генерация случайного шума
    noise = np.random.randn(num_elements) * noise_level / 100

    # Суммирование сигналов и добавление шума
    combined_signal = sine_wave + cosine_wave + noise

    return sine_wave, cosine_wave, combined_signal


def start_demodulator(file_name):
    messagebox.showinfo("Режим Демодулятора", f"Выбранный файл: {file_name}")


def open_file_dialog(file_name_entry):
    file_name_entry.config(state="normal")  # Устанавливаем состояние "обычное"
    filetypes = (("QAM датаграмма файл", "*.qam"),
                 ("Текстовый файл", "*.txt"),
                 ("Изображение", "*.jpg *.gif *.png"),
                 ("Любой", "*"))
    file_name = filedialog.askopenfilename(filetypes=filetypes)
    file_name_entry.delete(0, tk.END)
    file_name_entry.insert(0, file_name)
    file_name_entry.config(state="readonly")  # Устанавливаем состояние "readonly" после вставки значения


def execute_modulator(modulation_order_var, carrier_frequency_entry, sampling_frequency_entry, transmission_time_entry,
                      data_length_entry, data_entry, noise_level_entry, file_name_entry):
    # Проверка на заполненность всех полей
    if (modulation_order_var.get() and carrier_frequency_entry.get() and sampling_frequency_entry.get() and
            transmission_time_entry.get() and data_length_entry.get() and data_entry.get() and
            noise_level_entry.get() and file_name_entry.get()):

        # Получаем значения частот
        carrier_frequency = float(carrier_frequency_entry.get())
        sampling_frequency = float(sampling_frequency_entry.get())

        # Проверка на соотношение частот
        if sampling_frequency <= carrier_frequency * 2:
            messagebox.showerror("Ошибка",
                                 "Частота дискретизации должна быть больше несущей частоты  более чем в 2 раза.")
            return

        # Получаем значения длины данных
        data_length = int(data_length_entry.get())
        # Получаем данные из поля
        data = data_entry.get()

        # Проверка на соответствие длины данных
        if data_length != len(data):
            messagebox.showerror("Ошибка", "Длина данных не совпадает с указанной длиной.")
            return

        # Если все поля заполнены и соответствуют условиям, создаем словарь с данными
        data_dict = {
            'modulation_order': modulation_order_var.get(),
            'carrier_frequency': carrier_frequency_entry.get(),
            'sampling_frequency': sampling_frequency_entry.get(),
            'transmission_time': transmission_time_entry.get(),
            'data_length': data_length_entry.get(),
            'data': data_entry.get(),
            'noise_level': noise_level_entry.get(),
            'file_name': file_name_entry.get()
        }

        # Вызываем функцию open_modulator с нашим словарем
        start_modulator(data_dict)
    else:
        # Если какое-то поле не заполнено, выводим сообщение об ошибке
        messagebox.showerror("Ошибка", "Все поля должны быть заполнены.")


from validators import validate_frequency, validate_time, validate_data_length, validate_hex_data, validate_noise_level, \
    validate_file_name_length

from controls import create_modulation_order_options, get_encoding_coefficients, get_block_length


def show_modulator_fields(modulator_frame, demodulator_frame):
    modulator_frame.pack(pady=10)
    demodulator_frame.pack_forget()
    # select_mode_button.config(command=open_modulator)


def show_demodulator_fields(modulator_frame, demodulator_frame):
    modulator_frame.pack_forget()
    demodulator_frame.pack(pady=10)
    # select_mode_button.config(command=open_demodulator)


def qam_mod():
    # Создание главного окна
    root = tk.Tk()
    root.title("Выбор режима")

    mode_var = tk.StringVar(root, "Модулятор")
    data_dict = {}

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
    modulation_order_var.set("QAM4")  # Устанавливаем значение по умолчанию

    modulation_order_option_menu = ttk.Combobox(modulator_frame, textvariable=modulation_order_var,
                                                values=create_modulation_order_options())
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
    data_length_label = tk.Label(modulator_frame, text="Число данных в hex:")
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

    # Название файла
    filename_label = tk.Label(modulator_frame, text="Название файла (не более 100 символов):")
    filename_label.grid(row=7, column=0, padx=5, pady=5)

    validate_file_name_length_cmd = (root.register(validate_file_name_length), "%P")
    filename_entry = tk.Entry(modulator_frame, validate="key", validatecommand=validate_file_name_length_cmd)
    filename_entry.grid(row=7, column=1, padx=5, pady=5)

    # Фрейм для выбора файла
    demodulator_frame = tk.Frame(root)

    # Надпись для выбора файла
    file_name_label = tk.Label(demodulator_frame, text="Выберите файл:")
    file_name_label.grid(row=0, column=0, padx=5, pady=5)

    # Поле для отображения выбранного файла
    file_name_entry = tk.Entry(demodulator_frame, state="readonly")
    file_name_entry.grid(row=0, column=1, padx=5, pady=5)

    # Кнопка для выбора файла
    select_file_button = tk.Button(demodulator_frame, text="Обзор...",
                                   command=lambda: open_file_dialog(file_name_entry))
    select_file_button.grid(row=0, column=2, padx=5, pady=5)

    # Привязка действий к изменению режима
    mode_var.trace_add("write", lambda *args: (show_modulator_fields(modulator_frame,
                                                                     demodulator_frame) if mode_var.get() == "Модулятор" else show_demodulator_fields(
        modulator_frame, demodulator_frame)))

    # Кнопка для открытия окна выбора режима
    do_modulator_button = tk.Button(modulator_frame, text="Выполнить 1",
                                    command=lambda: execute_modulator(modulation_order_var, carrier_frequency_entry,
                                                                      sampling_frequency_entry, transmission_time_entry,
                                                                      data_length_entry, data_entry, noise_level_entry,
                                                                      filename_entry))
    do_modulator_button.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

    # Кнопка для открытия окна выбора режима
    do_demodulator_button = tk.Button(demodulator_frame, text="Выполнить 2",
                                      command=lambda: start_demodulator(file_name_entry.get()))
    do_demodulator_button.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

    # Запуск главного цикла обработки событий
    root.mainloop()


if __name__ == "__main__":
    qam_mod()
