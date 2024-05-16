import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, hilbert
import pickle
import os

from controls import create_modulation_order_options, get_encoding_coefficients, get_block_length


def execute_demodulator(file_name):
    # Функция для проверки существования файла и запуска демодулятора.
    qam_file_name = f"{file_name}"

    if os.path.exists(qam_file_name):
        print(f"Файл {qam_file_name} найден.")
        data = load_qam_data(file_name)
        start_demodulator(file_name)
    else:
        print(f"Ошибка: Файл {qam_file_name} не найден.")


def start_demodulator(file_name):
    loaded_qam_data = load_qam_data(file_name)
    print(f"Загруженные данные из файла {file_name}:")
    for key, value in loaded_qam_data.items():
        if key == 'combined_signal':
            print(f"{key}: [длина = {len(value)}]")
        else:
            print(f"{key}: {value}")

    # Извлечение параметров и данных
    combined_signal = np.array(loaded_qam_data['combined_signal'])
    carrier_frequency = float(loaded_qam_data['carrier_frequency'])
    sampling_frequency = float(loaded_qam_data['sampling_frequency'])
    modulation_scheme = loaded_qam_data['modulation_order']
    data_length = int(loaded_qam_data['data_length'], 10)

    # Генерация массива времени
    num_elements = len(combined_signal)
    t = np.linspace(0, num_elements / sampling_frequency, num_elements)

    # Генерация синусоидальных сигналов
    sine_wave = np.sin(2 * np.pi * carrier_frequency * t)
    cosine_wave = np.cos(2 * np.pi * carrier_frequency * t)

    # Умножение combined_signal на синусоиду и косинусоиду
    multiplied__sine = 2 * combined_signal * sine_wave
    multiplied__cosine = 2 * combined_signal * cosine_wave

    # Получение длины блока и числа блоков
    block_length = get_block_length(modulation_scheme)
    num_blocks = -(-data_length * 4 // block_length)  # Округление вверх
    print(f"block_length - {block_length}")
    print(f"data_length - {data_length}")
    print(f"num_blocks - {num_blocks}")

    # Центрирование сигнала по сегментам
    segment_length = num_elements // num_blocks
    print(f"segment_length - {segment_length}")

    # Применение ФНЧ к сигналам
    cutoff_frequency = carrier_frequency / 3  # Пример частоты среза
    filtered_sine = low_pass_filter(multiplied__sine, cutoff_frequency, sampling_frequency)
    filtered_cosine = low_pass_filter(multiplied__cosine, cutoff_frequency, sampling_frequency)

    averaged_sine = average_mid_segment(filtered_sine, segment_length, (segment_length * num_blocks))
    averaged_cosine = average_mid_segment(filtered_cosine, segment_length, (segment_length * num_blocks))

    # Построение графиков
    plt.figure(figsize=(14, 10))

    plt.subplot(5, 1, 1)
    plt.plot(combined_signal, label='Combined Signal')
    plt.title('Combined Signal')
    plt.legend()

    plt.subplot(5, 1, 2)
    plt.plot(multiplied__sine, label='Filtered Signal * Sine Wave')
    plt.title('Combined Signal * Sine Wave')
    plt.legend()

    plt.subplot(5, 1, 3)
    plt.plot(multiplied__cosine, label='Filtered Signal * Cosine Wave', color='orange')
    plt.title('Combined Signal * Cosine Wave')
    plt.legend()

    plt.subplot(5, 1, 4)
    plt.plot(averaged_sine, label='Envelope Signal * Sine Wave')
    plt.title('Combined Signal * Sine Wave')
    plt.legend()

    plt.subplot(5, 1, 5)
    plt.plot(averaged_cosine, label='Envelope Signal * Cosine Wave', color='orange')
    plt.title('Combined Signal * Cosine Wave')
    plt.legend()

    plt.tight_layout()
    plt.savefig(f"{file_name}_multiplied.png")
    plt.show()

    coefficients = get_encoding_coefficients(modulation_scheme)
    # decoded_string = ""

    print(f"sine: {averaged_sine}")
    print(f"cosine: {averaged_cosine}")

    decoded_bits = []

    for avg_sine, avg_cosine in zip(averaged_sine, averaged_cosine):
        found = False
        for key, (coef_2, coef_1) in coefficients.items():
            if (abs((avg_sine - coef_2) / (coef_2 if coef_2 != 0 else 1)) <= 0.2 and
                    abs((avg_cosine - coef_1) / (coef_1 if coef_1 != 0 else 1)) <= 0.2):
                decoded_bits.append(format(int(key, 10), f'0{block_length}b'))
                # print(f"key: {key}, 2 coef {coef_2} sine{avg_sine}, 1 coef {coef_1} cosine {avg_cosine}")
                found = True
                break
        if not found:
            decoded_bits.append('0' * block_length)  # Если не найдено совпадение, добавляем неизвестный символ

    print(f"Decoded string: {decoded_bits}")

    # Корректное объединение битов
    total_bit_length = data_length * 4
    bit_sequence = ''
    for bits in decoded_bits:
        if len(bit_sequence) + len(bits) <= total_bit_length:
            bit_sequence += bits
        else:
            # Обрезаем лишние биты
            bit_sequence += bits[(block_length - (total_bit_length - len(bit_sequence))):]
            break
    print(f"bit_sequence: {bit_sequence}")

    # Разделение на блоки по 4 бита и преобразование в шестнадцатеричный вид
    hex_output = [format(int(bit_sequence[i:i + 4], 2), 'X') for i in range(0, len(bit_sequence), 4)]

    print(f"Hex output: {''.join(hex_output)}")


def load_qam_data(file_name):
    # Функция для загрузки данных из файла .qam.

    qam_file_name = f"{file_name}"
    with open(qam_file_name, 'rb') as qam_file:
        loaded_qam_data = pickle.load(qam_file)
    return loaded_qam_data


def average_mid_segment(signal, segment_length, num_elements):
    return np.array([
        np.mean(signal[i + segment_length // 4:i + 3 * segment_length // 4])
        for i in range(0, num_elements, segment_length)
    ])


def low_pass_filter(data, cutoff, fs, order=5):
    """
    Функция для применения фильтра нижних частот к данным.

    Args:
        data (array): Массив данных для фильтрации.
        cutoff (float): Частота среза фильтра.
        fs (float): Частота дискретизации.
        order (int): Порядок фильтра.

    Returns:
        array: Отфильтрованные данные.
    """
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    filtered_data = filtfilt(b, a, data)
    return filtered_data
