/**
 * @file    MotorDrive_double.h
 * @brief   Controls and observations of the MotorDrive double, for the test programs.
 */
#ifndef MOTORDRIVE_DOUBLE_H
#define MOTORDRIVE_DOUBLE_H

#include "Std_Types.h"

/** Motor state the double publishes from now on (0 stopped, 1 opening, 2 closing; other values for error cases). */
void MotorDriveDouble_SetApplied(uint8 direction);
/** Reversal request and window speed of the last MotorDrive_Step call, and the number of calls. */
boolean MotorDriveDouble_LastReversalRequest(void);
uint16 MotorDriveDouble_LastSpeed(void);
uint32 MotorDriveDouble_Steps(void);

#endif /* MOTORDRIVE_DOUBLE_H */
