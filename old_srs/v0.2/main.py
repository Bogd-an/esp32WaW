import network
import urequests
import ujson  # Замість json
import time
from machine import Pin

from secrets import *


PIN_PC_BUTTON = Pin(13, Pin.OUT)
PIN_PC_LED_ON = Pin(12, Pin.IN)
LED_PIN       = Pin(2, Pin.OUT)


def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SECRET_WIFI_SSID, SECRET_WIFI_PASSWORD)
    while not wlan.isconnected():
        print("Connecting to WiFi...")
        time.sleep(0.1)
        LED_PIN.value(not LED_PIN.value())
    print("Connected to WiFi")
    print("IP address:", wlan.ifconfig()[0])

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{SECRET_TG_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text}
    response = urequests.post(url, json=payload)
    print(response.text)

def handle_new_messages(last_update_id):
    url = f"https://api.telegram.org/bot{SECRET_TG_TOKEN}/getUpdates"
    response = urequests.get(url)
    data = ujson.loads(response.text)
    messages = data.get('result', [])
    print(f'tg answer')
    for message in messages:
        update_id = message['update_id']
        print(update_id)
        if update_id > last_update_id:
            user_id = message['message']['from']['id']
            chat_id = message['message']['chat']['id']
            text = message['message']['text']

            if user_id in SECRET_ADMINS:
                if text == "/on":
                    PIN_PC_BUTTON.value(0)
                    time.sleep(0.5)
                    PIN_PC_BUTTON.value(1)
                    status = "on" if PIN_PC_LED_ON.value() == 0 else "off"  # Assuming active-low LED
                    send_telegram_message(chat_id, f"Click ON. LED status: {status}")
                elif text == "/status":
                    status = "on" if PIN_PC_LED_ON.value() == 0 else "off"  # Assuming active-low LED
                    send_telegram_message(chat_id, f"LED status: {status}")
                elif text == "/help":
                    help_message = ("This bot is designed for remotely turning on your computer.\n\n"
                                    "Available commands:\n"
                                    "/on - Presses the power button for 0.5 seconds and checks the LED status.\n"
                                    "/status - Returns the current status of the power LED.\n"
                                    "/help - Shows this help message.")
                    send_telegram_message(chat_id, help_message)
                else:
                    send_telegram_message(chat_id, "Unknown command. Type /help")
            else:
                send_telegram_message(chat_id, "Unauthorized user")

            last_update_id = update_id
            
    return last_update_id

def save_last_update_id(last_update_id):
    try:
        with open('last_update_id.json', 'w') as file:
            ujson.dump({'last_update_id': last_update_id}, file)
    except OSError as e:
        print(f"Error saving last_update_id: {e}")

def load_last_update_id():
    try:
        with open('last_update_id.json', 'r') as file:
            data = ujson.load(file)
            return data.get('last_update_id', 0)
    except OSError:
        return 0

def go():
    connect_to_wifi()
    last_update_id = load_last_update_id()
    while True:
        last_update_id = handle_new_messages(last_update_id)
        time.sleep(2)
        save_last_update_id(last_update_id)
