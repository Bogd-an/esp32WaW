# Костиль для віддаленого Wake on Lan

Основа: _ESP32_, _MicroPython_, _Telegram bot_

## Інсталяція:
0. Треба ESPішка (бажано з USB-UART + дрова)
1. Прошиваємо MicroPython (вау, онлайн)
  https://bipes.net.br/flash/esp-web-tool
2. Здобуваємо ключі і кидаємо в файл `secrets.py` ([EXAMPLE_secrets.py](srs/EXAMPLE_secrets.py))
3. Вивантажкємо усі srs файли на ESPішку (`EXAMPLE_secrets.py` не треба)
4. Профіт

---
Ну так, можна було взяти готовий проєкт , але свою милиці ближче до серця.

Цей цікавий (danilofuchs/esp32-telegram-wake-on-lan)[https://github.com/danilofuchs/esp32-telegram-wake-on-lan/tree/master]
