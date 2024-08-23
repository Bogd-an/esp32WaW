from machine import Pin
import network
import urequests
import ujson
import time
import socket

from secrets import *

LED_PIN = Pin(2, Pin.OUT)

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SECRET_WIFI_SSID, SECRET_WIFI_PASSWORD)
    while not wlan.isconnected():
        # print("Connecting to WiFi...")
        time.sleep(0.1)
        LED_PIN.value(not LED_PIN.value())
    # print("Connected to WiFi")
    # print("IP address:", wlan.ifconfig()[0])

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{SECRET_TG_TOKEN}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text}
    response = urequests.post(url, json=payload)
    response.close()
    # print(response.text)

def handle_new_messages(last_update_id):
    url = f"https://api.telegram.org/bot{SECRET_TG_TOKEN}/getUpdates"
    # response = urequests.get(url)
    response = urequests.request('GET', url)
    data = ujson.loads(response.text)
    messages = data.get('result', [])
    # print(f'tg answer')
    for message in messages:
        update_id = message['update_id']
        # print(update_id)
        if update_id > last_update_id:
            user_id = message['message']['from']['id']
            chat_id = message['message']['chat']['id']
            text = message['message']['text']

            if user_id in SECRET_ADMINS:
                if text == "/wol":
                    mac_address = SECRET_MAC_ADDRESS.replace(':', '').replace('-', '').lower()
                    mac_address_bytes = b''.join(bytes([int(mac_address[i:i+2], 16)]) for i in range(0, len(mac_address), 2))
                    magic_packet = b'\xFF' * 6 + mac_address_bytes * 16
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.sendto(magic_packet, ('255.255.255.255', 9))
                    sock.close()
                    send_telegram_message(chat_id, f"Send WaL")
                elif text == "/help":
                    help_message = ("This bot is designed for remotely turning on your computer.\n\n"
                                    "Available commands:\n"
                                    "/wol  - Send Wake on Lan to PC\n"
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
        # print(f"Error saving last_update_id: {e}")
        pass

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
