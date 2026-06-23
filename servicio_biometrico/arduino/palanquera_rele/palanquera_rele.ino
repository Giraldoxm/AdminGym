/*
 * JainSportBox — Control de palanquera por relé
 * Arduino UNO + módulo relé SRD-05VDC-SL-C (activo-bajo)
 *
 * Protocolo serial (9600 baud, line ending \n):
 *   PC -> Arduino : 'A' = abrir palanquera (pulso de RELE_MS ms)
 *                   'P' = ping (responde con la firma, usado para autodetección)
 *   Arduino -> PC : "JSB-PALANQUERA READY"  al arrancar
 *                   "JSB-PALANQUERA OK"     en respuesta a 'P'
 *
 * El Arduino es el dueño del tiempo de pulso: una vez recibido 'A' mantiene el
 * relé activado RELE_MS y lo cierra solo. Si el PC se reinicia o el bridge se cae
 * a mitad de pulso, la palanquera igual vuelve a su estado de reposo (cerrada).
 *
 * Cableado (módulo de 1 canal):
 *   VCC  -> 5V        GND -> GND        IN -> PIN_RELE (D7)
 *   La palanquera se conecta a los bornes NO/COM (normalmente abierto) del relé,
 *   de modo que el "pulso" cierre el contacto que dispara el solenoide/motor.
 */

const int  PIN_RELE = 7;        // pin de señal (IN) del módulo de relé
const long RELE_MS  = 5000;     // tiempo que la palanquera queda abierta (ms)

// Módulo SRD-05VDC-SL-C activo-bajo: LOW activa el relé. Si tu módulo fuera
// activo-alto, intercambiá estos dos valores (RELE_ON = HIGH, RELE_OFF = LOW).
const int  RELE_ON  = LOW;      // relé activado  -> palanquera abierta
const int  RELE_OFF = HIGH;     // relé en reposo -> palanquera cerrada

unsigned long cierreEn = 0;     // millis() en que debe cerrarse
bool          abierta  = false;

void setup() {
  pinMode(PIN_RELE, OUTPUT);
  digitalWrite(PIN_RELE, RELE_OFF);   // arrancar siempre cerrada
  Serial.begin(9600);
  Serial.println("JSB-PALANQUERA READY");
}

void abrirPalanquera() {
  digitalWrite(PIN_RELE, RELE_ON);
  abierta  = true;
  cierreEn = millis() + RELE_MS;      // re-arma el temporizador si ya estaba abierta
}

void loop() {
  // Cierre no bloqueante: seguimos atendiendo comandos mientras está abierta.
  // El cast a long maneja el wraparound de millis() para diferencias cortas.
  if (abierta && (long)(millis() - cierreEn) >= 0) {
    digitalWrite(PIN_RELE, RELE_OFF);
    abierta = false;
  }

  if (Serial.available() > 0) {
    char c = Serial.read();
    if (c == 'A') {
      abrirPalanquera();
    } else if (c == 'P') {
      Serial.println("JSB-PALANQUERA OK");
    }
  }
}
