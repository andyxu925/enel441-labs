// Copyright 2014 Werdroid
// Author Vladimir Kosmala
// Modified Arne Dankers 2025

#include "LS7366R.h"

#include <SPI.h>
#include <Arduino.h>

// Constructors ////////////////////////////////////////////////////////////////

LS7366R::LS7366R(unsigned char _encoder1Select, unsigned char mdr0_conf, unsigned char mdr1_conf)
{
	encoder1Select = _encoder1Select;



	pinMode(encoder1Select, OUTPUT);

	SPI.begin();

	digitalWrite(encoder1Select, LOW);
	SPI.transfer(WR | MDR0);
	SPI.transfer(mdr0_conf);
	digitalWrite(encoder1Select, HIGH);
	
	digitalWrite(encoder1Select, LOW);
	SPI.transfer(WR | MDR1);
	SPI.transfer(mdr1_conf);
	digitalWrite(encoder1Select, HIGH);

	reset();
}

// Public Methods //////////////////////////////////////////////////////////////

void LS7366R::reset()
{
	digitalWrite(encoder1Select, LOW);

	SPI.transfer(CLR | CNTR);
	digitalWrite(encoder1Select, HIGH);

}

void LS7366R::sync()
{
	long count;

	digitalWrite(encoder1Select, LOW);

	SPI.transfer(LOAD | OTR);
	digitalWrite(encoder1Select, HIGH);


	digitalWrite(encoder1Select, LOW);
	SPI.transfer(RD | OTR);
	count = SPI.transfer(0x00);
	count <<= 8;
	count |= SPI.transfer(0x00);
	count <<= 8;
	count |= SPI.transfer(0x00);
	count <<= 8;
	count |= SPI.transfer(0x00);
	digitalWrite(encoder1Select, HIGH);
	encoder1Value = count;

}

long LS7366R::encoder1()
{
	return encoder1Value;
}

