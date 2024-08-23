#include <WiFi.h>
#include <UniversalTelegramBot.h>
#include <WiFiClientSecure.h>


const byte PIN_PC_BUTTON         = 13;
const byte PIN_PC_LED_ON         = 12;

WiFiClientSecure secured_client;
UniversalTelegramBot bot(SECRET_TG_TOKEN, secured_client);
unsigned long lastTimeBotRan;

String helpMessage = String("This bot is designed for remotely turning on your computer.\n\n") +
                     "Available commands:\n" +
                     "/on - Presses the power button for 0.5 seconds and checks the LED status.\n" +
                     "/status - Returns the current status of the power LED.\n" +
                     "/help - Shows this help message.";

void setup() {
  Serial.begin(115200);
  
  pinMode(PIN_PC_BUTTON, OUTPUT);
  digitalWrite(PIN_PC_BUTTON, HIGH); // Підтягування до плюса
  pinMode(PIN_PC_LED_ON, INPUT);
  pinMode(2, OUTPUT);
  
  Serial.print("Connecting to Wifi SSID ");
  Serial.print(  WiFi.begin(SECRET_WIFI_SSID, SECRET_WIFI_PASSWORD);
);
  WiFi.begin(SECRET_WIFI_SSID, SECRET_WIFI_PASSWORD);
  secured_client.setCACert(TELEGRAM_CERTIFICATE_ROOT); // Add root certificate for api.telegram.org
  while (WiFi.status() != WL_CONNECTED)
  {
    Serial.print(".");
    delay(500);
    digitalWrite(2, !digitalRead(2));
  }
  Serial.print("\nWiFi connected. IP address: ");
  Serial.println(WiFi.localIP());
  bot.sendMessage(CHAT_ID, "online", "");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED)  connectToWiFi();
  if (millis() - lastTimeBotRan > 3000) {
    lastTimeBotRan = millis();
    int numNewMessages = bot.getUpdates(bot.last_message_received + 1);

    while (numNewMessages) {
      Serial.println("got response");
      handleNewMessages(numNewMessages);
      numNewMessages = bot.getUpdates(bot.last_message_received + 1);
      digitalWrite(2, HIGH);
      delay(100);
    }
  }
  digitalWrite(2, LOW);
}

void connectToWiFi() {
  Serial.println("Connecting to WiFi: ");
  while (WiFi.status() != WL_CONNECTED) {
    delay(25);
    Serial.println("*");
    digitalWrite(2, !digitalRead(2));   
  }

  Serial.println("Connected to WiFi");
}



void handleNewMessages(int numNewMessages) {
  for (int i = 0; i < numNewMessages; i++) {
    int user_id = bot.messages[i].from_id.toInt();
    String chat_id = bot.messages[i].chat_id;

    bool isAdmin = true;
    for (int j = 0; j < SECRET_ADMNINS_COUNT; j++) {
      if (user_id == SECRET_ADMNINS[j]) break;
      isAdmin = false;
    }

    if (isAdmin) {
      String text = bot.messages[i].text;
      if (text == "/on") {
        digitalWrite(PIN_PC_BUTTON, LOW);
        delay(500);
        digitalWrite(PIN_PC_BUTTON, HIGH);
        bot.sendMessage(chat_id, String("Click ON. LED status: " + String(digitalRead(PIN_PC_LED_ON) ? "on" : "off"), ""));
      }
      else if (text == "/status") bot.sendMessage(chat_id, String("LED status: " + String(digitalRead(PIN_PC_LED_ON) ? "on" : "off"), ""));
      else if (text == "/help")   bot.sendMessage(chat_id, helpMessage, "");
      else                        bot.sendMessage(chat_id, "Unknown command. Type /help", "");
    } else bot.sendMessage(chat_id, "Unauthorized user", "");
  }
}
