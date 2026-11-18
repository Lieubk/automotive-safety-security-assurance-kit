/**
 * @file    AntiPinch.c
 * @brief   Detection of an obstacle in the path of the closing window.
 *
 * Design item: UNT-0003. See AntiPinch.h for the interface contract.
 */

/*==============================================================================
 * INCLUDES
 *============================================================================*/
#include "AntiPinch.h"

/*==============================================================================
 * MACROS
 *============================================================================*/

/** The reference speed is stored with 4 fractional bits: 1 count = 1/16 mm/s. */
#define ANTIPINCH_REFERENCE_SHIFT    (4u)
/** Lower limit of the stored reference speed: 50 mm/s = 800 counts of 1/16 mm/s. */
#define ANTIPINCH_REFERENCE_MIN_Q4   ((uint16)800u)

/*==============================================================================
 * FILE-LOCAL VARIABLES
 *============================================================================*/

/* All variables are accessed from the 5 ms task only (see UNT-0003, data). */

/** Detector state, ANTIPINCH_STATE_IDLE..ANTIPINCH_STATE_REVERSING. */
static AntiPinch_StateType AntiPinch_State = ANTIPINCH_STATE_IDLE;

/** Reference speed in 1/16 mm/s, 800..8015 in state MONITORING, 0 otherwise. */
static uint16 AntiPinch_ReferenceQ4 = 0u;

/** Closing cycles counted in state SETTLING, 1..ANTIPINCH_SETTLING_CYCLES. */
static uint8 AntiPinch_SettlingCycles = 0u;

/** Consecutive cycles with a speed drop inside the protected zone, 0..ANTIPINCH_CONFIRM_CYCLES. */
static uint8 AntiPinch_DropCycles = 0u;

/** Cycles spent in state REVERSING, 0..ANTIPINCH_REVERSAL_CYCLES. */
static uint16 AntiPinch_ReversalCycles = 0u;

/** Position at which the reversal ends, 0..960, or ANTIPINCH_POSITION_INVALID when only the time limit applies. */
static uint16 AntiPinch_ReversalTarget = ANTIPINCH_POSITION_INVALID;

/*==============================================================================
 * PROTOTYPES OF FILE-LOCAL FUNCTIONS
 *============================================================================*/
static boolean AntiPinch_InputsValid(uint16 position, uint16 speed_mm_s, AntiPinch_MotionType motion);
static void AntiPinch_EnterIdle(void);
static void AntiPinch_StartReversal(uint16 position);
static void AntiPinch_StepIdle(AntiPinch_MotionType motion);
static void AntiPinch_StepSettling(uint16 speed_mm_s, AntiPinch_MotionType motion);
static void AntiPinch_StepMonitoring(uint16 position, uint16 speed_mm_s, AntiPinch_MotionType motion);
static void AntiPinch_StepReversing(uint16 position);
static void AntiPinch_StepInvalid(AntiPinch_MotionType motion);

/*==============================================================================
 * FUNCTION DEFINITIONS
 *============================================================================*/

void AntiPinch_Init(void)
{
  AntiPinch_EnterIdle();
}

Std_ReturnType AntiPinch_Step(uint16 position, uint16 speed_mm_s, AntiPinch_MotionType motion)
{
  Std_ReturnType result;

  if (AntiPinch_InputsValid(position, speed_mm_s, motion) == TRUE)
  {
    result = E_OK;

    switch (AntiPinch_State)
    {
      case ANTIPINCH_STATE_SETTLING:
        AntiPinch_StepSettling(speed_mm_s, motion);
        break;

      case ANTIPINCH_STATE_MONITORING:
        AntiPinch_StepMonitoring(position, speed_mm_s, motion);
        break;

      case ANTIPINCH_STATE_REVERSING:
        AntiPinch_StepReversing(position);
        break;

      default:
        /* ANTIPINCH_STATE_IDLE; a corrupted state value is treated the same way. */
        AntiPinch_StepIdle(motion);
        break;
    }
  }
  else
  {
    result = E_NOT_OK;
    AntiPinch_StepInvalid(motion);
  }

  return result;
}

Std_ReturnType AntiPinch_GetStatus(AntiPinch_StatusType *status)
{
  Std_ReturnType result = E_NOT_OK;

  if (status != NULL_PTR)
  {
    status->state = AntiPinch_State;
    status->reversal_request = (AntiPinch_State == ANTIPINCH_STATE_REVERSING) ? TRUE : FALSE;
    status->reference_speed_mm_s = (uint16)(AntiPinch_ReferenceQ4 >> ANTIPINCH_REFERENCE_SHIFT);
    result = E_OK;
  }

  return result;
}

/**
 * @brief  Check the arguments of AntiPinch_Step() against their ranges.
 *
 * @param[in]  position    Window opening as passed to AntiPinch_Step().
 * @param[in]  speed_mm_s  Window speed as passed to AntiPinch_Step().
 * @param[in]  motion      Drive direction as passed to AntiPinch_Step().
 * @return     TRUE when all three values are in range, FALSE otherwise.
 */
static boolean AntiPinch_InputsValid(uint16 position, uint16 speed_mm_s, AntiPinch_MotionType motion)
{
  boolean valid = TRUE;

  if ((position > ANTIPINCH_POSITION_MAX) && (position != ANTIPINCH_POSITION_INVALID))
  {
    valid = FALSE;
  }

  if (speed_mm_s > ANTIPINCH_SPEED_MAX_MM_S)
  {
    valid = FALSE;
  }

  if (motion > ANTIPINCH_MOTION_CLOSING)
  {
    valid = FALSE;
  }

  return valid;
}

/**
 * @brief  Enter state IDLE and clear everything that belongs to a supervised movement.
 */
static void AntiPinch_EnterIdle(void)
{
  AntiPinch_State = ANTIPINCH_STATE_IDLE;
  AntiPinch_ReferenceQ4 = 0u;
  AntiPinch_SettlingCycles = 0u;
  AntiPinch_DropCycles = 0u;
  AntiPinch_ReversalCycles = 0u;
  AntiPinch_ReversalTarget = ANTIPINCH_POSITION_INVALID;
}

/**
 * @brief  Enter state REVERSING and fix where the reversal ends.
 *
 * @param[in]  position  Position at detection, 0..960, or any larger value
 *                       when the position is unknown; the reversal is then
 *                       limited by time only.
 */
static void AntiPinch_StartReversal(uint16 position)
{
  uint16 target = ANTIPINCH_POSITION_INVALID;

  if (position <= ANTIPINCH_POSITION_MAX)
  {
    target = (uint16)(position + ANTIPINCH_REVERSAL_TRAVEL);
    if (target > ANTIPINCH_POSITION_MAX)
    {
      target = ANTIPINCH_POSITION_MAX;
    }
  }

  AntiPinch_State = ANTIPINCH_STATE_REVERSING;
  AntiPinch_ReferenceQ4 = 0u;
  AntiPinch_SettlingCycles = 0u;
  AntiPinch_DropCycles = 0u;
  AntiPinch_ReversalCycles = 0u;
  AntiPinch_ReversalTarget = target;
}

/**
 * @brief  One cycle in state IDLE: wait for a closing drive.
 *
 * @param[in]  motion  Applied drive direction, 0..2.
 */
static void AntiPinch_StepIdle(AntiPinch_MotionType motion)
{
  if (motion == ANTIPINCH_MOTION_CLOSING)
  {
    AntiPinch_State = ANTIPINCH_STATE_SETTLING;
    AntiPinch_SettlingCycles = 1u;
  }
  else
  {
    AntiPinch_EnterIdle();
  }
}

/**
 * @brief  One cycle in state SETTLING: wait until the drive has accelerated.
 *
 * @param[in]  speed_mm_s  Window speed, 0..500 mm/s.
 * @param[in]  motion      Applied drive direction, 0..2.
 */
static void AntiPinch_StepSettling(uint16 speed_mm_s, AntiPinch_MotionType motion)
{
  uint16 reference_mm_s;

  if (motion != ANTIPINCH_MOTION_CLOSING)
  {
    AntiPinch_EnterIdle();
  }
  else
  {
    AntiPinch_SettlingCycles = (uint8)(AntiPinch_SettlingCycles + 1u);

    if (AntiPinch_SettlingCycles >= ANTIPINCH_SETTLING_CYCLES)
    {
      reference_mm_s = speed_mm_s;
      if (reference_mm_s < ANTIPINCH_REFERENCE_MIN_MM_S)
      {
        reference_mm_s = ANTIPINCH_REFERENCE_MIN_MM_S;
      }

      AntiPinch_ReferenceQ4 = (uint16)(reference_mm_s << ANTIPINCH_REFERENCE_SHIFT);
      AntiPinch_DropCycles = 0u;
      AntiPinch_State = ANTIPINCH_STATE_MONITORING;
    }
  }
}

/**
 * @brief  One cycle in state MONITORING: compare the speed with the reference speed.
 *
 * The position value for "not referenced" lies above the zone limit, so an
 * unknown position is treated as inside the protected zone.
 *
 * @param[in]  position    Window opening, 0..960 counts, or ANTIPINCH_POSITION_INVALID.
 * @param[in]  speed_mm_s  Window speed, 0..500 mm/s.
 * @param[in]  motion      Applied drive direction, 0..2.
 */
static void AntiPinch_StepMonitoring(uint16 position, uint16 speed_mm_s, AntiPinch_MotionType motion)
{
  uint16 reference_mm_s = (uint16)(AntiPinch_ReferenceQ4 >> ANTIPINCH_REFERENCE_SHIFT);
  uint16 filtered_q4;

  if (motion != ANTIPINCH_MOTION_CLOSING)
  {
    AntiPinch_EnterIdle();
  }
  else if ((uint16)(speed_mm_s + ANTIPINCH_DROP_THRESHOLD_MM_S) < reference_mm_s)
  {
    /* Speed drop pending: the reference speed is held. */
    if (position > ANTIPINCH_ZONE_LIMIT)
    {
      AntiPinch_DropCycles = (uint8)(AntiPinch_DropCycles + 1u);
      if (AntiPinch_DropCycles >= ANTIPINCH_CONFIRM_CYCLES)
      {
        AntiPinch_StartReversal(position);
      }
    }
    else
    {
      /* Seal entry zone: the glass is slowed by the seal, not by an obstacle. */
      AntiPinch_DropCycles = 0u;
    }
  }
  else
  {
    AntiPinch_DropCycles = 0u;

    /* First-order low-pass: reference += (speed - reference) / 16, in 1/16 mm/s. */
    filtered_q4 = (uint16)((AntiPinch_ReferenceQ4 - (AntiPinch_ReferenceQ4 >> ANTIPINCH_REFERENCE_SHIFT))
                           + speed_mm_s);
    if (filtered_q4 < ANTIPINCH_REFERENCE_MIN_Q4)
    {
      filtered_q4 = ANTIPINCH_REFERENCE_MIN_Q4;
    }
    AntiPinch_ReferenceQ4 = filtered_q4;
  }
}

/**
 * @brief  One cycle in state REVERSING: end the reversal by travel or by time.
 *
 * @param[in]  position  Window opening, 0..960 counts; any larger value means
 *                       "unknown" and leaves only the time limit.
 */
static void AntiPinch_StepReversing(uint16 position)
{
  boolean finished = FALSE;

  AntiPinch_ReversalCycles = (uint16)(AntiPinch_ReversalCycles + 1u);

  if ((position <= ANTIPINCH_POSITION_MAX) && (position >= AntiPinch_ReversalTarget))
  {
    finished = TRUE;
  }

  if (AntiPinch_ReversalCycles >= ANTIPINCH_REVERSAL_CYCLES)
  {
    finished = TRUE;
  }

  if (finished == TRUE)
  {
    AntiPinch_EnterIdle();
  }
}

/**
 * @brief  One cycle with an argument out of range.
 *
 * A closing movement that cannot be supervised is turned into a reversal. The
 * drive counts as closing when a closing movement is being supervised or when
 * the direction of this cycle says so.
 *
 * @param[in]  motion  Drive direction as passed to AntiPinch_Step(); may be out of range.
 */
static void AntiPinch_StepInvalid(AntiPinch_MotionType motion)
{
  if (AntiPinch_State == ANTIPINCH_STATE_REVERSING)
  {
    AntiPinch_StepReversing(ANTIPINCH_POSITION_INVALID);
  }
  else if ((AntiPinch_State != ANTIPINCH_STATE_IDLE) || (motion == ANTIPINCH_MOTION_CLOSING))
  {
    AntiPinch_StartReversal(ANTIPINCH_POSITION_INVALID);
  }
  else
  {
    /* The drive does not close: nothing to protect. */
  }
}
