/**
 * @file    HallCapture.c
 * @brief   Capture of the Hall sensor edges of the window motor.
 *
 * Design item: UNT-0001. See HallCapture.h for the interface contract.
 */

/*==============================================================================
 * INCLUDES
 *============================================================================*/
#include "HallCapture.h"
#include "SchM_WindowPos.h"

/*==============================================================================
 * FILE-LOCAL VARIABLES
 *============================================================================*/

/*
 * All variables below are written by HallCapture_OnEdge() in the capture
 * interrupt and read by HallCapture_GetSnapshot() inside exclusive area
 * HallData.
 */

/** Accepted edges since initialisation, modulo 65536. */
static uint16 HallCapture_PulseCount = 0u;

/** Rejected edges since initialisation, saturating at HALLCAPTURE_REJECTED_MAX. */
static uint16 HallCapture_RejectedCount = 0u;

/** Capture time of the last accepted edge in us. */
static uint32 HallCapture_LastEdgeUs = 0u;

/** Interval between the last two accepted edges in us; 0 = not available. */
static uint32 HallCapture_PeriodUs = 0u;

/** TRUE once the first edge after initialisation has been accepted. */
static boolean HallCapture_EdgeSeen = FALSE;

/*==============================================================================
 * FUNCTION DEFINITIONS
 *============================================================================*/

void HallCapture_Init(void)
{
  HallCapture_PulseCount = 0u;
  HallCapture_RejectedCount = 0u;
  HallCapture_LastEdgeUs = 0u;
  HallCapture_PeriodUs = 0u;
  HallCapture_EdgeSeen = FALSE;
}

void HallCapture_OnEdge(uint32 timestamp_us)
{
  uint32 interval_us;

  if (HallCapture_EdgeSeen == FALSE)
  {
    /* First edge: there is no earlier edge to measure an interval against. */
    HallCapture_EdgeSeen = TRUE;
    HallCapture_LastEdgeUs = timestamp_us;
    HallCapture_PulseCount = (uint16)(HallCapture_PulseCount + 1u);
  }
  else
  {
    /* Unsigned subtraction: correct across a wrap of the capture timer. */
    interval_us = timestamp_us - HallCapture_LastEdgeUs;

    if (interval_us < HALLCAPTURE_MIN_INTERVAL_US)
    {
      /* Faster than the drive can move the glass: disturbance, not travel. */
      if (HallCapture_RejectedCount < HALLCAPTURE_REJECTED_MAX)
      {
        HallCapture_RejectedCount = (uint16)(HallCapture_RejectedCount + 1u);
      }
    }
    else
    {
      HallCapture_PeriodUs = interval_us;
      HallCapture_LastEdgeUs = timestamp_us;
      HallCapture_PulseCount = (uint16)(HallCapture_PulseCount + 1u);
    }
  }
}

Std_ReturnType HallCapture_GetSnapshot(HallCapture_SnapshotType *snapshot)
{
  Std_ReturnType result = E_NOT_OK;

  if (snapshot != NULL_PTR)
  {
    SchM_Enter_WindowPos_HallData();
    snapshot->pulse_count = HallCapture_PulseCount;
    snapshot->rejected_count = HallCapture_RejectedCount;
    snapshot->last_edge_us = HallCapture_LastEdgeUs;
    snapshot->period_us = HallCapture_PeriodUs;
    SchM_Exit_WindowPos_HallData();
    result = E_OK;
  }

  return result;
}
