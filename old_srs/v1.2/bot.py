from machine import Pin
import network
import urequests
import ujson
from time import sleep
import socket

from wol import wol
from secrets import (SECRET_TG_TOKEN,  SECRET_WIFI_SSID, 
                     SECRET_TG_ADMINS, SECRET_WIFI_PASSWORD)

LED_PIN = Pin(2, Pin.OUT)

TG_URL = f"https://api.telegram.org/bot{SECRET_TG_TOKEN}"

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SECRET_WIFI_SSID, SECRET_WIFI_PASSWORD)
    while not wlan.isconnected():
        # print("Connecting to WiFi...")
        sleep(0.1)
        LED_PIN.value(not LED_PIN.value())
    # print("Connected to WiFi")
    # print("IP address:", wlan.ifconfig()[0])

def send_tg_massage(chat_id, text):
    payload = {'chat_id': chat_id, 'text': text}
    response = urequests.post(f"{TG_URL}/sendMessage", json=payload)
    response.close()
    # print(response.text)

def handle_new_messages(last_update_id):
    response = urequests.request('GET', f"{TG_URL}/getUpdates")
    response.close()
    data = ujson.loads(response.text)
    messages = data.get('result', [])
    # print(f'tg answer')
    
    prev_last_update_id = last_update_id

    for message in messages:
        update_id = message['update_id']
        if update_id > last_update_id:
            last_update_id = update_id

            user_id = message['message']['from']['id']
            chat_id = message['message']['chat']['id']
            text    = message['message']['text']

            if user_id in SECRET_TG_ADMINS:
                if text == "/wol":
                    wol()
                    send_tg_massage(chat_id, "Send WaL")
                elif text == "/help" or text == "/start":
                    send_tg_massage(chat_id, 
                        ("Bot for remotely WoL computer.\n\n"
                        "Available commands:\n"
                        "/help - Shows this help message.\n\n"
                        "/wol  - Send Wake on Lan to PC\n") )
                else:
                    send_tg_massage(chat_id, "Unknown command. Type /help")
            else:
                send_tg_massage(chat_id, "Unauthorized user")

            
    
    if(prev_last_update_id != last_update_id): save_last_update_id(last_update_id)
    return last_update_id

def save_last_update_id(last_update_id):
    with open('last_update_id.json', 'w') as file:
        ujson.dump({'last_update_id': last_update_id}, file)


def load_last_update_id():
    with open('last_update_id.json', 'r') as file:
        return ujson.load(file).get('last_update_id', 0)


def go():
    connect_to_wifi()
    last_update_id = load_last_update_id()
    while True:
        last_update_id = handle_new_messages(last_update_id)
        sleep(2)
        
