// Copyright 2014 Werdroid
// Author Vladimir Kosmala
// Modified Arne Dankers 2025

#ifndef LS7366R_h
#define LS7366R_h

#define CLR B00000000
#define RD B01000000
#define WR B10000000
#define LOAD B11000000

#define MDR0 B00001000
#define MDR1 B00010000
#define DTR B00011000
#define CNTR B00100000
#define OTR B00101000
#define STR B00110000

// filter factor 1
// async index
// no index
// free-running
// 4x quadrature
#define MDR0_CONF B00000011

// no flag
// enabled
// 32 bits
#define MDR1_CONF B00000000

class LS7366R {
	public:
		unsigned char encoder1Select;

		long encoder1Value;

		LS7366R(unsigned char _encoder1Select, unsigned char mdr0_conf, unsigned char mdr1_conf);
		void reset();
		void sync();
		long encoder1();


};

#endif