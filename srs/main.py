import bot

import time
import machine
import sys

def main():
    try:
        bot.go()
    except Exception as e:
        print("Bot Exeception:", e)
    time.sleep(3)
    machine.reset()

if __name__ == "__main__":
    main()
