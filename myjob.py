import tkinter as tk
from scapy.all import sniff
from scapy.layers.inet import IP  # Импорт IP
from collections import defaultdict
import threading
import time

# Глобальные переменные для отслеживания активности
source_ips = defaultdict(int)  # Счетчик пакетов по исходным IP
last_packet_time = {}  # Время последнего пакета от IP
blocked_ips = set()  # Список заблокированных IP-адресов
suspicious_ips = set()  # Список подозрительных IP-адресов
sniffing = False  # Флаг для отслеживания статуса сниффинга

selected_ip = None  # Новая глобальная переменная для хранения выбранного IP-адреса
updating = False  # Новая глобальная переменная для отслеживания обновления списка

def block_traffic():
    global selected_ip
    if selected_ip and selected_ip not in blocked_ips:
        print(f"Блокирование данных от {selected_ip}")
        blocked_ips.add(selected_ip)
        suspicious_ips.discard(selected_ip)
        updating = True
        update_listboxes()
        updating = False

def unblock_traffic():
    global selected_ip
    if selected_ip in blocked_ips:
        print(f"Разблокирование данных от {selected_ip}")
        blocked_ips.remove(selected_ip)
        source_ips[selected_ip] = 0
        updating = True
        update_listboxes()
        updating = False

def ignore_traffic():
    global selected_ip
    if selected_ip in suspicious_ips:
        print(f"Игнорирование данных от {selected_ip}")
        suspicious_ips.remove(selected_ip)
        updating = True
        update_listboxes()
        updating = False

def analyze_packet(packet):
    global sniffing

    if not sniffing:
        return

    if IP in packet:
        source_ip = packet[IP].src
        packet_size = len(packet)

        # Проверка на большой размер пакета: размер пакета превышает заданный порог
        if packet_size > 512:  # Более 512 байт (0,5 КБ) за один пакет
            suspicious_ips.add(source_ip)

def start_sniffing():
    global sniffing
    sniffing = True
    print("Сканирование данных в сети...")
    sniff_thread = threading.Thread(target=lambda: sniff(prn=analyze_packet, store=0))
    sniff_thread.start()

def stop_sniffing():
    global sniffing
    sniffing = False
    print("Завершение сканирования данных в сети...")

def update_listboxes():
    global updating

    if not updating:
        all_listbox.delete(0, tk.END)  # Очищаем список перед обновлением
        suspicious_listbox.delete(0, tk.END)  # Очищаем список перед обновлением
        blocked_listbox.delete(0, tk.END)  # Очищаем список перед обновлением

        #all_listbox.insert(tk.END, "Общий список:")
        #suspicious_listbox.insert(tk.END, "Список подозрительных:")                          УДАЛИ!!!!!!!!!!!!!!!!!!
        #blocked_listbox.insert(tk.END, "Список заблокированных:")

        all_ips = list(source_ips.keys())
        suspicious_ips_list = list(suspicious_ips)
        blocked_ips_list = list(blocked_ips)

        for ip in all_ips:
            index = all_listbox.size()
            all_listbox.insert(tk.END, f"{ip}")

        for ip in suspicious_ips_list:
            index = suspicious_listbox.size()
            suspicious_listbox.insert(tk.END, f"{ip}")

        for ip in blocked_ips_list:
            index = blocked_listbox.size()
            blocked_listbox.insert(tk.END, f"{ip}")

    root.after(1000, update_listboxes)  # Запускаем обновление данных через 1 секунду

def select_ip(event):
    global selected_ip, updating

    if not updating:
        selection = event.widget.curselection()
        if selection:
            selected_ip = event.widget.get(selection)

def main():
    global root, all_listbox, suspicious_listbox, blocked_listbox

    root = tk.Tk()
    root.title("Сканирование данных в сети")

    start_button = tk.Button(root, text="Сканировать", command=start_sniffing)
    start_button.pack(pady=5)

    stop_button = tk.Button(root, text="Остановить", command=stop_sniffing)
    stop_button.pack(pady=5)


# Общий
    all_frame = tk.Frame(root)
    all_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
    all_label = tk.Label(all_frame, text="Общий:")
    all_label.pack(side=tk.TOP)
    all_listbox = tk.Listbox(all_frame, height=10, width=30)
    all_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    all_listbox.bind("<<ListboxSelect>>", select_ip)  # Добавляем обработчик события выбора IP-адреса

    # Подозрительные
    suspicious_frame = tk.Frame(root)
    suspicious_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
    suspicious_label = tk.Label(suspicious_frame, text="Подозрительные:")
    suspicious_label.pack(side=tk.TOP)
    suspicious_listbox = tk.Listbox(suspicious_frame, height=10, width=30)
    suspicious_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    suspicious_listbox.bind("<<ListboxSelect>>", select_ip)  # Добавляем обработчик события выбора IP-адреса
    block_button = tk.Button(suspicious_frame, text="Блокировать", command=block_traffic)
    block_button.pack(side=tk.BOTTOM, pady=5)
    ignore_button = tk.Button(suspicious_frame, text="Игнорировать", command=ignore_traffic)
    ignore_button.pack(side=tk.BOTTOM, pady=5)

    # Заблокированные
    blocked_frame = tk.Frame(root)
    blocked_frame.pack(side=tk.RIGHT, padx=5, pady=5, fill=tk.BOTH, expand=True)
    blocked_label = tk.Label(blocked_frame, text="Заблокированные:")
    blocked_label.pack(side=tk.TOP)
    blocked_listbox = tk.Listbox(blocked_frame, height=10, width=30)
    blocked_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    blocked_listbox.bind("<<ListboxSelect>>", select_ip)  # Добавляем обработчик события выбора IP-адреса
    unblock_button = tk.Button(blocked_frame, text="Разблокировать", command=unblock_traffic)
    unblock_button.pack(side=tk.BOTTOM, pady=5)

    # Запускаем обновление данных в текстовом поле
    update_listboxes()

    root.mainloop()

if __name__ == "__main__":

    main()