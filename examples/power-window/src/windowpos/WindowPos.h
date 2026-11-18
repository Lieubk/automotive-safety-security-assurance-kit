/**
 * @file    WindowPos.h
 * @brief   Window position and window speed from the Hall pulse data.
 *
 * Design item: UNT-0002. Component: WindowPos (CMP-0003).
 * Realizes interface IFC-0002 (window motion).
 * Implements SWR-0001 (window position), SWR-0002 (position reference) and
 * SWR-0003 (window speed).
 *
 * Position: the window opening, measured from the fully closed end stop.
 * 1 count = 0.5 mm (one Hall pulse), 0 = fully closed, 960 = fully open (480 mm).
 * Speed: 1 count = 1 mm/s, without sign; the direction is that of the drive.
 */
#ifndef WINDOWPOS_H
#define WINDOWPOS_H

/*==============================================================================
 * INCLUDES
 *============================================================================*/
#include "Std_Types.h"

/*==============================================================================
 * EXPORTED MACROS
 *============================================================================*/

/** Drive direction: the motor is not driven. */
#define WINDOWPOS_DIRECTION_STOPPED  ((WindowPos_DirectionType)0u)
/** Drive direction: the motor is driven towards a larger window opening. */
#define WINDOWPOS_DIRECTION_OPENING  ((WindowPos_DirectionType)1u)
/** Drive direction: the motor is driven towards a smaller window opening. */
#define WINDOWPOS_DIRECTION_CLOSING  ((WindowPos_DirectionType)2u)

/** Largest position value: 960 counts = 480 mm = fully open. */
#define WINDOWPOS_POSITION_MAX       ((uint16)960u)
/** Position value that marks "not referenced since reset"; no physical meaning. */
#define WINDOWPOS_POSITION_INVALID   ((uint16)65535u)
/** Largest speed value: 500 mm/s; faster pulse trains are reported as this value. */
#define WINDOWPOS_SPEED_MAX_MM_S     ((uint16)500u)

/*==============================================================================
 * EXPORTED TYPES
 *============================================================================*/

/**
 * Applied drive direction as delivered by interface IFC-0005.
 * Valid values: WINDOWPOS_DIRECTION_STOPPED, _OPENING, _CLOSING (0..2).
 */
typedef uint8 WindowPos_DirectionType;

/*==============================================================================
 * EXPORTED FUNCTIONS
 *============================================================================*/

/**
 * @brief  Bring the unit into its start state.
 *
 * Call context: start-up, after HallCapture_Init() and before the first call
 * of WindowPos_Step(). Afterwards the position is not referenced and the
 * speed is 0 mm/s.
 */
void WindowPos_Init(void);

/**
 * @brief  Take in the Hall pulses of the last cycle and update position and speed.
 *
 * Call context: 5 ms task; not re-entrant.
 *
 * Position: every new pulse moves the position by one count in the drive
 * direction, limited to 0..WINDOWPOS_POSITION_MAX. Pulses that arrive while
 * the drive is stopped are counted in the last drive direction (run-out).
 * The position becomes valid, and is set to WINDOWPOS_POSITION_MAX, when the
 * drive has been opening at 0 mm/s for 40 consecutive calls (200 ms): the
 * window then rests on the fully open end stop.
 *
 * Speed: 500000 divided by the longer of the last pulse period and the time
 * since the last pulse, both in us. 50000 us or longer gives 0 mm/s, 1000 us
 * or shorter gives WINDOWPOS_SPEED_MAX_MM_S. After a standstill the speed
 * stays 0 mm/s until two pulses have arrived.
 *
 * @param[in]  now_us     Current value of the capture time base, 0..4294967295 us, free running.
 * @param[in]  direction  Applied drive direction, 0..2 (WINDOWPOS_DIRECTION_...).
 * @retval E_OK      Position and speed were updated.
 * @retval E_NOT_OK  direction is out of range, or the pulse data could not be
 *                   read. Position, speed and all internal data are unchanged;
 *                   pulses that arrived are taken in by the next successful call.
 */
Std_ReturnType WindowPos_Step(uint32 now_us, WindowPos_DirectionType direction);

/**
 * @brief  Read the window position.
 *
 * Call context: task level.
 *
 * @param[out] position  Window opening, 0..960 counts of 0.5 mm, or
 *                       WINDOWPOS_POSITION_INVALID; must not be a null pointer.
 * @retval E_OK      The position is referenced; *position holds 0..960.
 * @retval E_NOT_OK  The position is not referenced (*position holds
 *                   WINDOWPOS_POSITION_INVALID), or position is a null pointer
 *                   (nothing is written).
 */
Std_ReturnType WindowPos_GetPosition(uint16 *position);

/**
 * @brief  Read the window speed.
 *
 * Call context: task level.
 *
 * @param[out] speed_mm_s  Window speed, 0 or 10..500 mm/s; must not be a null pointer.
 * @retval E_OK      *speed_mm_s holds the speed of the last successful step.
 * @retval E_NOT_OK  speed_mm_s is a null pointer; nothing is written.
 */
Std_ReturnType WindowPos_GetSpeed(uint16 *speed_mm_s);

#endif /* WINDOWPOS_H */
