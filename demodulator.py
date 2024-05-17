import tkinter as tk
from tkinter import Toplevel
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.signal import butter, filtfilt, hilbert
import pickle
import os

from controls import get_encoding_coefficients, get_block_length


def execute_demodulator(root, file_name):
    # Функция для проверки существования файла и запуска демодулятора.
    qam_file_name = f"{file_name}"

    if os.path.exists(qam_file_name):
        print(f"Файл {qam_file_name} найден.")
        data = load_qam_data(file_name)
        start_demodulator(root, file_name)
    else:
        print(f"Ошибка: Файл {qam_file_name} не найден.")


def start_demodulator(root, file_name):
    # Функция демодулирования
    loaded_qam_data = load_qam_data(file_name)

    # Извлечение параметров и данных
    combined_signal = np.array(loaded_qam_data['combined_signal'])
    carrier_frequency = float(loaded_qam_data['carrier_frequency'])
    sampling_frequency = float(loaded_qam_data['sampling_frequency'])
    modulation_scheme = loaded_qam_data['modulation_order']
    data_length = int(loaded_qam_data['data_length'], 10)

    num_elements = len(combined_signal)
    t = np.linspace(0, num_elements / sampling_frequency, num_elements)

    sine_wave = np.sin(2 * np.pi * carrier_frequency * t)
    cosine_wave = np.cos(2 * np.pi * carrier_frequency * t)

    # Умножение combined_signal на синусоиду и косинусоиду
    multiplied__sine = 2 * combined_signal * sine_wave
    multiplied__cosine = 2 * combined_signal * cosine_wave

    # Получение длины блока, числа блоков, длины сегмента
    block_length = get_block_length(modulation_scheme)
    num_blocks = -(-data_length * 4 // block_length)

    segment_length = num_elements // num_blocks

    # Применение ФНЧ к сигналам
    cutoff_frequency = carrier_frequency / 3
    filtered_sine = low_pass_filter(multiplied__sine, cutoff_frequency, sampling_frequency)
    filtered_cosine = low_pass_filter(multiplied__cosine, cutoff_frequency, sampling_frequency)

    averaged_sine = average_mid_segment(filtered_sine, segment_length, (segment_length * num_blocks))
    averaged_cosine = average_mid_segment(filtered_cosine, segment_length, (segment_length * num_blocks))

    coefficients = get_encoding_coefficients(modulation_scheme)

    decoded_bits = []

    for avg_sine, avg_cosine in zip(averaged_sine, averaged_cosine):
        found = False
        for key, (coef_2, coef_1) in coefficients.items():
            if (abs((avg_sine - coef_2) / (coef_2 if coef_2 != 0 else 1)) <= 0.2 and
                    abs((avg_cosine - coef_1) / (coef_1 if coef_1 != 0 else 1)) <= 0.2):
                decoded_bits.append(format(int(key, 10), f'0{block_length}b'))
                found = True
                break
        if not found:
            decoded_bits.append(
                '0' * block_length)  # Если не найдено совпадение, добавляем 0 (для простоты работы, по хорошему ошибка приема сообщения)

    # Восстановление исходной битовой последовательности из блоков
    total_bit_length = data_length * 4
    bit_sequence = ''
    for bits in decoded_bits:
        if len(bit_sequence) + len(bits) <= total_bit_length:
            bit_sequence += bits
        else:
            # Обрезка добавленных битов
            bit_sequence += bits[(block_length - (total_bit_length - len(bit_sequence))):]
            break

    # Разделение на блоки по 4 бита и преобразование в шестнадцатеричный вид
    hex_output = [format(int(bit_sequence[i:i + 4], 2), 'X') for i in range(0, len(bit_sequence), 4)]

    # Создание нового окна для отображения результатов
    result_window = Toplevel(root)
    result_window.title("Demodulation Results")

    result_text = f"Carrier Frequency: {carrier_frequency} Hz\n"
    result_text += f"Sampling Frequency: {sampling_frequency} Hz\n"
    result_text += f"Modulation Scheme: {modulation_scheme}\n"
    result_text += f"Data Length: {data_length}\n"
    result_text += f"Decoded Message (Hex): {''.join(hex_output)}\n"

    text_label = tk.Label(result_window, text=result_text, justify=tk.LEFT)
    text_label.pack()

    # Отображение графика
    fig, ax = plt.subplots()
    ax.plot(t, combined_signal, label='Combined Signal')
    ax.plot(t, filtered_sine, label='Filtered Sine Component')
    ax.plot(t, filtered_cosine, label='Filtered Cosine Component')
    ax.legend()

    canvas = FigureCanvasTkAgg(fig, master=result_window)
    canvas.draw()
    canvas.get_tk_widget().pack()


def load_qam_data(file_name):
    # Функция для загрузки данных из файла .qam.

    qam_file_name = f"{file_name}"
    with open(qam_file_name, 'rb') as qam_file:
        loaded_qam_data = pickle.load(qam_file)
    return loaded_qam_data


def average_mid_segment(signal, segment_length, num_elements):
    # Создание массива среднего значения у сегментов данных
    return np.array([
        np.mean(signal[i + segment_length // 4:i + 3 * segment_length // 4])
        for i in range(0, num_elements, segment_length)
    ])


def low_pass_filter(data, cutoff, fs, order=5):
    # ФНЧ
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    filtered_data = filtfilt(b, a, data)
    return filtered_data
