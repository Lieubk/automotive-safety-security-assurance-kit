/**
 * @file    MotorDrive.h
 * @brief   Motor actuation of the window lifter.
 *
 * Window lifter platform release 3.2.0, taken over without change (CMP-0005).
 * Provides IFC-0004 (movement command) and IFC-0005 (motor state); uses IFC-0002
 * (window motion), IFC-0003 (detection status) and IFC-0008 (bridge output).
 * Directions: 0 stopped, 1 opening, 2 closing. One call of MotorDrive_Step() is one
 * cycle of 5 ms.
 */
#ifndef MOTORDRIVE_H
#define MOTORDRIVE_H

#include "Std_Types.h"

#define MOTORDRIVE_DIRECTION_STOPPED  ((uint8)0u)
#define MOTORDRIVE_DIRECTION_OPENING  ((uint8)1u)
#define MOTORDRIVE_DIRECTION_CLOSING  ((uint8)2u)
#define MOTORDRIVE_DUTY_MIN_PERCENT   ((uint8)30u)
#define MOTORDRIVE_DUTY_MAX_PERCENT   ((uint8)100u)
/** Cycles of the soft start: the duty cycle rises from 30 % to the commanded value in 100 ms. */
#define MOTORDRIVE_SOFT_START_CYCLES  ((uint8)20u)
/** Cycles at 0 mm/s after which a commanded movement is switched off: 250 ms. */
#define MOTORDRIVE_STALL_CYCLES       ((uint8)50u)

/** Sets the state of power-on: stopped, no command. */
void MotorDrive_Init(void);

/**
 * Movement command (IFC-0004). Stays in force until the next call.
 * @return E_OK when stored; E_NOT_OK when an argument is out of range, the command is
 *         then set to stopped.
 */
Std_ReturnType MotorDrive_RequestMovement(uint8 direction, uint8 duty_percent);

/**
 * One cycle: decides the bridge command from the reversal request (priority), the
 * movement command and the window speed, and writes it through BridgeOutput_Set.
 */
void MotorDrive_Step(boolean reversal_request, uint16 speed_mm_s);

/** Motor state (IFC-0005): the direction written to the bridge in the last cycle. */
uint8 MotorDrive_GetAppliedDirection(void);

/** Measurement access of the platform release: the direction of the movement command in force. */
uint8 MotorDrive_GetCommandedDirection(void);

#endif /* MOTORDRIVE_H */
