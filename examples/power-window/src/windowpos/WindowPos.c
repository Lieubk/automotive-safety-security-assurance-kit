/**
 * @file    WindowPos.c
 * @brief   Window position and window speed from the Hall pulse data.
 *
 * Design item: UNT-0002. See WindowPos.h for the interface contract.
 */

/*==============================================================================
 * INCLUDES
 *============================================================================*/
#include "WindowPos.h"
#include "HallCapture.h"

/*==============================================================================
 * MACROS
 *============================================================================*/

/** Glass travel per pulse times the time scale: 0.5 mm per pulse = 500000 mm/s * us. */
#define WINDOWPOS_SPEED_NUMERATOR       ((uint32)500000u)
/** Pulse period or pulse-free time from which the window counts as standing: 50000 us = 50 ms (10 mm/s). */
#define WINDOWPOS_STANDSTILL_US         ((uint32)50000u)
/** Pulse period at and below which the speed is limited to the maximum: 1000 us (500 mm/s). */
#define WINDOWPOS_FASTEST_PERIOD_US     ((uint32)1000u)
/** Time differences above this value mean "edge newer than the time passed in": half the timer range. */
#define WINDOWPOS_TIME_HALF_RANGE_US    ((uint32)0x7FFFFFFFu)
/** Pulses needed after a standstill before the pulse period is used: 2 pulses. */
#define WINDOWPOS_PULSES_FOR_PERIOD     ((uint8)2u)
/** Calls with opening drive at 0 mm/s after which the open end stop is assumed: 40 calls = 200 ms. */
#define WINDOWPOS_REFERENCE_CYCLES      ((uint8)40u)

/*==============================================================================
 * FILE-LOCAL VARIABLES
 *============================================================================*/

/* All variables are accessed from the 5 ms task only (see UNT-0002, data). */

/** Window opening in counts of 0.5 mm, 0..WINDOWPOS_POSITION_MAX; meaningful only while valid. */
static uint16 WindowPos_Position = 0u;

/** TRUE once the position has been referenced at the fully open end stop. */
static boolean WindowPos_PositionValid = FALSE;

/** Window speed in mm/s, 0 or 10..WINDOWPOS_SPEED_MAX_MM_S. */
static uint16 WindowPos_SpeedMmS = 0u;

/** Pulse counter value of the capture unit at the last successful step. */
static uint16 WindowPos_LastPulseCount = 0u;

/** Last drive direction other than stopped; WINDOWPOS_DIRECTION_STOPPED until the drive has moved. */
static WindowPos_DirectionType WindowPos_CountDirection = WINDOWPOS_DIRECTION_STOPPED;

/** Pulses received since the last standstill, 0..WINDOWPOS_PULSES_FOR_PERIOD, saturating. */
static uint8 WindowPos_PulsesSinceStandstill = 0u;

/** Consecutive calls with opening drive at 0 mm/s, 0..WINDOWPOS_REFERENCE_CYCLES, saturating. */
static uint8 WindowPos_StallCycles = 0u;

/*==============================================================================
 * PROTOTYPES OF FILE-LOCAL FUNCTIONS
 *============================================================================*/
static void WindowPos_UpdatePosition(uint16 new_pulses);
static void WindowPos_UpdateSpeed(const HallCapture_SnapshotType *snapshot, uint32 now_us, uint16 new_pulses);
static uint16 WindowPos_SpeedFromPeriod(uint32 period_us);
static void WindowPos_UpdateReference(WindowPos_DirectionType direction);

/*==============================================================================
 * FUNCTION DEFINITIONS
 *============================================================================*/

void WindowPos_Init(void)
{
  WindowPos_Position = 0u;
  WindowPos_PositionValid = FALSE;
  WindowPos_SpeedMmS = 0u;
  WindowPos_LastPulseCount = 0u;
  WindowPos_CountDirection = WINDOWPOS_DIRECTION_STOPPED;
  WindowPos_PulsesSinceStandstill = 0u;
  WindowPos_StallCycles = 0u;
}

Std_ReturnType WindowPos_Step(uint32 now_us, WindowPos_DirectionType direction)
{
  Std_ReturnType result = E_NOT_OK;
  HallCapture_SnapshotType snapshot;
  uint16 new_pulses;

  if (direction <= WINDOWPOS_DIRECTION_CLOSING)
  {
    if (HallCapture_GetSnapshot(&snapshot) == E_OK)
    {
      /* Unsigned subtraction: correct across a wrap of the pulse counter. */
      new_pulses = (uint16)(snapshot.pulse_count - WindowPos_LastPulseCount);
      WindowPos_LastPulseCount = snapshot.pulse_count;

      if (direction != WINDOWPOS_DIRECTION_STOPPED)
      {
        WindowPos_CountDirection = direction;
      }

      WindowPos_UpdatePosition(new_pulses);
      WindowPos_UpdateSpeed(&snapshot, now_us, new_pulses);
      WindowPos_UpdateReference(direction);
      result = E_OK;
    }
  }

  return result;
}

Std_ReturnType WindowPos_GetPosition(uint16 *position)
{
  Std_ReturnType result = E_NOT_OK;

  if (position != NULL_PTR)
  {
    if (WindowPos_PositionValid == TRUE)
    {
      *position = WindowPos_Position;
      result = E_OK;
    }
    else
    {
      *position = WINDOWPOS_POSITION_INVALID;
    }
  }

  return result;
}

Std_ReturnType WindowPos_GetSpeed(uint16 *speed_mm_s)
{
  Std_ReturnType result = E_NOT_OK;

  if (speed_mm_s != NULL_PTR)
  {
    *speed_mm_s = WindowPos_SpeedMmS;
    result = E_OK;
  }

  return result;
}

/**
 * @brief  Move the position by the pulses of this cycle, limited to the travel range.
 *
 * A valid position implies a known counting direction, because referencing
 * happens only while the drive is opening.
 *
 * @param[in]  new_pulses  Pulses accepted since the last successful step, 0..65535.
 */
static void WindowPos_UpdatePosition(uint16 new_pulses)
{
  uint32 opened;

  if (WindowPos_PositionValid == TRUE)
  {
    if (WindowPos_CountDirection == WINDOWPOS_DIRECTION_CLOSING)
    {
      if (new_pulses >= WindowPos_Position)
      {
        WindowPos_Position = 0u;
      }
      else
      {
        WindowPos_Position = (uint16)(WindowPos_Position - new_pulses);
      }
    }
    else
    {
      opened = (uint32)WindowPos_Position + (uint32)new_pulses;
      if (opened > WINDOWPOS_POSITION_MAX)
      {
        WindowPos_Position = WINDOWPOS_POSITION_MAX;
      }
      else
      {
        WindowPos_Position = (uint16)opened;
      }
    }
  }
}

/**
 * @brief  Derive the speed from the pulse period and the time since the last pulse.
 *
 * @param[in]  snapshot    Pulse data of this cycle; never a null pointer.
 * @param[in]  now_us      Current value of the capture time base in us.
 * @param[in]  new_pulses  Pulses accepted since the last successful step, 0..65535.
 */
static void WindowPos_UpdateSpeed(const HallCapture_SnapshotType *snapshot, uint32 now_us, uint16 new_pulses)
{
  uint32 elapsed_us = now_us - snapshot->last_edge_us;
  uint32 effective_us;
  uint16 speed_mm_s = 0u;

  if (elapsed_us > WINDOWPOS_TIME_HALF_RANGE_US)
  {
    /* The last edge was captured after now_us had been sampled. */
    elapsed_us = 0u;
  }

  if (new_pulses >= WINDOWPOS_PULSES_FOR_PERIOD)
  {
    WindowPos_PulsesSinceStandstill = WINDOWPOS_PULSES_FOR_PERIOD;
  }
  else if ((new_pulses == 1u) && (WindowPos_PulsesSinceStandstill < WINDOWPOS_PULSES_FOR_PERIOD))
  {
    WindowPos_PulsesSinceStandstill = (uint8)(WindowPos_PulsesSinceStandstill + 1u);
  }
  else
  {
    /* No new pulse, or enough pulses counted already. */
  }

  if (WindowPos_PulsesSinceStandstill > 0u)
  {
    if (elapsed_us >= WINDOWPOS_STANDSTILL_US)
    {
      /* Standstill: the period of the next pulse spans the pause and is not used. */
      WindowPos_PulsesSinceStandstill = 0u;
    }
    else if (WindowPos_PulsesSinceStandstill >= WINDOWPOS_PULSES_FOR_PERIOD)
    {
      /* Without a new pulse the window cannot be faster than one pulse per elapsed time. */
      effective_us = (snapshot->period_us > elapsed_us) ? snapshot->period_us : elapsed_us;
      speed_mm_s = WindowPos_SpeedFromPeriod(effective_us);
    }
    else
    {
      /* First pulse after a standstill: no trustworthy period yet. */
    }
  }

  WindowPos_SpeedMmS = speed_mm_s;
}

/**
 * @brief  Convert a pulse period into a speed.
 *
 * @param[in]  period_us  Pulse period, 0..4294967295 us.
 * @return     Speed in mm/s: 0 for 50000 us and longer, 500 for 1000 us and
 *             shorter, otherwise 500000 / period_us rounded down (10..499).
 */
static uint16 WindowPos_SpeedFromPeriod(uint32 period_us)
{
  uint16 speed_mm_s;

  if (period_us >= WINDOWPOS_STANDSTILL_US)
  {
    speed_mm_s = 0u;
  }
  else if (period_us <= WINDOWPOS_FASTEST_PERIOD_US)
  {
    speed_mm_s = WINDOWPOS_SPEED_MAX_MM_S;
  }
  else
  {
    speed_mm_s = (uint16)(WINDOWPOS_SPEED_NUMERATOR / period_us);
  }

  return speed_mm_s;
}

/**
 * @brief  Reference the position when the opening drive rests on the end stop.
 *
 * @param[in]  direction  Applied drive direction of this cycle, 0..2.
 */
static void WindowPos_UpdateReference(WindowPos_DirectionType direction)
{
  if ((direction == WINDOWPOS_DIRECTION_OPENING) && (WindowPos_SpeedMmS == 0u))
  {
    if (WindowPos_StallCycles < WINDOWPOS_REFERENCE_CYCLES)
    {
      WindowPos_StallCycles = (uint8)(WindowPos_StallCycles + 1u);
    }

    if (WindowPos_StallCycles >= WINDOWPOS_REFERENCE_CYCLES)
    {
      WindowPos_Position = WINDOWPOS_POSITION_MAX;
      WindowPos_PositionValid = TRUE;
    }
  }
  else
  {
    WindowPos_StallCycles = 0u;
  }
}
