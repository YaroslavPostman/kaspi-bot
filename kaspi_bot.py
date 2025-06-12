import requests
import os
import datetime
from collections import defaultdict

# Получаем переменные из GitHub Secrets
KASPI_API_TOKEN = os.getenv("KASPI_API_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_orders():
    headers = {
        "X-Auth-Token": KASPI_API_TOKEN,
        "Content-Type": "application/json"
    }
    url = "https://mc.shop.kaspi.kz/mc/api/orderTabs/active?count=100&selectedTabs=KASPI_DELIVERY_CARGO_ASSEMBLY&startIndex=0&loadPoints=true&_m=30067732"
    
    response = requests.get(url, headers=headers)
    print("Ответ от Kaspi API:")
    print(response.text)

    try:
        data = response.json()
    except Exception as e:
        print("Ошибка разбора JSON:", str(e))
        return []

    orders = []

    try:
        for order in data[0].get("orders", []):
            for product in order.get("positions", []):
                name = product.get("name", "").lower()
                qty = product.get("quantity", 1)

                color = "неизвестно"
                size = "неизвестно"

                for c in ["черный", "белый", "синий", "красный", "бежевый"]:
                    if c in name:
                        color = c
                for s in ["s", "m", "l", "xl", "xxl"]:
                    if f" {s} " in name or name.endswith(f" {s}"):
                        size = s.upper()

                orders.append({"color": color, "size": size, "qty": qty})
    except Exception as e:
        print("Ошибка при обработке заказов:", str(e))

    return orders

def format_orders(orders):
    grouped = defaultdict(lambda: defaultdict(int))
    for order in orders:
        grouped[order["color"]][order["size"]] += order["qty"]

    message = ""
    for color, sizes in grouped.items():
        message += f"Цвет {color}:\n"
        for size, qty in sizes.items():
            message += f"  {size} - {qty}\n"
    return message.strip()

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    print("Отправка в Telegram:")
    print(payload)
    response = requests.post(url, data=payload)
    print("Ответ Telegram:", response.status_code, response.text)
    return response.ok

if __name__ == "__main__":
    orders = get_orders()
    
    if orders:
        message = format_orders(orders)
    else:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Нет заказов на сборку. Время: {now}"  # Уникальное сообщение

    print("Сообщение:")
    print(message)
    send_to_telegram(message)
