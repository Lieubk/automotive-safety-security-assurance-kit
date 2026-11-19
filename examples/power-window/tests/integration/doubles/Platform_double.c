/**
 * @file    Platform_double.c
 * @brief   Double of the basic software of the door module (CMP-0006). See Platform_double.h.
 */
#include "Platform_double.h"
#include "BridgeOutput.h"
#include "SchM_WindowPos.h"
#include "HallCapture.h"
#include "WindowPos.h"
#include "AntiPinch.h"
#include "MotorDrive.h"
#include "WindowCmd.h"

static uint32 platform_time_us = 0u;
static uint8 platform_switch_request = 0u;
static Std_ReturnType platform_bridge_result = E_OK;
static uint8 platform_bridge_direction = 0u;
static uint8 platform_bridge_duty = 0u;
static uint32 platform_bridge_calls = 0u;
static uint8 platform_inject = PLATFORM_INJECT_NONE;
static uint16 platform_inject_value = 0u;

void Platform_InjectDetectionInput(uint8 which, uint16 value)
{
  platform_inject = which;
  platform_inject_value = value;
}

void Platform_Reset(void)
{
  platform_inject = PLATFORM_INJECT_NONE;
  platform_time_us = 0u;
  platform_switch_request = 0u;
  platform_bridge_result = E_OK;
  platform_bridge_direction = 0u;
  platform_bridge_duty = 0u;
  platform_bridge_calls = 0u;
}

void Platform_Start(void)
{
  HallCapture_Init();
  WindowPos_Init();
  AntiPinch_Init();
  MotorDrive_Init();
  WindowCmd_Init();
}

void Platform_HallEdge(uint32 timestamp_us)
{
  HallCapture_OnEdge(timestamp_us);
}

void Platform_SetTime(uint32 now_us)
{
  platform_time_us = now_us;
}

void Platform_Task5ms(void)
{
  /* integration code of the task: interface values are passed between the entries */
  uint32 now_us = platform_time_us;
  uint8 applied = MotorDrive_GetAppliedDirection();      /* IFC-0005, as of the previous cycle */
  uint16 position = WINDOWPOS_POSITION_INVALID;
  uint16 speed = 0u;
  AntiPinch_StatusType status = {ANTIPINCH_STATE_IDLE, FALSE, 0u};

  (void)WindowPos_Step(now_us, applied);
  (void)WindowPos_GetPosition(&position);                 /* IFC-0002; invalid value while not referenced */
  (void)WindowPos_GetSpeed(&speed);
  (void)AntiPinch_Step((platform_inject == PLATFORM_INJECT_POSITION) ? platform_inject_value : position,
                       (platform_inject == PLATFORM_INJECT_SPEED) ? platform_inject_value : speed,
                       (platform_inject == PLATFORM_INJECT_DIRECTION) ? (uint8)platform_inject_value : applied);
  (void)AntiPinch_GetStatus(&status);                     /* IFC-0003 */
  MotorDrive_Step(status.reversal_request, speed);
}

void Platform_Task20ms(void)
{
  WindowCmd_Step(platform_switch_request);                /* IFC-0006 */
}

void Platform_SetSwitchRequest(uint8 value)
{
  platform_switch_request = value;
}

void Platform_SetBridgeResult(Std_ReturnType result)
{
  platform_bridge_result = result;
}

uint8 Platform_BridgeDirection(void)
{
  return platform_bridge_direction;
}

uint8 Platform_BridgeDuty(void)
{
  return platform_bridge_duty;
}

uint32 Platform_BridgeCalls(void)
{
  return platform_bridge_calls;
}

Std_ReturnType BridgeOutput_Set(uint8 direction, uint8 duty_percent)
{
  platform_bridge_calls++;
  platform_bridge_direction = direction;
  platform_bridge_duty = duty_percent;
  return platform_bridge_result;
}

/* Exclusive area HallData: tasks and the interrupt run one after the other on the host,
 * so there is nothing to lock. */
void SchM_Enter_WindowPos_HallData(void)
{
}

void SchM_Exit_WindowPos_HallData(void)
{
}
