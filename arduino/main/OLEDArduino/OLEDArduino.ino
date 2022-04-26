
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
// The pins for I2C are defined by the Wire-library. 
// On an arduino UNO:       A4(SDA), A5(SCL)
// On an arduino MEGA 2560: 20(SDA), 21(SCL)
// On an arduino LEONARDO:   2(SDA),  3(SCL), ...
#define OLED_RESET -1 // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

#define NUMFLAKES     10 // Number of snowflakes in the animation example

#define LOGO_HEIGHT   16
#define LOGO_WIDTH    16
static const unsigned char PROGMEM logo_bmp[] =
{ 0b00000000, 0b11000000,
  0b00000001, 0b11000000,
  0b00000001, 0b11000000,
  0b00000011, 0b11100000,
  0b11110011, 0b11100000,
  0b11111110, 0b11111000,
  0b01111110, 0b11111111,
  0b00110011, 0b10011111,
  0b00011111, 0b11111100,
  0b00001101, 0b01110000,
  0b00011011, 0b10100000,
  0b00111111, 0b11100000,
  0b00111111, 0b11110000,
  0b01111100, 0b11110000,
  0b01110000, 0b01110000,
  0b00000000, 0b00110000 };
   String readString;

void setup() {
  Serial.begin(9600);
  // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }
  display.display();
  delay(1000); // Pause for 2 second
  display.clearDisplay();
  display.display();
  delay(2000);
}

void loop() {
  if (Serial.available() > 0) {
    String readString = Serial.readStringUntil('\n');
    Serial.print("You sent me: ");
    Serial.println(readString);
    if(readString.equals("waiting")){
      pleaseScanCard();
    }
    else if(readString.equals("processing")){
      Serial.print("in process");
      processing();
      delay(1000);
    }
    else if(readString.equals("granted")){
      accessGranted();
    }
    else if(readString.equals("deniedfunds")){
      Serial.println("inside if");
      accessDenied("Insufficient Funds");
    }
    else if(readString.equals("deniedcard")){
      accessDenied("Invalid card");
    }
    else if(readString.substring(0,7).equals("balance")){
      String balance = readString.substring(7);
      displayBalance(balance);
    }
  }
}

void accessGranted(void) {
  display.clearDisplay();
  display.setTextSize(2);             // Normal 1:1 pixel scale
  display.setTextColor(SSD1306_WHITE);        // Draw white text
  oledDisplayCenter("Access", 0);
  oledDisplayCenter("Granted", 1);
  display.setTextSize(1); 
  oledDisplayCenter("Pull Vehicle Forward", 3);
  display.display();
  delay(2000);
}
void displayBalance(String balance){
  display.clearDisplay();
  display.setTextSize(2); 
  display.setTextColor(SSD1306_WHITE);        // Draw white text
  oledDisplayCenter("Balance:", 0);
  oledDisplayCenter(balance, 1);
  display.display();
  delay(3000);
}
void processing(void){
  Serial.print("in method");
  display.clearDisplay();
  display.setTextSize(2); 
  display.setTextColor(SSD1306_WHITE);        // Draw white text
  oledDisplayCenter("Processing", 1);
  display.display();
  delay(2000);
}
void pleaseScanCard(void){
  display.setTextSize(2); 
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);        // Draw white text
  oledDisplayCenter("Please", 0);
  oledDisplayCenter("Scan For", 1);
  oledDisplayCenter("Access", 2);
  display.display();
  
}
void accessDenied(String reason) {
  display.clearDisplay();
  display.setTextSize(2);             // Normal 1:1 pixel scale
  display.setTextColor(SSD1306_WHITE);        // Draw white text
  oledDisplayCenter("Access", 0);
  oledDisplayCenter("Denied", 1);
  display.setTextSize(1); 
  oledDisplayCenter(reason, 3);
  display.display();
  delay(2000);
}
void oledDisplayCenter(String text, int num) {
  int16_t x1;
  int16_t y1;
  uint16_t width;
  uint16_t height;

  display.getTextBounds(text, 0, 0, &x1, &y1, &width, &height);

  // display on horizontal and vertical center
  //display.clearDisplay(); // clear display
  display.setCursor((SCREEN_WIDTH - width) / 2, ((SCREEN_HEIGHT - (2 * height)) / 2)+(height*(num)));
  display.setTextWrap(true);

  display.println(text); // text to display
}