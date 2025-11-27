void setup() {
	Serial.begin(9600);
}

void loop() {
	static float deg = 0.0;
	float rad = radians(deg);      // convert degrees -> radians
	float v = sin(rad);            // -1.0 .. 1.0
	Serial.println(v, 4);         // 4 decimal places
	deg += 5.0;                   // step (degrees)
	if (deg >= 360.0) deg -= 360.0;
	delay(10);
}