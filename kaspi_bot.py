import requests
import os
from collections import defaultdict

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
    if response.status_code != 200:
        print("Ошибка:", response.text)
        return []

    data = response.json()
    orders = []
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
    requests.post(url, data=payload)

if __name__ == "__main__":
    orders = get_orders()
    if orders:
        message = format_orders(orders)
        send_to_telegram(message)
    else:
        send_to_telegram("Нет заказов на сборку.")
