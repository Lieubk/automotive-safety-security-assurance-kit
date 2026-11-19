/**
 * @file    Platform_double.h
 * @brief   Double of the basic software of the door module (CMP-0006), for the test programs.
 *
 * Test equipment. It plays what the platform does for the application: the task
 * bodies of the execution model (VIEW-0004) in the order stated there, the capture
 * interrupt (IFC-0001), the capture timer (IFC-0007), the switch request as the
 * communication stack delivers it (IFC-0006) and the bridge output (IFC-0008). It
 * contains no logic of the application. Its configuration of tasks is a copy of
 * VIEW-0004; the customer's configuration is checked against VIEW-0004 on the control unit.
 */
#ifndef PLATFORM_DOUBLE_H
#define PLATFORM_DOUBLE_H

#include "Std_Types.h"

/** Clears the double: time 0, switch request NONE, bridge answers E_OK, no bridge call seen. */
void Platform_Reset(void);

/** OsTask_Init: the init entries of VIEW-0004 in their order. */
void Platform_Start(void);

/** Isr_HallCapture: one Hall edge with the capture time the hardware latched (IFC-0001). */
void Platform_HallEdge(uint32 timestamp_us);

/** Sets the free-running capture timer (IFC-0007). */
void Platform_SetTime(uint32 now_us);

/** OsTask_Control_5ms: reads the timer once and calls the 5 ms entries in their order. */
void Platform_Task5ms(void);

/** OsTask_Command_20ms: hands the switch request to the command logic. */
void Platform_Task20ms(void);

/** Value the communication stack delivers for the switch request: 0..3, 4..6 reserved, 7 invalid or timed out. */
void Platform_SetSwitchRequest(uint8 value);

/** Answer of the next BridgeOutput_Set calls: E_OK, or E_NOT_OK for a bridge driver fault. */
void Platform_SetBridgeResult(Std_ReturnType result);

/** Inputs of the obstacle detection the integration code can be made to pass wrongly, as a
 *  measurement and calibration tool overwrites a signal on the control unit. */
#define PLATFORM_INJECT_NONE       ((uint8)0u)
#define PLATFORM_INJECT_POSITION   ((uint8)1u)
#define PLATFORM_INJECT_SPEED      ((uint8)2u)
#define PLATFORM_INJECT_DIRECTION  ((uint8)3u)

/** From the next 5 ms cycle on, hand `value` to AntiPinch_Step instead of the input `which`; NONE ends it. */
void Platform_InjectDetectionInput(uint8 which, uint16 value);

/** Arguments of the last BridgeOutput_Set call and the number of calls since the reset. */
uint8 Platform_BridgeDirection(void);
uint8 Platform_BridgeDuty(void);
uint32 Platform_BridgeCalls(void);

#endif /* PLATFORM_DOUBLE_H */
