/**
 * @file    MotorDrive_double.c
 * @brief   Double of MotorDrive (CMP-0005) for integration steps that do not integrate it.
 *
 * Test equipment. Same functions as reused/motordrive/MotorDrive.h. It publishes a
 * prepared motor state (IFC-0005) and records what the 5 ms task hands to it: the
 * reversal request (IFC-0003) and the window speed (IFC-0002). No logic of MotorDrive.
 */
#include "MotorDrive.h"
#include "MotorDrive_double.h"

static uint8 double_applied = MOTORDRIVE_DIRECTION_STOPPED;
static boolean double_reversal_request = FALSE;
static uint16 double_speed = 0u;
static uint32 double_steps = 0u;

void MotorDriveDouble_SetApplied(uint8 direction)
{
  double_applied = direction;
}

boolean MotorDriveDouble_LastReversalRequest(void)
{
  return double_reversal_request;
}

uint16 MotorDriveDouble_LastSpeed(void)
{
  return double_speed;
}

uint32 MotorDriveDouble_Steps(void)
{
  return double_steps;
}

void MotorDrive_Init(void)
{
  double_applied = MOTORDRIVE_DIRECTION_STOPPED;
  double_reversal_request = FALSE;
  double_speed = 0u;
  double_steps = 0u;
}

Std_ReturnType MotorDrive_RequestMovement(uint8 direction, uint8 duty_percent)
{
  (void)direction;
  (void)duty_percent;
  return E_OK;
}

void MotorDrive_Step(boolean reversal_request, uint16 speed_mm_s)
{
  double_reversal_request = reversal_request;
  double_speed = speed_mm_s;
  double_steps++;
}

uint8 MotorDrive_GetAppliedDirection(void)
{
  return double_applied;
}

uint8 MotorDrive_GetCommandedDirection(void)
{
  return MOTORDRIVE_DIRECTION_STOPPED;
}
