from time    import sleep
from machine import reset

from bot import run

def main():
    try:
        run()
    except Exception as e:
        print("Bot Exeception:", e)
    sleep(3)
    reset()

if __name__ == "__main__":
    main()
