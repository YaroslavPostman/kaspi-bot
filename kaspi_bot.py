import requests
import datetime
import pytz
import json
import os

# ⚙️ Конфигурация
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
KASPI_API_URL = os.getenv("KASPI_API_URL")

# 🕐 Текущая дата в KZT
tz = pytz.timezone("Asia/Almaty")
current_time = datetime.datetime.now(tz)
formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

# 🔄 Получение заказов
def get_orders():
    try:
        response = requests.get(KASPI_API_URL)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status code: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# 📤 Отправка сообщения в Telegram
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(url, data=payload)

# 🧠 Основная логика
def main():
    orders_data = get_orders()

    # Проверка ошибок
    if "error" in orders_data:
        send_telegram_message(f"❌ Ошибка при получении заказов: {orders_data['error']}")
        return

    orders = orders_data.get("orders", [])
    total = len(orders)

    # ⚠️ Отладка: сколько заказов
    debug_text = f"🛒 [v3.6-debug] Получено заказов: {total}\nВремя: {formatted_time} (KZT)"
    send_telegram_message(debug_text)

    # ⚠️ Если заказов нет — отправим как и раньше
    if total == 0:
        send_telegram_message(f"❌ [v3.6] Нет заказов на сборку. Время: {formatted_time} (KZT)")
        return

    # 🧾 Отправим первые 3 заказа как json (сокращённо)
    preview = json.dumps(orders[:3], indent=2, ensure_ascii=False)
    send_telegram_message(f"<pre>{preview}</pre>")

    # ⛏️ Тут можно добавить группировку по цвету/размеру, как в старой версии
    # Например: group_and_send(orders)

if __name__ == "__main__":
    main()
