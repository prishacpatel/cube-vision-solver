/*
  Rubik's Cube robot: one stepper motor per face (U R F D L B), driven by A4988 / DRV8825 drivers.

  Protocol (USB serial, 115200 baud): the PC sends one line of moves, e.g.  R U' F2 D
  The Arduino turns each face, then replies  DONE  (or  ERR <token>  if it can't parse a move).

  Wiring (Arduino Uno):  STEP pins 2,4,6,8,10,12   DIR pins 3,5,7,9,11,13
  All drivers share ENABLE (tie low) and a 12 V supply with a 100 uF capacitor across it.
  Set the microstep jumpers on the drivers to match MICROSTEPS below.

  Mechanics: each motor shaft needs a 3D-printed cross-shaped adapter that holds one face center.
  Many open designs exist (search "6 stepper rubik's cube robot"); adjust the pins/constants to match.
*/

const int STEP_PIN[6] = {2, 4, 6, 8, 10, 12};   // order: U R F D L B
const int DIR_PIN[6]  = {3, 5, 7, 9, 11, 13};
const char FACES[6]   = {'U', 'R', 'F', 'D', 'L', 'B'};

// Flip an entry if that motor turns the wrong way (clockwise as seen looking AT the face).
const bool INVERT_DIR[6] = {false, false, false, false, false, false};

const int  MOTOR_STEPS_PER_REV = 200;   // 1.8 degree stepper
const int  MICROSTEPS          = 8;
const int  STEP_DELAY_US       = 600;   // lower = faster; raise it if motors stall
const long QUARTER_TURN        = (long)MOTOR_STEPS_PER_REV * MICROSTEPS / 4;

int faceIndex(char c) {
  for (int i = 0; i < 6; i++) if (FACES[i] == c) return i;
  return -1;
}

void turn(int face, int quarters, bool clockwise) {
  bool dir = clockwise ^ INVERT_DIR[face];
  digitalWrite(DIR_PIN[face], dir ? HIGH : LOW);
  delayMicroseconds(5);
  long steps = QUARTER_TURN * quarters;
  for (long s = 0; s < steps; s++) {
    digitalWrite(STEP_PIN[face], HIGH);
    delayMicroseconds(STEP_DELAY_US);
    digitalWrite(STEP_PIN[face], LOW);
    delayMicroseconds(STEP_DELAY_US);
  }
  delay(120);   // let the cube settle between moves
}

// Returns false if the token is not a valid move.
bool runMove(const String& tok) {
  if (tok.length() == 0 || tok.length() > 2) return false;
  int f = faceIndex(tok[0]);
  if (f < 0) return false;
  int quarters = 1;
  bool clockwise = true;
  if (tok.length() == 2) {
    if (tok[1] == '\'') clockwise = false;
    else if (tok[1] == '2') quarters = 2;
    else return false;
  }
  turn(f, quarters, clockwise);
  return true;
}

void setup() {
  for (int i = 0; i < 6; i++) {
    pinMode(STEP_PIN[i], OUTPUT);
    pinMode(DIR_PIN[i], OUTPUT);
  }
  Serial.begin(115200);
}

void loop() {
  if (!Serial.available()) return;
  String line = Serial.readStringUntil('\n');
  line.trim();
  int start = 0;
  while (start < (int)line.length()) {
    int sp = line.indexOf(' ', start);
    if (sp < 0) sp = line.length();
    String tok = line.substring(start, sp);
    if (tok.length() && !runMove(tok)) {
      Serial.print("ERR ");
      Serial.println(tok);
      return;
    }
    start = sp + 1;
  }
  Serial.println("DONE");
}
