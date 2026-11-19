/**
 * @file    MotorDrive.c
 * @brief   Motor actuation of the window lifter.
 *
 * Window lifter platform release 3.2.0, taken over without change (CMP-0005).
 */
#include "MotorDrive.h"
#include "BridgeOutput.h"

/* Accessed from the 5 ms task (step) and the 20 ms task (command); the tasks do not
 * preempt each other. */
static uint8 MotorDrive_CommandDirection = MOTORDRIVE_DIRECTION_STOPPED;
static uint8 MotorDrive_CommandDuty = 0u;
static uint8 MotorDrive_Applied = MOTORDRIVE_DIRECTION_STOPPED;
static uint8 MotorDrive_DrivenDirection = MOTORDRIVE_DIRECTION_STOPPED;
static uint8 MotorDrive_SoftStartCycles = 0u;
static uint8 MotorDrive_StallCycles = 0u;
static boolean MotorDrive_Stalled = FALSE;

void MotorDrive_Init(void)
{
  MotorDrive_CommandDirection = MOTORDRIVE_DIRECTION_STOPPED;
  MotorDrive_CommandDuty = 0u;
  MotorDrive_Applied = MOTORDRIVE_DIRECTION_STOPPED;
  MotorDrive_DrivenDirection = MOTORDRIVE_DIRECTION_STOPPED;
  MotorDrive_SoftStartCycles = 0u;
  MotorDrive_StallCycles = 0u;
  MotorDrive_Stalled = FALSE;
}

Std_ReturnType MotorDrive_RequestMovement(uint8 direction, uint8 duty_percent)
{
  Std_ReturnType result = E_OK;

  if ((direction > MOTORDRIVE_DIRECTION_CLOSING)
      || ((direction != MOTORDRIVE_DIRECTION_STOPPED)
          && ((duty_percent < MOTORDRIVE_DUTY_MIN_PERCENT) || (duty_percent > MOTORDRIVE_DUTY_MAX_PERCENT))))
  {
    direction = MOTORDRIVE_DIRECTION_STOPPED;
    duty_percent = 0u;
    result = E_NOT_OK;
  }
  if (direction != MotorDrive_CommandDirection)
  {
    MotorDrive_Stalled = FALSE;            /* a new command may move a stalled window again */
  }
  MotorDrive_CommandDirection = direction;
  MotorDrive_CommandDuty = duty_percent;
  return result;
}

void MotorDrive_Step(boolean reversal_request, uint16 speed_mm_s)
{
  uint8 direction = MOTORDRIVE_DIRECTION_STOPPED;
  uint8 duty = 0u;

  if (reversal_request == TRUE)
  {
    /* the reversal wins over every movement command and is not supervised for stall */
    direction = MOTORDRIVE_DIRECTION_OPENING;
    duty = MOTORDRIVE_DUTY_MAX_PERCENT;
    MotorDrive_DrivenDirection = MOTORDRIVE_DIRECTION_STOPPED;   /* a command afterwards starts softly */
  }
  else if ((MotorDrive_CommandDirection != MOTORDRIVE_DIRECTION_STOPPED) && (MotorDrive_Stalled == FALSE))
  {
    if (MotorDrive_CommandDirection != MotorDrive_DrivenDirection)
    {
      MotorDrive_SoftStartCycles = 0u;
      MotorDrive_StallCycles = 0u;
      MotorDrive_DrivenDirection = MotorDrive_CommandDirection;
    }
    MotorDrive_StallCycles = (speed_mm_s == 0u) ? (uint8)(MotorDrive_StallCycles + 1u) : 0u;
    if (MotorDrive_StallCycles >= MOTORDRIVE_STALL_CYCLES)
    {
      MotorDrive_Stalled = TRUE;
      MotorDrive_DrivenDirection = MOTORDRIVE_DIRECTION_STOPPED;
    }
    else
    {
      direction = MotorDrive_CommandDirection;
      duty = (uint8)(MOTORDRIVE_DUTY_MIN_PERCENT
                     + (((uint16)(MotorDrive_CommandDuty - MOTORDRIVE_DUTY_MIN_PERCENT) * MotorDrive_SoftStartCycles)
                        / MOTORDRIVE_SOFT_START_CYCLES));
      if (MotorDrive_SoftStartCycles < MOTORDRIVE_SOFT_START_CYCLES)
      {
        MotorDrive_SoftStartCycles++;
      }
    }
  }
  else
  {
    MotorDrive_DrivenDirection = MOTORDRIVE_DIRECTION_STOPPED;
  }

  if (BridgeOutput_Set(direction, duty) == E_OK)
  {
    MotorDrive_Applied = direction;
  }
  else
  {
    MotorDrive_Applied = MOTORDRIVE_DIRECTION_STOPPED;          /* the bridge is off; repeated next cycle */
  }
}

uint8 MotorDrive_GetAppliedDirection(void)
{
  return MotorDrive_Applied;
}

uint8 MotorDrive_GetCommandedDirection(void)
{
  return MotorDrive_CommandDirection;
}
