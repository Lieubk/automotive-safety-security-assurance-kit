/**
 * @file    WindowCmd.c
 * @brief   Command logic of the window lifter: manual movement and automatic closing.
 *
 * Window lifter platform release 3.2.1 (3.2.0 with the correction of PRB-0001), taken
 * over without change (CMP-0002).
 */
#include "WindowCmd.h"
#include "WindowPos.h"
#include "AntiPinch.h"
#include "MotorDrive.h"

#define WINDOWCMD_MODE_IDLE           ((uint8)0u)
#define WINDOWCMD_MODE_MANUAL_OPEN    ((uint8)1u)
#define WINDOWCMD_MODE_MANUAL_CLOSE   ((uint8)2u)
#define WINDOWCMD_MODE_AUTO_CLOSE     ((uint8)3u)

/* Accessed from the 20 ms task only. */
static uint8 WindowCmd_Mode = WINDOWCMD_MODE_IDLE;
static uint8 WindowCmd_LastRequest = WINDOWCMD_SWITCH_NONE;
static uint8 WindowCmd_EndStopCycles = 0u;

void WindowCmd_Init(void)
{
  WindowCmd_Mode = WINDOWCMD_MODE_IDLE;
  WindowCmd_LastRequest = WINDOWCMD_SWITCH_NONE;
  WindowCmd_EndStopCycles = 0u;
}

void WindowCmd_Step(uint8 switch_request)
{
  uint16 position = 0u;
  uint16 speed = 0u;
  AntiPinch_StatusType status = {ANTIPINCH_STATE_IDLE, FALSE, 0u};
  boolean available = (WindowPos_GetPosition(&position) == E_OK) ? TRUE : FALSE;
  uint8 request = (switch_request > WINDOWCMD_SWITCH_AUTO_CLOSE) ? WINDOWCMD_SWITCH_NONE : switch_request;
  boolean changed = (request != WindowCmd_LastRequest) ? TRUE : FALSE;
  uint8 direction = MOTORDRIVE_DIRECTION_STOPPED;

  (void)WindowPos_GetSpeed(&speed);
  (void)AntiPinch_GetStatus(&status);
  WindowCmd_LastRequest = request;

  if (WindowCmd_Mode == WINDOWCMD_MODE_AUTO_CLOSE)
  {
    /* ended by a reversal, noticed in the status or in the direction actually driven,
     * by any switch request other than NONE, or by the window standing closed */
    WindowCmd_EndStopCycles = ((available == TRUE) && (position <= WINDOWCMD_CLOSED_LIMIT) && (speed == 0u))
                              ? (uint8)(WindowCmd_EndStopCycles + 1u) : 0u;
    if ((status.reversal_request == TRUE)
        || (MotorDrive_GetAppliedDirection() == MOTORDRIVE_DIRECTION_OPENING)
        || ((changed == TRUE) && (request != WINDOWCMD_SWITCH_NONE) && (request != WINDOWCMD_SWITCH_AUTO_CLOSE))
        || (WindowCmd_EndStopCycles > WINDOWCMD_END_STOP_CYCLES))
    {
      WindowCmd_Mode = WINDOWCMD_MODE_IDLE;
    }
  }
  if (WindowCmd_Mode != WINDOWCMD_MODE_AUTO_CLOSE)
  {
    if (request == WINDOWCMD_SWITCH_OPEN)
    {
      WindowCmd_Mode = WINDOWCMD_MODE_MANUAL_OPEN;
    }
    else if (request == WINDOWCMD_SWITCH_CLOSE)
    {
      WindowCmd_Mode = WINDOWCMD_MODE_MANUAL_CLOSE;
    }
    else if ((request == WINDOWCMD_SWITCH_AUTO_CLOSE) && (changed == TRUE) && (available == TRUE))
    {
      WindowCmd_Mode = WINDOWCMD_MODE_AUTO_CLOSE;
      WindowCmd_EndStopCycles = 0u;
    }
    else
    {
      WindowCmd_Mode = WINDOWCMD_MODE_IDLE;
    }
  }

  if (WindowCmd_Mode == WINDOWCMD_MODE_MANUAL_OPEN)
  {
    direction = MOTORDRIVE_DIRECTION_OPENING;
  }
  else if ((WindowCmd_Mode == WINDOWCMD_MODE_MANUAL_CLOSE) || (WindowCmd_Mode == WINDOWCMD_MODE_AUTO_CLOSE))
  {
    direction = MOTORDRIVE_DIRECTION_CLOSING;
  }
  else
  {
    direction = MOTORDRIVE_DIRECTION_STOPPED;
  }
  (void)MotorDrive_RequestMovement(direction, WINDOWCMD_DUTY_PERCENT);
}
