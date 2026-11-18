/**
 * @file    AntiPinch.h
 * @brief   Detection of an obstacle in the path of the closing window.
 *
 * Design item: UNT-0003. Component: AntiPinch (CMP-0004).
 * Realizes interface IFC-0003 (detection status).
 * Implements SWR-0004 (obstacle detection), SWR-0005 (end of the reversal)
 * and SWR-0006 (reversal on invalid supervision inputs).
 *
 * Position values are window openings in counts of 0.5 mm (0 = fully closed,
 * 960 = fully open); speed values are in mm/s; one call of AntiPinch_Step()
 * is one cycle of 5 ms.
 */
#ifndef ANTIPINCH_H
#define ANTIPINCH_H

/*==============================================================================
 * INCLUDES
 *============================================================================*/
#include "Std_Types.h"

/*==============================================================================
 * EXPORTED MACROS
 *============================================================================*/

/** Drive direction: the motor is not driven. */
#define ANTIPINCH_MOTION_STOPPED         ((AntiPinch_MotionType)0u)
/** Drive direction: the motor is driven towards a larger window opening. */
#define ANTIPINCH_MOTION_OPENING         ((AntiPinch_MotionType)1u)
/** Drive direction: the motor is driven towards a smaller window opening. */
#define ANTIPINCH_MOTION_CLOSING         ((AntiPinch_MotionType)2u)

/** Detector state: no closing movement is supervised. */
#define ANTIPINCH_STATE_IDLE             ((AntiPinch_StateType)0u)
/** Detector state: closing has started, the drive is still accelerating. */
#define ANTIPINCH_STATE_SETTLING         ((AntiPinch_StateType)1u)
/** Detector state: the closing speed is compared with the reference speed. */
#define ANTIPINCH_STATE_MONITORING       ((AntiPinch_StateType)2u)
/** Detector state: an obstacle was found, the window has to be driven open. */
#define ANTIPINCH_STATE_REVERSING        ((AntiPinch_StateType)3u)

/** Largest position value: 960 counts = 480 mm = fully open. */
#define ANTIPINCH_POSITION_MAX           ((uint16)960u)
/** Position value that marks "position not referenced"; no physical meaning. */
#define ANTIPINCH_POSITION_INVALID       ((uint16)65535u)
/** Largest speed value: 500 mm/s. */
#define ANTIPINCH_SPEED_MAX_MM_S         ((uint16)500u)

/** Upper edge of the seal entry zone: 10 counts = 5 mm. Detection is active above it. */
#define ANTIPINCH_ZONE_LIMIT             ((uint16)10u)
/** Closing cycles before the speed comparison starts: 20 cycles = 100 ms. */
#define ANTIPINCH_SETTLING_CYCLES        ((uint8)20u)
/** Speed drop below the reference speed that indicates an obstacle: more than 20 mm/s. */
#define ANTIPINCH_DROP_THRESHOLD_MM_S    ((uint16)20u)
/** Consecutive cycles with a speed drop needed to confirm an obstacle: 2 cycles = 10 ms. */
#define ANTIPINCH_CONFIRM_CYCLES         ((uint8)2u)
/** Lower limit of the reference speed: 50 mm/s. */
#define ANTIPINCH_REFERENCE_MIN_MM_S     ((uint16)50u)
/** Opening travel of a reversal: 240 counts = 120 mm. */
#define ANTIPINCH_REVERSAL_TRAVEL        ((uint16)240u)
/** Longest duration of a reversal: 400 cycles = 2 s. */
#define ANTIPINCH_REVERSAL_CYCLES        ((uint16)400u)

/*==============================================================================
 * EXPORTED TYPES
 *============================================================================*/

/**
 * Applied drive direction as delivered by interface IFC-0005.
 * Valid values: ANTIPINCH_MOTION_STOPPED, _OPENING, _CLOSING (0..2).
 */
typedef uint8 AntiPinch_MotionType;

/** Detector state. Valid values: ANTIPINCH_STATE_IDLE, _SETTLING, _MONITORING, _REVERSING (0..3). */
typedef uint8 AntiPinch_StateType;

/** Output of the detector as published on interface IFC-0003. */
typedef struct
{
  /** Detector state, 0..3. */
  AntiPinch_StateType state;
  /** TRUE while the window has to be driven in the opening direction. */
  boolean reversal_request;
  /** Reference speed in mm/s, 50..500 in state MONITORING, 0 in every other state. */
  uint16 reference_speed_mm_s;
} AntiPinch_StatusType;

/*==============================================================================
 * EXPORTED FUNCTIONS
 *============================================================================*/

/**
 * @brief  Bring the detector into state IDLE.
 *
 * Call context: start-up, before the first call of AntiPinch_Step().
 * Afterwards the reversal request is FALSE and the reference speed is 0.
 */
void AntiPinch_Init(void);

/**
 * @brief  Supervise the closing movement for one cycle.
 *
 * Call context: 5 ms task, after the position and speed of the same cycle
 * have been determined; not re-entrant.
 *
 * IDLE: a closing drive starts SETTLING (cycle 1).
 * SETTLING: in closing cycle 20 the reference speed is set to the current
 * speed, at least ANTIPINCH_REFERENCE_MIN_MM_S, and MONITORING starts.
 * MONITORING: a speed more than ANTIPINCH_DROP_THRESHOLD_MM_S below the
 * reference speed in ANTIPINCH_CONFIRM_CYCLES consecutive cycles, at a
 * position above ANTIPINCH_ZONE_LIMIT or with the position not referenced,
 * starts REVERSING. Otherwise the reference speed follows the speed through
 * a first-order low-pass (one sixteenth of the difference per cycle).
 * REVERSING: ends in IDLE when the position has reached the detection
 * position plus ANTIPINCH_REVERSAL_TRAVEL (limited to ANTIPINCH_POSITION_MAX)
 * or after ANTIPINCH_REVERSAL_CYCLES cycles.
 * SETTLING and MONITORING fall back to IDLE when the drive no longer closes.
 *
 * @param[in]  position    Window opening, 0..960 counts of 0.5 mm, or ANTIPINCH_POSITION_INVALID.
 * @param[in]  speed_mm_s  Window speed, 0..500 mm/s.
 * @param[in]  motion      Applied drive direction, 0..2 (ANTIPINCH_MOTION_...).
 * @retval E_OK      All arguments were in range; the cycle was evaluated.
 * @retval E_NOT_OK  At least one argument was out of range. In SETTLING and
 *                   MONITORING, and in IDLE when motion is
 *                   ANTIPINCH_MOTION_CLOSING, the detector starts REVERSING,
 *                   limited by time only. In REVERSING the cycle counts towards
 *                   the time limit. Otherwise nothing changes.
 */
Std_ReturnType AntiPinch_Step(uint16 position, uint16 speed_mm_s, AntiPinch_MotionType motion);

/**
 * @brief  Read the detector output.
 *
 * Call context: task level.
 *
 * @param[out] status  Receives state, reversal request and reference speed; must not be a null pointer.
 * @retval E_OK      *status was written.
 * @retval E_NOT_OK  status is a null pointer; nothing was written.
 */
Std_ReturnType AntiPinch_GetStatus(AntiPinch_StatusType *status);

#endif /* ANTIPINCH_H */
