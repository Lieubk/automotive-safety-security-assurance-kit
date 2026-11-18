/**
 * @file    test_AntiPinch.c
 * @brief   Unit tests of unit AntiPinch (UNT-0003), test cases UT-0013 to UT-0020.
 *
 * Built from this file and src/antipinch/AntiPinch.c. The unit has no
 * dependencies; every input is an argument of AntiPinch_Step().
 * Positions are in counts of 0.5 mm, speeds in mm/s, one step is one 5 ms cycle.
 */
#include "test_support.h"
#include "AntiPinch.h"

/*------------------------------------------------------------------------------
 * Helpers
 *----------------------------------------------------------------------------*/

/** Check detector state and reversal request as read through AntiPinch_GetStatus(). */
#define ASSERT_DETECTOR(expected_state, expected_request) \
  do \
  { \
    AntiPinch_StatusType detector_status; \
    TEST_ASSERT_EQUAL(E_OK, AntiPinch_GetStatus(&detector_status)); \
    TEST_ASSERT_EQUAL((expected_state), detector_status.state); \
    TEST_ASSERT_EQUAL((expected_request), detector_status.reversal_request); \
  } while (0)

/** Check the reference speed as read through AntiPinch_GetStatus(). */
#define ASSERT_REFERENCE(expected_mm_s) \
  do \
  { \
    AntiPinch_StatusType detector_status; \
    TEST_ASSERT_EQUAL(E_OK, AntiPinch_GetStatus(&detector_status)); \
    TEST_ASSERT_EQUAL((expected_mm_s), detector_status.reference_speed_mm_s); \
  } while (0)

/** Repeat one input set for a number of cycles. Returns the number of steps that did not return E_OK. */
static unsigned int run_cycles(unsigned int cycles, uint16 position, uint16 speed_mm_s, AntiPinch_MotionType motion)
{
  unsigned int refused = 0u;
  unsigned int cycle;

  for (cycle = 0u; cycle < cycles; cycle++)
  {
    if (AntiPinch_Step(position, speed_mm_s, motion) != E_OK)
    {
      refused++;
    }
  }
  return refused;
}

/** Initialise and close for 20 cycles at constant speed: the detector is then in MONITORING. */
static void start_monitoring(uint16 position, uint16 speed_mm_s)
{
  AntiPinch_Init();
  (void)run_cycles(20u, position, speed_mm_s, ANTIPINCH_MOTION_CLOSING);
}

/*------------------------------------------------------------------------------
 * Test cases
 *----------------------------------------------------------------------------*/

/* UT-0013: settling time and start of monitoring */
static void test_UT_0013_settling_and_start_of_monitoring(void)
{
  AntiPinch_Init();
  ASSERT_DETECTOR(ANTIPINCH_STATE_IDLE, FALSE);
  ASSERT_REFERENCE(0u);

  /* An opening or stopped drive is not supervised. */
  TEST_ASSERT_EQUAL(0u, run_cycles(5u, 600u, 150u, ANTIPINCH_MOTION_OPENING));
  TEST_ASSERT_EQUAL(0u, run_cycles(5u, 600u, 0u, ANTIPINCH_MOTION_STOPPED));
  ASSERT_DETECTOR(ANTIPINCH_STATE_IDLE, FALSE);

  /* Closing cycle 1 starts the settling time. */
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(600u, 0u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_SETTLING, FALSE);

  /* Cycles 2 to 19: speed changes, even a fall from 150 to 40 mm/s, cause no reaction. */
  TEST_ASSERT_EQUAL(0u, run_cycles(9u, 600u, 150u, ANTIPINCH_MOTION_CLOSING));
  TEST_ASSERT_EQUAL(0u, run_cycles(9u, 600u, 40u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_SETTLING, FALSE);
  ASSERT_REFERENCE(0u);

  /* Cycle 20: monitoring starts with the current speed as reference speed. */
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(600u, 150u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);
  ASSERT_REFERENCE(150u);

  /* The drive stops: back to IDLE. A new closing movement settles again for 20 cycles. */
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(600u, 150u, ANTIPINCH_MOTION_STOPPED));
  ASSERT_DETECTOR(ANTIPINCH_STATE_IDLE, FALSE);
  ASSERT_REFERENCE(0u);
  TEST_ASSERT_EQUAL(0u, run_cycles(19u, 600u, 140u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_SETTLING, FALSE);
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(600u, 140u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);
  ASSERT_REFERENCE(140u);

  /* An opening drive ends the monitoring in the same way. */
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(600u, 140u, ANTIPINCH_MOTION_OPENING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_IDLE, FALSE);
  ASSERT_REFERENCE(0u);

  /* Settling interrupted by an opening drive: the count starts again. */
  AntiPinch_Init();
  TEST_ASSERT_EQUAL(0u, run_cycles(10u, 600u, 100u, ANTIPINCH_MOTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(600u, 100u, ANTIPINCH_MOTION_OPENING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_IDLE, FALSE);
  TEST_ASSERT_EQUAL(0u, run_cycles(19u, 600u, 100u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_SETTLING, FALSE);
}

/* UT-0014: obstacle detected by a speed drop */
static void test_UT_0014_obstacle_detected_by_speed_drop(void)
{
  /* Steady closing at 150 mm/s, opening 300 mm: nothing is reported. */
  start_monitoring(600u, 150u);
  TEST_ASSERT_EQUAL(0u, run_cycles(10u, 600u, 150u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);
  ASSERT_REFERENCE(150u);

  /* The speed falls to 129 mm/s, 21 mm/s below the reference: not yet in the first cycle ... */
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(600u, 129u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);
  ASSERT_REFERENCE(150u);

  /* ... but in the second one, 10 ms after the fall at the latest. */
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(599u, 129u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);
  ASSERT_REFERENCE(0u);

  /* The request stays set while the drive stops and turns. */
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(598u, 20u, ANTIPINCH_MOTION_STOPPED));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(598u, 0u, ANTIPINCH_MOTION_OPENING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);

  /* A blocked window (speed 0) is found in the same way. */
  start_monitoring(300u, 180u);
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(300u, 0u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(300u, 0u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);
}

/* UT-0015: limits of the speed drop and of its confirmation */
static void test_UT_0015_threshold_and_confirmation_limits(void)
{
  unsigned int cycle;

  /* 130 mm/s is exactly 20 mm/s below the reference of 150 mm/s: never an obstacle. */
  start_monitoring(600u, 150u);
  for (cycle = 0u; cycle < 40u; cycle++)
  {
    TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(600u, 130u, ANTIPINCH_MOTION_CLOSING));
    ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);
  }

  /* 21 mm/s below the reference for single cycles only: never an obstacle, reference unchanged. */
  start_monitoring(600u, 150u);
  for (cycle = 0u; cycle < 5u; cycle++)
  {
    TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(600u, 129u, ANTIPINCH_MOTION_CLOSING));
    ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);
    TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(600u, 150u, ANTIPINCH_MOTION_CLOSING));
    ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);
    ASSERT_REFERENCE(150u);
  }

  /* Two cycles in a row: obstacle. */
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(600u, 129u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(600u, 129u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);
}

/* UT-0016: edge of the protected zone and position not referenced */
static void test_UT_0016_protected_zone_and_invalid_position(void)
{
  /* Opening 5 mm (10 counts): seal entry zone, a speed drop is not an obstacle. */
  start_monitoring(10u, 150u);
  TEST_ASSERT_EQUAL(0u, run_cycles(10u, 10u, 100u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);

  /* Opening 5.5 mm (11 counts): protected. */
  start_monitoring(11u, 150u);
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(11u, 100u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(11u, 100u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);

  /* A drop that starts at 11 counts and continues at 10 counts is not confirmed ... */
  start_monitoring(11u, 150u);
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(11u, 100u, ANTIPINCH_MOTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(10u, 100u, ANTIPINCH_MOTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(10u, 100u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);

  /* ... and needs two full cycles again once the position is back above the zone limit. */
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(11u, 100u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(11u, 100u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);

  /* Position not referenced: treated as inside the protected zone. */
  start_monitoring(65535u, 150u);
  ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(65535u, 100u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(65535u, 100u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);
}

/* UT-0017: reference speed - lower limit and tracking */
static void test_UT_0017_reference_speed_limit_and_tracking(void)
{
  AntiPinch_StatusType status;
  unsigned int cycle;

  /* Closing at 30 mm/s: the reference speed starts at its lower limit of 50 mm/s and stays there. */
  AntiPinch_Init();
  TEST_ASSERT_EQUAL(0u, run_cycles(20u, 600u, 30u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);
  ASSERT_REFERENCE(50u);
  TEST_ASSERT_EQUAL(0u, run_cycles(10u, 600u, 30u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);
  ASSERT_REFERENCE(50u);

  /* 29 mm/s is more than 20 mm/s below the limit: a drive that does not get going is an obstacle. */
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(600u, 29u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(600u, 29u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);

  /* Speed falling from 150 to 100 mm/s by 1 mm/s every 10 ms (100 mm/s^2): followed, no obstacle. */
  start_monitoring(600u, 150u);
  for (cycle = 1u; cycle <= 100u; cycle++)
  {
    TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(600u, (uint16)(150u - (cycle / 2u)), ANTIPINCH_MOTION_CLOSING));
    ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);
  }
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_GetStatus(&status));
  TEST_ASSERT(status.reference_speed_mm_s >= 100u);
  TEST_ASSERT(status.reference_speed_mm_s <= 110u);

  /* A constant speed is reached exactly, from above and from below. */
  TEST_ASSERT_EQUAL(0u, run_cycles(200u, 600u, 100u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_REFERENCE(100u);
  TEST_ASSERT_EQUAL(0u, run_cycles(200u, 600u, 115u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);
  ASSERT_REFERENCE(115u);
}

/* UT-0018: end of the reversal by travel */
static void test_UT_0018_reversal_ends_by_travel(void)
{
  /* Obstacle at 600 counts: the reversal ends at 840 counts (120 mm further open). */
  start_monitoring(600u, 150u);
  TEST_ASSERT_EQUAL(0u, run_cycles(2u, 600u, 100u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(600u, 0u, ANTIPINCH_MOTION_STOPPED));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(700u, 150u, ANTIPINCH_MOTION_OPENING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(839u, 150u, ANTIPINCH_MOTION_OPENING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(840u, 150u, ANTIPINCH_MOTION_OPENING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_IDLE, FALSE);

  /* Obstacle at 800 counts: less than 120 mm remain, the reversal ends fully open at 960 counts. */
  start_monitoring(800u, 150u);
  TEST_ASSERT_EQUAL(0u, run_cycles(2u, 800u, 100u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(959u, 150u, ANTIPINCH_MOTION_OPENING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(960u, 150u, ANTIPINCH_MOTION_OPENING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_IDLE, FALSE);

  /* After the reversal the next closing movement is supervised as usual. */
  TEST_ASSERT_EQUAL(0u, run_cycles(20u, 960u, 150u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_MONITORING, FALSE);
}

/* UT-0019: end of the reversal by time */
static void test_UT_0019_reversal_ends_by_time(void)
{
  /* Position not referenced: only the time limit of 400 cycles (2 s) ends the reversal. */
  start_monitoring(65535u, 150u);
  TEST_ASSERT_EQUAL(0u, run_cycles(2u, 65535u, 100u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);
  TEST_ASSERT_EQUAL(0u, run_cycles(399u, 65535u, 150u, ANTIPINCH_MOTION_OPENING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(65535u, 150u, ANTIPINCH_MOTION_OPENING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_IDLE, FALSE);

  /* Position referenced, but the window does not move: the time limit ends the reversal as well. */
  start_monitoring(600u, 150u);
  TEST_ASSERT_EQUAL(0u, run_cycles(2u, 600u, 100u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);
  TEST_ASSERT_EQUAL(0u, run_cycles(399u, 600u, 0u, ANTIPINCH_MOTION_OPENING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(600u, 0u, ANTIPINCH_MOTION_OPENING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_IDLE, FALSE);
}

/* UT-0020: arguments out of range, and null pointer */
static void test_UT_0020_invalid_arguments_and_null_pointer(void)
{
  /* The drive does not close: each argument just outside its range is refused and changes nothing. */
  AntiPinch_Init();
  TEST_ASSERT_EQUAL(E_NOT_OK, AntiPinch_Step(961u, 0u, ANTIPINCH_MOTION_STOPPED));
  TEST_ASSERT_EQUAL(E_NOT_OK, AntiPinch_Step(65534u, 0u, ANTIPINCH_MOTION_OPENING));
  TEST_ASSERT_EQUAL(E_NOT_OK, AntiPinch_Step(600u, 501u, ANTIPINCH_MOTION_OPENING));
  TEST_ASSERT_EQUAL(E_NOT_OK, AntiPinch_Step(600u, 100u, (AntiPinch_MotionType)3u));
  ASSERT_DETECTOR(ANTIPINCH_STATE_IDLE, FALSE);

  /* The drive starts to close with a position out of range: reversal from the first cycle on. */
  TEST_ASSERT_EQUAL(E_NOT_OK, AntiPinch_Step(961u, 0u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);
  AntiPinch_Init();

  /* The limits of the ranges are accepted. */
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(960u, 500u, ANTIPINCH_MOTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(0u, 0u, ANTIPINCH_MOTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(65535u, 0u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_SETTLING, FALSE);

  /* SETTLING: a direction out of range still belongs to the closing movement and starts a reversal. */
  TEST_ASSERT_EQUAL(E_NOT_OK, AntiPinch_Step(600u, 80u, (AntiPinch_MotionType)3u));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);

  /* SETTLING: a speed out of range cannot be supervised and starts a reversal. */
  AntiPinch_Init();
  TEST_ASSERT_EQUAL(0u, run_cycles(5u, 600u, 80u, ANTIPINCH_MOTION_CLOSING));
  TEST_ASSERT_EQUAL(E_NOT_OK, AntiPinch_Step(600u, 501u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);

  /* This reversal is limited by time only: fully open does not end it ... */
  TEST_ASSERT_EQUAL(E_OK, AntiPinch_Step(960u, 150u, ANTIPINCH_MOTION_OPENING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);

  /* ... and refused cycles count towards the 400 cycles: 1 + 398 = 399, then the last one. */
  TEST_ASSERT_EQUAL(398u, run_cycles(398u, 961u, 150u, ANTIPINCH_MOTION_OPENING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);
  TEST_ASSERT_EQUAL(E_NOT_OK, AntiPinch_Step(961u, 150u, ANTIPINCH_MOTION_OPENING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_IDLE, FALSE);

  /* MONITORING: a position or a direction out of range starts a reversal as well. */
  start_monitoring(600u, 150u);
  TEST_ASSERT_EQUAL(E_NOT_OK, AntiPinch_Step(961u, 150u, ANTIPINCH_MOTION_CLOSING));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);
  start_monitoring(600u, 150u);
  TEST_ASSERT_EQUAL(E_NOT_OK, AntiPinch_Step(600u, 150u, (AntiPinch_MotionType)255u));
  ASSERT_DETECTOR(ANTIPINCH_STATE_REVERSING, TRUE);

  /* Null pointer at the read function. */
  TEST_ASSERT_EQUAL(E_NOT_OK, AntiPinch_GetStatus(NULL_PTR));
}

/*------------------------------------------------------------------------------
 * Test program
 *----------------------------------------------------------------------------*/

int main(void)
{
  TEST_RUN("UT-0013", test_UT_0013_settling_and_start_of_monitoring);
  TEST_RUN("UT-0014", test_UT_0014_obstacle_detected_by_speed_drop);
  TEST_RUN("UT-0015", test_UT_0015_threshold_and_confirmation_limits);
  TEST_RUN("UT-0016", test_UT_0016_protected_zone_and_invalid_position);
  TEST_RUN("UT-0017", test_UT_0017_reference_speed_limit_and_tracking);
  TEST_RUN("UT-0018", test_UT_0018_reversal_ends_by_travel);
  TEST_RUN("UT-0019", test_UT_0019_reversal_ends_by_time);
  TEST_RUN("UT-0020", test_UT_0020_invalid_arguments_and_null_pointer);
  return TEST_EXIT_CODE();
}
