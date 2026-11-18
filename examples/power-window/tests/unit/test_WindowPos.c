/**
 * @file    test_WindowPos.c
 * @brief   Unit tests of unit WindowPos (UNT-0002), test cases UT-0006 to UT-0012.
 *
 * Built from this file and src/windowpos/WindowPos.c. The capture unit is
 * replaced by a test double, so that every pulse pattern, time relation and
 * service failure can be produced.
 */
#include "test_support.h"
#include "WindowPos.h"
#include "HallCapture.h"

/*------------------------------------------------------------------------------
 * Test double of HallCapture_GetSnapshot()
 *----------------------------------------------------------------------------*/

static HallCapture_SnapshotType stub_snapshot;
static Std_ReturnType stub_result = E_OK;
static unsigned int stub_calls = 0u;

Std_ReturnType HallCapture_GetSnapshot(HallCapture_SnapshotType *snapshot)
{
  stub_calls++;
  if ((stub_result == E_OK) && (snapshot != NULL_PTR))
  {
    *snapshot = stub_snapshot;
  }
  return stub_result;
}

/*------------------------------------------------------------------------------
 * Helpers
 *----------------------------------------------------------------------------*/

/** Time passed to WindowPos_Step() by step_with_pulses(), in us. */
static uint32 test_now_us = 0u;

/** Start state: unit initialised, no pulse ever captured, time far away from time stamp 0. */
static void fixture_reset(void)
{
  stub_snapshot.pulse_count = 0u;
  stub_snapshot.rejected_count = 0u;
  stub_snapshot.last_edge_us = 0u;
  stub_snapshot.period_us = 0u;
  stub_result = E_OK;
  stub_calls = 0u;
  test_now_us = 1000000u;
  WindowPos_Init();
}

/** Describe the pulse data the next step will read. */
static void set_capture(uint16 pulse_count, uint32 period_us, uint32 last_edge_us)
{
  stub_snapshot.pulse_count = pulse_count;
  stub_snapshot.period_us = period_us;
  stub_snapshot.last_edge_us = last_edge_us;
}

/**
 * One 5 ms cycle in which the given number of pulses arrived. The time stamp
 * of the last pulse stays far in the past, so the speed is 0 mm/s.
 */
static Std_ReturnType step_with_pulses(uint16 pulses, WindowPos_DirectionType direction)
{
  stub_snapshot.pulse_count = (uint16)(stub_snapshot.pulse_count + pulses);
  test_now_us += 5000u;
  return WindowPos_Step(test_now_us, direction);
}

/** Cycles with the given drive direction, no pulses, speed 0 mm/s. Returns the number of refused steps. */
static unsigned int stand_still(unsigned int cycles, WindowPos_DirectionType direction)
{
  unsigned int refused = 0u;
  unsigned int cycle;

  for (cycle = 0u; cycle < cycles; cycle++)
  {
    if (step_with_pulses(0u, direction) != E_OK)
    {
      refused++;
    }
  }
  return refused;
}

/*------------------------------------------------------------------------------
 * Test cases
 *----------------------------------------------------------------------------*/

/* UT-0006: state after initialisation */
static void test_UT_0006_state_after_init(void)
{
  uint16 position = 0u;
  uint16 speed_mm_s = 123u;

  fixture_reset();
  TEST_ASSERT_EQUAL(E_NOT_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(65535u, position);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(0u, speed_mm_s);

  /* Reference the position and let the window move: 2 pulses, 4000 us apart, closing. */
  TEST_ASSERT_EQUAL(0u, stand_still(40u, WINDOWPOS_DIRECTION_OPENING));
  set_capture(2u, 4000u, 1300000u);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(1300100u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(958u, position);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(125u, speed_mm_s);

  /* A new initialisation returns to the start state. */
  WindowPos_Init();
  TEST_ASSERT_EQUAL(E_NOT_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(65535u, position);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(0u, speed_mm_s);
}

/* UT-0007: referencing at the fully open end stop */
static void test_UT_0007_referencing_at_open_stop(void)
{
  uint16 position = 0u;

  /* 39 cycles opening at 0 mm/s: not yet; cycle 40: referenced, fully open. */
  fixture_reset();
  TEST_ASSERT_EQUAL(0u, stand_still(39u, WINDOWPOS_DIRECTION_OPENING));
  TEST_ASSERT_EQUAL(E_NOT_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(65535u, position);
  TEST_ASSERT_EQUAL(0u, stand_still(1u, WINDOWPOS_DIRECTION_OPENING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(960u, position);

  /* Resting on the end stop for another 300 cycles (1.5 s) changes nothing. */
  TEST_ASSERT_EQUAL(0u, stand_still(300u, WINDOWPOS_DIRECTION_OPENING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(960u, position);

  /* The count starts again when the drive stops opening for one cycle. */
  fixture_reset();
  TEST_ASSERT_EQUAL(0u, stand_still(39u, WINDOWPOS_DIRECTION_OPENING));
  TEST_ASSERT_EQUAL(0u, stand_still(1u, WINDOWPOS_DIRECTION_STOPPED));
  TEST_ASSERT_EQUAL(0u, stand_still(39u, WINDOWPOS_DIRECTION_OPENING));
  TEST_ASSERT_EQUAL(E_NOT_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(0u, stand_still(1u, WINDOWPOS_DIRECTION_OPENING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(960u, position);

  /* The count starts again when the window moves for one cycle (100 mm/s). */
  fixture_reset();
  TEST_ASSERT_EQUAL(0u, stand_still(39u, WINDOWPOS_DIRECTION_OPENING));
  set_capture(2u, 5000u, test_now_us + 4900u);
  TEST_ASSERT_EQUAL(E_OK, step_with_pulses(0u, WINDOWPOS_DIRECTION_OPENING));
  test_now_us += 60000u;
  TEST_ASSERT_EQUAL(0u, stand_still(39u, WINDOWPOS_DIRECTION_OPENING));
  TEST_ASSERT_EQUAL(E_NOT_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(0u, stand_still(1u, WINDOWPOS_DIRECTION_OPENING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(960u, position);

  /* A closing or stopped drive at 0 mm/s never references the position. */
  fixture_reset();
  TEST_ASSERT_EQUAL(0u, stand_still(100u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(0u, stand_still(100u, WINDOWPOS_DIRECTION_STOPPED));
  TEST_ASSERT_EQUAL(E_NOT_OK, WindowPos_GetPosition(&position));

  /* A referenced position is set to fully open again at the end stop. */
  TEST_ASSERT_EQUAL(0u, stand_still(40u, WINDOWPOS_DIRECTION_OPENING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(960u, position);
  TEST_ASSERT_EQUAL(E_OK, step_with_pulses(100u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(860u, position);
  TEST_ASSERT_EQUAL(0u, stand_still(40u, WINDOWPOS_DIRECTION_OPENING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(960u, position);
}

/* UT-0008: position counting, run-out and travel limits */
static void test_UT_0008_position_counting_and_limits(void)
{
  uint16 position = 0u;

  fixture_reset();
  TEST_ASSERT_EQUAL(0u, stand_still(40u, WINDOWPOS_DIRECTION_OPENING));

  /* Closing counts down, opening counts up. */
  TEST_ASSERT_EQUAL(E_OK, step_with_pulses(100u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(860u, position);
  TEST_ASSERT_EQUAL(E_OK, step_with_pulses(20u, WINDOWPOS_DIRECTION_OPENING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(880u, position);

  /* Pulses with the drive stopped are counted in the last drive direction. */
  TEST_ASSERT_EQUAL(E_OK, step_with_pulses(3u, WINDOWPOS_DIRECTION_STOPPED));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(883u, position);
  TEST_ASSERT_EQUAL(E_OK, step_with_pulses(5u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, step_with_pulses(2u, WINDOWPOS_DIRECTION_STOPPED));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(876u, position);

  /* Upper limit: 959, 960, and no further. */
  TEST_ASSERT_EQUAL(E_OK, step_with_pulses(83u, WINDOWPOS_DIRECTION_OPENING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(959u, position);
  TEST_ASSERT_EQUAL(E_OK, step_with_pulses(1u, WINDOWPOS_DIRECTION_OPENING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(960u, position);
  TEST_ASSERT_EQUAL(E_OK, step_with_pulses(1u, WINDOWPOS_DIRECTION_OPENING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(960u, position);
  TEST_ASSERT_EQUAL(E_OK, step_with_pulses(200u, WINDOWPOS_DIRECTION_OPENING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(960u, position);

  /* Lower limit: 1, 0, and no further. */
  TEST_ASSERT_EQUAL(E_OK, step_with_pulses(959u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(1u, position);
  TEST_ASSERT_EQUAL(E_OK, step_with_pulses(1u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(0u, position);
  TEST_ASSERT_EQUAL(E_OK, step_with_pulses(1u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(0u, position);
  TEST_ASSERT_EQUAL(E_OK, step_with_pulses(500u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(0u, position);

  /* Wrap of the 16 bit pulse counter: 65530 -> 4 is 10 pulses. */
  stub_snapshot.pulse_count = 65530u;
  TEST_ASSERT_EQUAL(E_OK, step_with_pulses(0u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(0u, position);
  TEST_ASSERT_EQUAL(E_OK, step_with_pulses(10u, WINDOWPOS_DIRECTION_OPENING));
  TEST_ASSERT_EQUAL(4u, stub_snapshot.pulse_count);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(10u, position);
}

/* UT-0009: speed from the pulse period and from the time since the last pulse */
static void test_UT_0009_speed_from_period_and_elapsed_time(void)
{
  uint16 position = 0u;
  uint16 speed_mm_s = 0u;

  /* Two pulses 3333 us apart, the last one 500 us ago: 500000 / 3333 = 150 mm/s. */
  fixture_reset();
  set_capture(2u, 3333u, 2000000u);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(2000500u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(150u, speed_mm_s);

  /* No further pulse: after 5000 us at most 100 mm/s, after 10000 us at most 50 mm/s. */
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(2005000u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(100u, speed_mm_s);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(2010000u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(50u, speed_mm_s);

  /* A pulse after 12500 us, read 2500 us later: the period decides, 40 mm/s. */
  set_capture(3u, 12500u, 2012500u);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(2015000u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(40u, speed_mm_s);

  /* Rounding down: 500000 / 3334 = 149.97 -> 149 mm/s. */
  set_capture(4u, 3334u, 2015834u);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(2016000u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(149u, speed_mm_s);

  /* The speed is also measured while the drive is stopped (run-out) and opening. */
  set_capture(5u, 5000u, 2020834u);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(2021000u, WINDOWPOS_DIRECTION_STOPPED));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(100u, speed_mm_s);
  set_capture(6u, 2500u, 2023334u);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(2024000u, WINDOWPOS_DIRECTION_OPENING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(200u, speed_mm_s);

  /* The speed does not depend on a referenced position. */
  TEST_ASSERT_EQUAL(E_NOT_OK, WindowPos_GetPosition(&position));
}

/* UT-0010: speed limits - standstill and maximum */
static void test_UT_0010_speed_limits(void)
{
  uint16 speed_mm_s = 0u;

  /* 49999 us without a pulse: 10 mm/s. 50000 us: standstill, 0 mm/s. */
  fixture_reset();
  set_capture(2u, 3333u, 3000000u);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(3049999u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(10u, speed_mm_s);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(3050000u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(0u, speed_mm_s);

  /*
   * The first pulse after a standstill gives no speed, whatever period comes with it
   * (3000 us here, as a wrap of the time base during the pause can produce); the second one does.
   */
  set_capture(3u, 3000u, 3060000u);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(3060100u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(0u, speed_mm_s);
  set_capture(4u, 4000u, 3064000u);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(3064100u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(125u, speed_mm_s);

  /* Pulse period 49999 us: 10 mm/s. 50000 us: 0 mm/s, and the next period counts at once. */
  set_capture(5u, 49999u, 3113999u);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(3114000u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(10u, speed_mm_s);
  set_capture(6u, 50000u, 3163999u);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(3164000u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(0u, speed_mm_s);
  set_capture(7u, 5000u, 3168999u);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(3169000u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(100u, speed_mm_s);

  /* Maximum: 1001 us -> 499 mm/s, 1000 us -> 500 mm/s, 400 us -> still 500 mm/s. */
  set_capture(8u, 1001u, 3170000u);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(3170100u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(499u, speed_mm_s);
  set_capture(9u, 1000u, 3171000u);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(3171100u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(500u, speed_mm_s);
  set_capture(10u, 400u, 3171400u);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(3171500u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(500u, speed_mm_s);

  /* Pulse captured 100 us after the time was sampled: the time since the pulse counts as 0. */
  set_capture(11u, 4000u, 3175400u);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(3175300u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(125u, speed_mm_s);

  /* Wrap of the time base between the last pulse and now: 0x1500 = 5376 us -> 93 mm/s. */
  set_capture(12u, 3333u, 0xFFFFF000u);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(0x00000500u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(93u, speed_mm_s);
}

/* UT-0011: refused step - invalid direction and failure of the capture service */
static void test_UT_0011_step_refused(void)
{
  uint16 position = 0u;
  uint16 speed_mm_s = 0u;

  /* Referenced, 2 pulses closing at 125 mm/s: position 958. */
  fixture_reset();
  TEST_ASSERT_EQUAL(0u, stand_still(40u, WINDOWPOS_DIRECTION_OPENING));
  set_capture(2u, 4000u, 1300000u);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(1300100u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(958u, position);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(125u, speed_mm_s);

  /* Direction 3 and 255 with 10 pulses pending: refused, pulse data not read, nothing changes. */
  set_capture(12u, 2000u, 1305000u);
  stub_calls = 0u;
  TEST_ASSERT_EQUAL(E_NOT_OK, WindowPos_Step(1305100u, (WindowPos_DirectionType)3u));
  TEST_ASSERT_EQUAL(E_NOT_OK, WindowPos_Step(1305100u, (WindowPos_DirectionType)255u));
  TEST_ASSERT_EQUAL(0u, stub_calls);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(958u, position);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(125u, speed_mm_s);

  /* The next valid step takes the pending pulses in: position 948, 250 mm/s. */
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(1305100u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(1u, stub_calls);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(948u, position);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(250u, speed_mm_s);

  /* Capture service fails with 4 pulses pending: refused, nothing changes. */
  set_capture(16u, 5000u, 1310000u);
  stub_result = E_NOT_OK;
  TEST_ASSERT_EQUAL(E_NOT_OK, WindowPos_Step(1310100u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(948u, position);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(250u, speed_mm_s);

  /* The service works again: the pending pulses are taken in, position 944, 100 mm/s. */
  stub_result = E_OK;
  TEST_ASSERT_EQUAL(E_OK, WindowPos_Step(1310100u, WINDOWPOS_DIRECTION_CLOSING));
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(944u, position);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetSpeed(&speed_mm_s));
  TEST_ASSERT_EQUAL(100u, speed_mm_s);
}

/* UT-0012: null pointers at the read functions */
static void test_UT_0012_null_pointers(void)
{
  fixture_reset();
  TEST_ASSERT_EQUAL(E_NOT_OK, WindowPos_GetPosition(NULL_PTR));
  TEST_ASSERT_EQUAL(E_NOT_OK, WindowPos_GetSpeed(NULL_PTR));

  /* Also refused once the position is referenced. */
  TEST_ASSERT_EQUAL(0u, stand_still(40u, WINDOWPOS_DIRECTION_OPENING));
  TEST_ASSERT_EQUAL(E_NOT_OK, WindowPos_GetPosition(NULL_PTR));
  TEST_ASSERT_EQUAL(E_NOT_OK, WindowPos_GetSpeed(NULL_PTR));
}

/*------------------------------------------------------------------------------
 * Test program
 *----------------------------------------------------------------------------*/

int main(void)
{
  TEST_RUN("UT-0006", test_UT_0006_state_after_init);
  TEST_RUN("UT-0007", test_UT_0007_referencing_at_open_stop);
  TEST_RUN("UT-0008", test_UT_0008_position_counting_and_limits);
  TEST_RUN("UT-0009", test_UT_0009_speed_from_period_and_elapsed_time);
  TEST_RUN("UT-0010", test_UT_0010_speed_limits);
  TEST_RUN("UT-0011", test_UT_0011_step_refused);
  TEST_RUN("UT-0012", test_UT_0012_null_pointers);
  return TEST_EXIT_CODE();
}
