
#include <Adafruit_NeoPixel.h>

#define NUMPIXELS 1

const int NEOPIXEL_ENABLE_PIN = 11;
const int NEOPIXEL_PIN  = 12;
const int LED_R_PIN = 17;
const int LED_G_PIN = 16;
const int LED_B_PIN = 25;

const int TIMER_OUT_PIN = D6;
const int DELAY_CONFIG_PIN = A0;
const int HIGH_LOW_CONFIG_PIN = D1;

const int ADC_MIN = 220;
const int ADC_MAX = 1019;
const int MAX_DELAY_MS = 20000;

Adafruit_NeoPixel pixels(NUMPIXELS, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  Serial.begin(9600);
  pixels.begin();

  pinMode(NEOPIXEL_ENABLE_PIN, OUTPUT);
  pinMode(DELAY_CONFIG_PIN, INPUT);
  pinMode(TIMER_OUT_PIN, OUTPUT);
  pinMode(HIGH_LOW_CONFIG_PIN, INPUT_PULLUP);

  pinMode(LED_R_PIN, OUTPUT);
  pinMode(LED_G_PIN, OUTPUT);
  pinMode(LED_B_PIN, OUTPUT);

  int hl_cfg = digitalReadFast(HIGH_LOW_CONFIG_PIN);
  digitalWriteFast(TIMER_OUT_PIN, hl_cfg ? LOW : HIGH);
  
  digitalWrite(NEOPIXEL_ENABLE_PIN, LOW);
  digitalWrite(LED_R_PIN, HIGH);
  digitalWrite(LED_G_PIN, HIGH);
  digitalWrite(LED_B_PIN, HIGH);

  waitForPossibleSerial();

  Serial.println("Computing delay duration");

  float delayFactor = readDelayFactor(); 
  Serial.printf("Delay factor: %f\n", delayFactor);

  int delayMs = (int) (delayFactor * (float) MAX_DELAY_MS);
  Serial.printf("Delaying: %dms\n", delayMs);
  delay(delayMs);

  Serial.println("Executing delay logic");
  digitalWrite(TIMER_OUT_PIN, hl_cfg ? HIGH : LOW);

  digitalWriteFast(NEOPIXEL_ENABLE_PIN, HIGH);
  pixels.clear();
  pixels.setPixelColor(0, hl_cfg ? pixels.Color(0, 10, 2) : pixels.Color(10, 0, 0));
  pixels.show();
}

void waitForPossibleSerial() {
  int now = millis();
  while (!Serial && (millis() - now) < 1000);
}
 
float readDelayFactor() {
  int avgSum = 0;
  for (int i = 0; i < 10; i++) {
    avgSum += analogRead(DELAY_CONFIG_PIN);
  }
  int pinValue = avgSum / 10;
  Serial.printf("Read pin value: %d\n", pinValue);
  
  pinValue = constrain(pinValue, ADC_MIN, ADC_MAX);
  Serial.printf("Clamped to: %d\n", pinValue);

  return 1.0 - (float) (pinValue - ADC_MIN) / (float) (ADC_MAX - ADC_MIN);
}
 
void loop() {}