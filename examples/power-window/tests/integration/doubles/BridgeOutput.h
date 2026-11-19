/**
 * @file    BridgeOutput.h
 * @brief   Stand-in for the header of the bridge output service of the platform (IFC-0008).
 *
 * Test equipment. The real header belongs to the basic software of the customer
 * (CMP-0006); this one declares only what the application uses, as IFC-0008 states it.
 */
#ifndef BRIDGEOUTPUT_H
#define BRIDGEOUTPUT_H

#include "Std_Types.h"

/** Writes direction (0 off, 1 opening, 2 closing) and duty cycle in percent to the bridge driver. */
Std_ReturnType BridgeOutput_Set(uint8 direction, uint8 duty_percent);

#endif /* BRIDGEOUTPUT_H */
