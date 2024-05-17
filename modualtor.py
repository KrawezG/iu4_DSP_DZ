import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
import numpy as np
import matplotlib.pyplot as plt
import pickle

from controls import create_modulation_order_options, get_encoding_coefficients, get_block_length


def execute_modulator(modulation_order_var, carrier_frequency_entry, sampling_frequency_entry, transmission_time_entry,
                      data_length_entry, data_entry, noise_level_entry, file_name_entry):
    # Функция на проверку заполненных полей и запуск модулятора
    if (modulation_order_var.get() and carrier_frequency_entry.get() and sampling_frequency_entry.get() and
            transmission_time_entry.get() and data_length_entry.get() and data_entry.get() and
            noise_level_entry.get() and file_name_entry.get()):

        carrier_frequency = float(carrier_frequency_entry.get())
        sampling_frequency = float(sampling_frequency_entry.get())

        # Проверка на соотношение частот по критерию Найквиста
        if sampling_frequency <= carrier_frequency * 2:
            messagebox.showerror("Ошибка",
                                 "Частота дискретизации должна быть больше несущей частоты  более чем в 2 раза.")
            return

        data_length = int(data_length_entry.get())
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


def start_modulator(data_dict):
    # Функция модулятора
    for key, value in data_dict.items():
        print(key + ":", value)

    # Деление исходных данных на блоки данных для схемы модуляции
    blocks, array = process_data(data_dict)
    for block in blocks:
        print(block)

    print("\nArray:")
    print(array)

    # Построение синфазного  сигнала, квадратурного сигнала и их суммы
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
    plt.savefig(f"{data_dict['file_name']}.png")
    plt.show()

    qam_data = {
        'modulation_order': data_dict['modulation_order'],
        'carrier_frequency': data_dict['carrier_frequency'],
        'sampling_frequency': data_dict['sampling_frequency'],
        'transmission_time': data_dict['transmission_time'],
        'data_length': data_dict['data_length'],
        'combined_signal': combined_signal
    }

    qam_file_name = f"{data_dict['file_name']}.qam"
    with open(qam_file_name, 'wb') as qam_file:
        pickle.dump(qam_data, qam_file)

    print(f"Данные успешно сохранены в файл {qam_file_name}")


def hex_to_binary(hex_string):
    # Функция для конвертации строки шестнадцатеричных чисел в двоичный вид
    binary_data = ''.join(format(int(char, 16), '04b') for char in hex_string)
    return binary_data


def split_binary_data(binary_data, block_length):
    # Функция для разбиения двоичных данных на блоки длины block_length
    blocks = [binary_data[i:i + block_length] for i in range(0, len(binary_data), block_length)]

    # Проверка последнего блока ти дополнение его нулями при необходимости
    if len(blocks[-1]) < block_length:
        blocks[-1] = blocks[-1].rjust(block_length, '0')

    return blocks


def process_data(data_dict):
    # Функция для обработки данных, извлеченных из словаря
    modulation_scheme = (data_dict['modulation_order'])
    sampling_frequency = float(data_dict['sampling_frequency'])
    transmission_time = float(data_dict['transmission_time'])
    data = data_dict['data']

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
    array = [[0, 0]] * num_elements

    # Получаем коэффициенты для данной схемы модуляции
    coefficients = get_encoding_coefficients(modulation_scheme)

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
    # Функция для генерации синфазного и квадратурного сигналов с добавлением шума и их суммирования
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
