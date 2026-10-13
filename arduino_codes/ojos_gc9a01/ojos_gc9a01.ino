#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_GC9A01A.h>

#define PIN_DC 9
#define PIN_RST 8
#define PIN_CS_L 10
#define PIN_CS_R 7

const int16_t CX = 120;
const int16_t CY = 120;
const int16_t R_SCLERA = 110;
const int16_t R_IRIS = 50;
const int16_t R_RING = 40;
const int16_t R_PUPIL = 22;
const int16_t R_SHINE = 7;
const int16_t MAX_OFF = 30;
const int16_t STEP_PX = 6;

const uint16_t C_BLACK = 0x0000;
const uint16_t C_WHITE = 0xFFFF;
const uint16_t C_IRIS_DARK = 0x0230;
const uint16_t C_IRIS = 0x04DF;

Adafruit_GC9A01A left(PIN_CS_L, PIN_DC, PIN_RST);
Adafruit_GC9A01A right(PIN_CS_R, PIN_DC, -1);

int16_t curX = 0;
int16_t curY = 0;
int16_t tgtX = 0;
int16_t tgtY = 0;

uint32_t nextLook = 0;
uint32_t nextMove = 0;
uint32_t nextBlink = 0;
uint32_t nextLid = 0;

uint8_t lidPhase = 0;
uint8_t lidStep = 0;

const uint8_t LID_STEPS = 5;
const int16_t LID_FULL = 122;

int16_t eyeOffsetX(bool isRight, int16_t ox) {
  return isRight ? (ox * 3) / 4 : ox;
}

void drawSclera(Adafruit_GC9A01A &g) {
  g.fillCircle(CX, CY, R_SCLERA, C_WHITE);
}

void drawIris(Adafruit_GC9A01A &g, int16_t x, int16_t y) {
  g.fillCircle(x, y, R_IRIS, C_IRIS_DARK);
  g.fillCircle(x, y, R_RING, C_IRIS);
  g.fillCircle(x, y, R_PUPIL, C_BLACK);
  g.fillCircle(x - 14, y - 14, R_SHINE, C_WHITE);
}

void eraseIris(Adafruit_GC9A01A &g, int16_t x, int16_t y) {
  g.fillCircle(x, y, R_IRIS + 1, C_WHITE);
}

void drawEye(Adafruit_GC9A01A &g, int16_t x, int16_t y) {
  drawSclera(g);
  drawIris(g, x, y);
}

void moveIris(Adafruit_GC9A01A &g, int16_t ox, int16_t oy, int16_t nx, int16_t ny) {
  eraseIris(g, CX + ox, CY + oy);
  drawIris(g, CX + nx, CY + ny);
}

void drawLids(Adafruit_GC9A01A &g, int16_t h) {
  g.fillRect(0, 0, 240, h, C_BLACK);
  g.fillRect(0, 240 - h, 240, h, C_BLACK);
}

void drawBoth(int16_t x, int16_t y) {
  drawEye(left, CX + eyeOffsetX(false, x), CY + y);
  drawEye(right, CX + eyeOffsetX(true, x), CY + y);
}

void setup() {
  randomSeed(analogRead(A0));
  left.begin(40000000);
  right.begin(40000000);
  left.fillScreen(C_BLACK);
  right.fillScreen(C_BLACK);
  drawBoth(0, 0);
  uint32_t now = millis();
  nextLook = now + random(1500, 3000);
  nextBlink = now + random(2000, 5000);
}

void updateLook(uint32_t now) {
  if (now >= nextLook) {
    tgtX = random(-MAX_OFF, MAX_OFF + 1);
    tgtY = random(-MAX_OFF, MAX_OFF + 1);
    nextLook = now + random(1500, 3000);
  }
  if (lidPhase != 0 || now < nextMove) return;
  if (curX == tgtX && curY == tgtY) return;
  nextMove = now + 20;
  int16_t nx = curX;
  int16_t ny = curY;
  if (tgtX > curX) nx = min((int16_t)(curX + STEP_PX), tgtX);
  else if (tgtX < curX) nx = max((int16_t)(curX - STEP_PX), tgtX);
  if (tgtY > curY) ny = min((int16_t)(curY + STEP_PX), tgtY);
  else if (tgtY < curY) ny = max((int16_t)(curY - STEP_PX), tgtY);
  moveIris(left, eyeOffsetX(false, curX), curY, eyeOffsetX(false, nx), ny);
  moveIris(right, eyeOffsetX(true, curX), curY, eyeOffsetX(true, nx), ny);
  curX = nx;
  curY = ny;
}

void updateBlink(uint32_t now) {
  if (lidPhase == 0) {
    if (now >= nextBlink) {
      lidPhase = 1;
      lidStep = 0;
      nextLid = now;
    }
    return;
  }
  if (now < nextLid) return;
  nextLid = now + 25;
  if (lidPhase == 1) {
    lidStep++;
    int16_t h = (int16_t)((long)LID_FULL * lidStep / LID_STEPS);
    drawLids(left, h);
    drawLids(right, h);
    if (lidStep >= LID_STEPS) {
      lidPhase = 2;
      nextLid = now + 60;
    }
  } else {
    drawBoth(curX, curY);
    lidPhase = 0;
    nextBlink = now + random(2000, 5000);
  }
}

void loop() {
  uint32_t now = millis();
  updateBlink(now);
  updateLook(now);
}
