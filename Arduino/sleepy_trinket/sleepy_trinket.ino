#include <avr/sleep.h> // Needed for sleep_mode
#include <avr/wdt.h> // Needed to enable/disable watch dog timer
#include <avr/power.h> // Needed to enable/disable power modes


void enableWatchdog() {
  MCUSR = 0;
  WDTCSR = _BV(WDCE) | _BV(WDE);
  WDTCSR = _BV(WDIE) | SREG_S;
  wdt_reset();
}


void disableAdc() {
  ADCSRA = ADCSRA;
  ADCSRA = 0;
}


void gotoSleep() {
  enableWatchdog();
  disableAdc();
  power_all_disable();
  // --- start timed sleep sequence (order of events matter) --- //
  noInterrupts();
  sleep_enable();
  set_sleep_mode (SLEEP_MODE_PWR_DOWN);
  sleep_bod_disable();
  interrupts();
  Serial.println("Sleeping.");
  sleep_mode();
  // --- end timed sleep sequence (order of events matter) --- //
  // - WAKEUP FROM SLEEP - //
  wakeupFromSleep();
  Serial.println("Awake.");
}


void wakeupFromSleep() {
  Serial.println("Waking up from sleep");
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.println("Starting up.");
}

void loop() {
  // put your main code here, to run repeatedly:
  gotoSleep();
}
