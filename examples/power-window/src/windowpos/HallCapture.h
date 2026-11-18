/**
 * @file    HallCapture.h
 * @brief   Capture of the Hall sensor edges of the window motor.
 *
 * Design item: UNT-0001. Component: WindowPos (CMP-0003).
 * Realizes interface IFC-0001 (Hall edge notification).
 * Implements the pulse acceptance of SWR-0001 (window position) and supplies
 * the pulse data for SWR-0003 (window speed).
 *
 * The unit counts the accepted edges and measures the interval between the
 * last two of them. It is written in the capture interrupt and read from task
 * level through HallCapture_GetSnapshot().
 */
#ifndef HALLCAPTURE_H
#define HALLCAPTURE_H

/*==============================================================================
 * INCLUDES
 *============================================================================*/
#include "Std_Types.h"

/*==============================================================================
 * EXPORTED MACROS
 *============================================================================*/

/**
 * Shortest interval between two edges that is accepted: 400 us.
 * At 0.5 mm of glass travel per edge this corresponds to 1250 mm/s, more than
 * six times the highest window speed of 200 mm/s.
 */
#define HALLCAPTURE_MIN_INTERVAL_US  ((uint32)400u)

/** Upper limit of the rejected edge counter: 65535 edges; the counter stops there. */
#define HALLCAPTURE_REJECTED_MAX     ((uint16)65535u)

/*==============================================================================
 * EXPORTED TYPES
 *============================================================================*/

/** Consistent copy of the capture data, taken at one instant. */
typedef struct
{
  /** Accepted edges since initialisation, modulo 65536. 1 count = 1 edge = 0.5 mm of glass travel. */
  uint16 pulse_count;
  /** Rejected edges since initialisation, 0..65535, saturating. */
  uint16 rejected_count;
  /** Capture time of the last accepted edge. 1 count = 1 us, free running, wraps at 2^32. */
  uint32 last_edge_us;
  /** Interval between the last two accepted edges. 1 count = 1 us; 0 = fewer than two edges accepted. */
  uint32 period_us;
} HallCapture_SnapshotType;

/*==============================================================================
 * EXPORTED FUNCTIONS
 *============================================================================*/

/**
 * @brief  Clear the capture data.
 *
 * Call context: start-up, before the Hall capture interrupt is enabled.
 * Afterwards pulse_count, rejected_count and period_us are 0 and the next edge
 * is treated as the first one.
 */
void HallCapture_Init(void);

/**
 * @brief  Process one edge of the Hall sensor signal.
 *
 * Call context: Hall capture interrupt only; not re-entrant.
 * The first edge after initialisation is always accepted and yields no period.
 * A later edge is accepted when it follows the last accepted edge by at least
 * HALLCAPTURE_MIN_INTERVAL_US; otherwise it only increments the rejected edge
 * counter. The interval is computed modulo 2^32, so a wrap of the capture
 * timer between two edges is handled.
 *
 * @param[in]  timestamp_us  Capture time of the edge, 0..4294967295 us, free running.
 */
void HallCapture_OnEdge(uint32 timestamp_us);

/**
 * @brief  Copy the capture data consistently.
 *
 * Call context: task level; the copy is made inside exclusive area HallData.
 *
 * @param[out] snapshot  Receives the copy; must not be a null pointer.
 * @retval E_OK      The snapshot was written.
 * @retval E_NOT_OK  snapshot is a null pointer; nothing was written and the
 *                   exclusive area was not entered.
 */
Std_ReturnType HallCapture_GetSnapshot(HallCapture_SnapshotType *snapshot);

#endif /* HALLCAPTURE_H */
