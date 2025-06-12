import requests
import os
import datetime
from collections import defaultdict

print("🧠 KASPI BOT VERSION: v3.5-debug-tagged")

KASPI_API_TOKEN = os.getenv("KASPI_API_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_orders():
    headers = {
        "X-Auth-Token": KASPI_API_TOKEN,
        "Content-Type": "application/json"
    }
    url = "https://mc.shop.kaspi.kz/mc/api/orderTabs/active?count=100&selectedTabs=KASPI_DELIVERY_ASSEMBLY&startIndex=0&loadPoints=true&_m=30067732"

    response = requests.get(url, headers=headers)
    print("🔴 Raw response from Kaspi API:")
    print(response.text)

    try:
        data = response.json()
    except Exception as e:
        print("❌ Ошибка при разборе JSON:", str(e))
        return []

    if not data or not isinstance(data, list):
        print("⚠️ Пустой или некорректный ответ от Kaspi API.")
        return []

    raw_orders = data[0].get("orders", [])
    print("🟡 Orders from JSON:", raw_orders)

    orders = []

    for order in raw_orders:
        print("🧾 Обрабатываем заказ:", order.get("id"))
        positions = order.get("positions", [])
        print(f"📦 Позиции в заказе {order.get('id')}: {positions}")

        for product in positions:
            print("📦 Найден товар:", product)
            name = product.get("name", "").lower()
            qty = product.get("quantity", 1)

            color = "неизвестно"
            size = "неизвестно"

            for c in ["черный", "белый", "синий", "красный", "бежевый"]:
                if c in name:
                    color = c

            for s in ["xxl", "xl", "l", "m", "s"]:
                if (
                    f" {s} " in f" {name} "
                    or f",{s}" in name
                    or name.endswith(f" {s}")
                    or name.endswith(f",{s}")
                ):
                    size = s.upper()
                    break

            orders.append({"color": color, "size": size, "qty": qty})

    print("🟢 Orders ready to send:")
    print(orders)
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
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }
    print("📤 Отправка в Telegram:", payload)
    response = requests.post(url, data=payload)
    print("📬 Ответ Telegram:", response.status_code, response.text)
    return response.ok

if __name__ == "__main__":
    orders = get_orders()

    print("✅ MAIN: Получены заказы:", orders)
    print("✅ MAIN: Длина списка заказов:", len(orders))

    if isinstance(orders, list) and any(orders):
        message = format_orders(orders)
        print("📦 Отправляем список заказов в Telegram")
    else:
        print("❌ Список заказов пустой или некорректный")
        kz_time = datetime.datetime.utcnow() + datetime.timedelta(hours=5)
        now = kz_time.strftime("%Y-%m-%d %H:%M:%S") + " (KZT)"
        message = f"❌ [v3.5-debug-tagged] Нет заказов на сборку. Время: {now}"

    print("📨 Финальное сообщение:")
    print(message)

    send_to_telegram(message)
