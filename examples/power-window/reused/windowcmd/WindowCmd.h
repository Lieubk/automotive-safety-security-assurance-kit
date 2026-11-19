/**
 * @file    WindowCmd.h
 * @brief   Command logic of the window lifter: manual movement and automatic closing.
 *
 * Window lifter platform release 3.2.0, taken over without change (CMP-0002).
 * Uses IFC-0002 (window motion), IFC-0003 (detection status), IFC-0004 (movement
 * command), IFC-0005 (motor state) and IFC-0006 (switch request). One call of
 * WindowCmd_Step() is one cycle of 20 ms.
 */
#ifndef WINDOWCMD_H
#define WINDOWCMD_H

#include "Std_Types.h"

#define WINDOWCMD_SWITCH_NONE         ((uint8)0u)
#define WINDOWCMD_SWITCH_OPEN         ((uint8)1u)
#define WINDOWCMD_SWITCH_CLOSE        ((uint8)2u)
#define WINDOWCMD_SWITCH_AUTO_CLOSE   ((uint8)3u)
/** Window opening at or below which an automatic closing movement may end: 5 mm in counts of 0.5 mm. */
#define WINDOWCMD_CLOSED_LIMIT        ((uint16)10u)
/** Cycles after the first one at 0 mm/s inside the closed limit that end an automatic closing movement: 200 ms. */
#define WINDOWCMD_END_STOP_CYCLES     ((uint8)10u)
/** Duty cycle of every movement command. */
#define WINDOWCMD_DUTY_PERCENT        ((uint8)100u)

/** Sets the state of power-on: no movement. */
void WindowCmd_Init(void);

/** One cycle: turns the switch request (IFC-0006, as delivered) into the movement command. */
void WindowCmd_Step(uint8 switch_request);

#endif /* WINDOWCMD_H */
