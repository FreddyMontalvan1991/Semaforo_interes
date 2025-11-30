int tVerde = 0;
int tAmarillo = 0;
int tRojo = 0;

void setup() {
  pinMode(8, OUTPUT); // Rojo
  pinMode(9, OUTPUT); // Amarillo
  pinMode(10, OUTPUT); // Verde

  // Apagar todo por defecto
  digitalWrite(8, LOW);
  digitalWrite(9, LOW);
  digitalWrite(10, LOW);

  Serial.begin(9600);
}

void loop() {

  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    data.trim();

    if (data == "STOP") {
      // Apagar LEDs
      digitalWrite(8, LOW);
      digitalWrite(9, LOW);
      digitalWrite(10, LOW);
      return;
    }

    int p1 = data.indexOf(',');
    int p2 = data.lastIndexOf(',');

    if (p1 > 0 && p2 > p1) {
      tVerde = data.substring(0, p1).toInt();
      tAmarillo = data.substring(p1 + 1, p2).toInt();
      tRojo = data.substring(p2 + 1).toInt();
    }
  }

  if (tVerde > 0 && tAmarillo > 0 && tRojo > 0) {

    // Verde
    digitalWrite(10, HIGH);
    digitalWrite(9, LOW);
    digitalWrite(8, LOW);
    delay(tVerde * 1000);

    // Amarillo
    digitalWrite(10, LOW);
    digitalWrite(9, HIGH);
    digitalWrite(8, LOW);
    delay(tAmarillo * 1000);

    // Rojo
    digitalWrite(10, LOW);
    digitalWrite(9, LOW);
    digitalWrite(8, HIGH);
    delay(tRojo * 1000);
  }
}
