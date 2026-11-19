/**
 * @file    test_qualification.c
 * @brief   Software qualification tests (PLN-0005): the complete software of the last
 *          integration step against the software requirements.
 *
 * Stimuli: the Hall signal as a pulse train of given period (signal generator, open
 * loop), the switch request as the communication stack delivers it, a fault of the
 * bridge driver, and - for SWR-0006 only - a wrong value of an input of the obstacle
 * detection, as a measurement and calibration tool would overwrite it. Observed: the
 * bridge output, and the measurement points named in PLN-0005 (window position and
 * speed, detection status, movement command). One test function per
 * software-qualification-test item; the item is the specification.
 */
#include "test_support.h"
#include "Platform_double.h"
#include "WindowPos.h"
#include "AntiPinch.h"
#include "MotorDrive.h"

#define SWITCH_NONE   0u
#define SWITCH_OPEN   1u
#define SWITCH_CLOSE  2u
#define SWITCH_AUTO   3u
#define NO_LIMIT      0xFFFFFFFFu

/* ---- stimulus and time -------------------------------------------------------------- */

static uint32 time_us;            /* time of the last 5 ms cycle */
static uint32 cycle_count;        /* 5 ms cycles since the start; the 20 ms task follows every fourth */
static uint32 next_edge_us;
static uint32 edge_period_us;     /* 0: no pulses */
static uint32 edges_left;         /* pulses still to come, or NO_LIMIT */

static void start(void)
{
  Platform_Reset();
  Platform_Start();
  time_us = 0u;
  cycle_count = 0u;
  edge_period_us = 0u;
}

/** Pulses from one period after the last cycle on, `count` of them (NO_LIMIT: until stopped). */
static void pulses(uint32 period_us, uint32 count)
{
  edge_period_us = period_us;
  next_edge_us = time_us + period_us;
  edges_left = count;
}

/** From the next pulse on, a new period (the speed of the glass changes). */
static void change_period(uint32 period_us)
{
  next_edge_us = next_edge_us - edge_period_us + period_us;
  edge_period_us = period_us;
}

static void no_pulses(void)
{
  edge_period_us = 0u;
}

static void cycle(void)
{
  time_us += 5000u;
  while ((edge_period_us != 0u) && (edges_left != 0u) && (next_edge_us <= time_us))
  {
    Platform_HallEdge(next_edge_us);
    next_edge_us += edge_period_us;
    if (edges_left != NO_LIMIT)
    {
      edges_left--;
    }
  }
  Platform_SetTime(time_us);
  Platform_Task5ms();
  cycle_count++;
  if ((cycle_count % 4u) == 0u)
  {
    Platform_Task20ms();
  }
}

static void cycles(uint32 n)
{
  uint32 i;
  for (i = 0u; i < n; i++)
  {
    cycle();
  }
}

/** Runs cycles until the 20 ms task has just run, so that a switch request set now is read 20 ms later. */
static void sync_command(void)
{
  while ((cycle_count % 4u) != 0u)
  {
    cycle();
  }
}

/* ---- measurement points --------------------------------------------------------------- */

static uint16 position(void)
{
  uint16 value = 0u;
  (void)WindowPos_GetPosition(&value);
  return value;
}

static boolean available(void)
{
  uint16 value = 0u;
  return (WindowPos_GetPosition(&value) == E_OK) ? TRUE : FALSE;
}

static uint16 speed(void)
{
  uint16 value = 0u;
  (void)WindowPos_GetSpeed(&value);
  return value;
}

static boolean request(void)
{
  AntiPinch_StatusType status = {0u, FALSE, 0u};
  (void)AntiPinch_GetStatus(&status);
  return status.reversal_request;
}

static uint8 command(void)
{
  return MotorDrive_GetCommandedDirection();
}

/* ---- situations ------------------------------------------------------------------------- */

/** Start, then the window at the open end stop with the switch on OPEN for 300 ms: referenced at 480 mm. */
static void start_referenced(void)
{
  start();
  Platform_SetSwitchRequest(SWITCH_OPEN);
  cycles(60u);
  Platform_SetSwitchRequest(SWITCH_NONE);
  cycles(8u);
}

/**
 * A movement by the switch with exactly n pulses 3 ms apart (n a multiple of 20): the
 * pulses start 3 ms after the drive starts, and the drive stops in the cycle of the last
 * pulse, so the glass stands when the pulses end.
 */
static void move_pulses(uint8 switch_request, uint32 n)
{
  sync_command();
  Platform_SetSwitchRequest(switch_request);
  cycles(5u);                                   /* read at +4, driven from +5 */
  pulses(3000u, n);
  cycles(((3u * n) / 5u) - 2u);
  Platform_SetSwitchRequest(SWITCH_NONE);
  cycles(2u);                                   /* read at the next command cycle, stopped with the last pulse */
}

/** Closing by the switch at 150 mm/s until the position is `limit` counts or less; the drive keeps closing. */
static void close_to(uint16 limit)
{
  uint32 i;
  Platform_SetSwitchRequest(SWITCH_CLOSE);
  while (Platform_BridgeDirection() != 2u)
  {
    cycle();
  }
  pulses(3333u, NO_LIMIT);
  for (i = 0u; (i < 2000u) && (position() > limit); i++)
  {
    cycle();
  }
}

/** Speed drop to 129 mm/s; the number of cycles until the reversal request is set (at most `limit`). */
static uint32 drop_until_request(uint32 limit)
{
  uint32 n = 0u;
  change_period(3870u);
  while ((request() == FALSE) && (n < limit))
  {
    cycle();
    n++;
  }
  return n;
}

/* ---- test cases ------------------------------------------------------------------------- */

/* SQT-0001: window opening from Hall pulses (SWR-0001) */
static void test_SQT_0001_opening_from_pulses(void)
{
  uint16 before;

  /* Step 1: referenced at 480.0 mm. */
  start_referenced();
  TEST_ASSERT_EQUAL(960u, position());

  /* Step 2: 100 pulses while the drive closes. */
  move_pulses(SWITCH_CLOSE, 100u);
  TEST_ASSERT_EQUAL(0u, Platform_BridgeDirection());
  TEST_ASSERT_EQUAL(860u, position());

  /* Step 3: 20 pulses while the drive opens. */
  move_pulses(SWITCH_OPEN, 20u);
  TEST_ASSERT_EQUAL(880u, position());

  /* Step 4: 3 pulses after the drive has stopped. */
  pulses(3000u, 3u);
  cycles(4u);
  TEST_ASSERT_EQUAL(883u, position());

  /* Step 5: a pulse 399 us after a counted pulse, then a pulse 400 us after a counted pulse. */
  no_pulses();
  before = position();
  Platform_HallEdge(time_us + 1000u);
  Platform_HallEdge(time_us + 1399u);
  cycle();
  TEST_ASSERT_EQUAL(before + 1u, position());
  Platform_HallEdge(time_us + 1000u);
  Platform_HallEdge(time_us + 1400u);
  cycle();
  TEST_ASSERT_EQUAL(before + 3u, position());

  /* Step 6: 120 pulses while opening, 1000 pulses while closing. */
  Platform_SetSwitchRequest(SWITCH_OPEN);
  cycles(8u);
  pulses(3000u, 120u);
  cycles(80u);
  TEST_ASSERT_EQUAL(960u, position());
  Platform_SetSwitchRequest(SWITCH_NONE);
  cycles(8u);
  Platform_SetSwitchRequest(SWITCH_CLOSE);
  cycles(8u);
  pulses(3000u, 1000u);
  cycles(610u);
  TEST_ASSERT_EQUAL(0u, position());
  TEST_ASSERT_EQUAL(FALSE, request());
}

/* SQT-0002: reference of the window opening at the open end stop (SWR-0002) */
static void test_SQT_0002_reference(void)
{
  uint16 value = 0u;

  /* Step 1: closing with pulses, stopped, no pulses. */
  start();
  Platform_SetSwitchRequest(SWITCH_CLOSE);
  cycles(5u);
  pulses(3333u, NO_LIMIT);
  cycles(35u);
  Platform_SetSwitchRequest(SWITCH_NONE);
  cycles(8u);
  no_pulses();
  cycles(60u);
  TEST_ASSERT_EQUAL(E_NOT_OK, WindowPos_GetPosition(&value));
  TEST_ASSERT_EQUAL(65535u, value);

  /* Step 2: OPEN at the open end stop; 195 ms and 200 ms after the drive started opening. */
  Platform_SetSwitchRequest(SWITCH_OPEN);
  while (Platform_BridgeDirection() != 1u)
  {
    cycle();
  }
  cycles(39u);
  TEST_ASSERT_EQUAL(FALSE, available());
  cycle();
  TEST_ASSERT_EQUAL(TRUE, available());
  TEST_ASSERT_EQUAL(960u, position());

  /* Step 3: after a new start, opening 195 ms, stopped 5 ms by a bridge fault, opening again. */
  start();
  Platform_SetSwitchRequest(SWITCH_OPEN);
  while (Platform_BridgeDirection() != 1u)
  {
    cycle();
  }
  cycles(38u);
  Platform_SetBridgeResult(E_NOT_OK);
  cycle();
  Platform_SetBridgeResult(E_OK);
  cycles(2u);
  TEST_ASSERT_EQUAL(FALSE, available());
  cycles(38u);
  TEST_ASSERT_EQUAL(FALSE, available());

  /* Step 4: referenced, closed to 430.0 mm, then opening at 0 mm/s for 200 ms. */
  start_referenced();
  move_pulses(SWITCH_CLOSE, 100u);
  TEST_ASSERT_EQUAL(860u, position());
  cycles(12u);                                  /* 60 ms without pulses: the speed is 0 */
  TEST_ASSERT_EQUAL(0u, speed());
  Platform_SetSwitchRequest(SWITCH_OPEN);
  while (Platform_BridgeDirection() != 1u)
  {
    cycle();
  }
  cycles(39u);
  TEST_ASSERT_EQUAL(860u, position());
  cycle();
  TEST_ASSERT_EQUAL(960u, position());
}

/* SQT-0003: window speed (SWR-0003) */
static void test_SQT_0003_speed(void)
{
  uint16 value;

  /* Step 1: pulses 3333 us apart, the last one 0.5 ms before a cycle. */
  start();
  edge_period_us = 3333u;
  next_edge_us = time_us + 50000u - 500u - (9u * 3333u);
  edges_left = 10u;
  cycles(10u);
  value = speed();
  TEST_ASSERT((value >= 149u) && (value <= 151u));

  /* Step 2: pulses 3333 us apart, the last one at a cycle; then none. */
  edge_period_us = 3333u;
  next_edge_us = time_us + 100000u - (9u * 3333u);
  edges_left = 10u;
  cycles(20u);
  cycle();
  TEST_ASSERT(speed() <= 100u);
  cycle();
  TEST_ASSERT(speed() <= 50u);

  /* Step 3: 50 ms after the last pulse; then one pulse; then a second one. */
  cycles(8u);
  TEST_ASSERT_EQUAL(0u, speed());
  Platform_HallEdge(time_us + 1000u);
  cycle();
  TEST_ASSERT_EQUAL(0u, speed());
  Platform_HallEdge(time_us + 1000u);
  cycle();
  TEST_ASSERT(speed() > 0u);

  /* Step 4: pulses 1000 us apart, then 900 us apart. */
  pulses(1000u, NO_LIMIT);
  cycles(4u);
  TEST_ASSERT_EQUAL(500u, speed());
  change_period(900u);
  cycles(4u);
  TEST_ASSERT_EQUAL(500u, speed());
}

/* SQT-0004: obstacle detection during closing (SWR-0004) */
static void test_SQT_0004_detection(void)
{
  uint32 n;
  uint32 i;
  uint32 speed_x2;
  boolean never = TRUE;

  /* Step 1: closing at 150 mm/s to 300.0 mm, then 129 mm/s. */
  start_referenced();
  close_to(600u);
  TEST_ASSERT_EQUAL(FALSE, request());
  n = drop_until_request(10u);
  TEST_ASSERT(n <= 2u);

  /* Step 2: as step 1, then 130 mm/s for 1 s. */
  start_referenced();
  close_to(600u);
  change_period(3846u);
  for (i = 0u; i < 200u; i++)
  {
    cycle();
    never = (request() == FALSE) ? never : FALSE;
  }
  TEST_ASSERT_EQUAL(TRUE, never);

  /* Step 3: as step 1, then falling by 100 mm/s per second to 100 mm/s, held 0.5 s. */
  start_referenced();
  close_to(600u);
  for (speed_x2 = 300u; speed_x2 > 200u; speed_x2--)
  {
    change_period(1000000u / speed_x2);
    cycle();
    never = (request() == FALSE) ? never : FALSE;
  }
  for (i = 0u; i < 100u; i++)
  {
    cycle();
    never = (request() == FALSE) ? never : FALSE;
  }
  TEST_ASSERT_EQUAL(TRUE, never);

  /* Step 4: the drop at 5.0 mm; at 8.0 mm; with the opening not available. */
  start_referenced();
  close_to(10u);
  TEST_ASSERT_EQUAL(10u, drop_until_request(10u));
  start_referenced();
  close_to(16u);
  TEST_ASSERT(drop_until_request(10u) <= 2u);
  start();
  close_to(0u);                      /* not available: closes until the time limit of the loop */
  TEST_ASSERT(drop_until_request(10u) <= 2u);

  /* Step 5: closing from standstill at 29 mm/s, then at 30 mm/s. */
  start_referenced();
  Platform_SetSwitchRequest(SWITCH_CLOSE);
  while (Platform_BridgeDirection() != 2u)
  {
    cycle();
  }
  pulses(17241u, NO_LIMIT);
  for (n = 0u; (n < 40u) && (request() == FALSE); n++)
  {
    cycle();
  }
  TEST_ASSERT(n <= 22u);
  start_referenced();
  Platform_SetSwitchRequest(SWITCH_CLOSE);
  while (Platform_BridgeDirection() != 2u)
  {
    cycle();
  }
  pulses(16666u, NO_LIMIT);
  for (i = 0u; i < 200u; i++)
  {
    cycle();
    never = (request() == FALSE) ? never : FALSE;
  }
  TEST_ASSERT_EQUAL(TRUE, never);
}

/* SQT-0005: end of the reversal (SWR-0005) */
static void test_SQT_0005_end_of_reversal(void)
{
  uint16 at_set;
  uint32 i;

  /* Step 1: request set at about 300 mm, glass opening at 150 mm/s. */
  start_referenced();
  close_to(600u);
  TEST_ASSERT(drop_until_request(10u) <= 2u);
  at_set = position();
  change_period(3333u);
  for (i = 0u; (i < 400u) && (request() == TRUE); i++)
  {
    TEST_ASSERT(position() < (uint16)(at_set + 240u));
    cycle();
  }
  TEST_ASSERT_EQUAL(FALSE, request());
  TEST_ASSERT(position() >= (uint16)(at_set + 240u));

  /* Step 2: request set at about 400 mm. */
  start_referenced();
  close_to(800u);
  TEST_ASSERT(drop_until_request(10u) <= 2u);
  change_period(3333u);
  for (i = 0u; (i < 400u) && (request() == TRUE); i++)
  {
    TEST_ASSERT(position() < 960u);
    cycle();
  }
  TEST_ASSERT_EQUAL(FALSE, request());
  TEST_ASSERT_EQUAL(960u, position());

  /* Step 3: request set with the opening not available. */
  start();
  close_to(0u);
  TEST_ASSERT(drop_until_request(10u) <= 2u);
  change_period(3333u);
  cycles(399u);
  TEST_ASSERT_EQUAL(TRUE, request());
  cycle();
  TEST_ASSERT_EQUAL(FALSE, request());

  /* Step 4: request set at about 300 mm, glass opening at 40 mm/s. */
  start_referenced();
  close_to(600u);
  TEST_ASSERT(drop_until_request(10u) <= 2u);
  at_set = position();
  change_period(12500u);
  cycles(399u);
  TEST_ASSERT_EQUAL(TRUE, request());
  cycle();
  TEST_ASSERT_EQUAL(FALSE, request());
  TEST_ASSERT((position() > (uint16)(at_set + 150u)) && (position() < (uint16)(at_set + 170u)));
}

/* SQT-0006: reversal when a closing movement cannot be supervised (SWR-0006) */
static void test_SQT_0006_unsupervised_closing(void)
{
  static const uint8 inputs[3] = {PLATFORM_INJECT_POSITION, PLATFORM_INJECT_SPEED, PLATFORM_INJECT_DIRECTION};
  static const uint16 values[3] = {961u, 501u, 3u};
  static const uint32 moments[3] = {0u, 10u, 40u};
  uint32 k;
  uint32 m;

  /* Steps 1 to 3: each wrong value in the first cycle of a closing movement (the direction
   * in the second), after 50 ms and after 200 ms; cleared 2.000 s after the 50 ms case. */
  for (k = 0u; k < 3u; k++)
  {
    for (m = 0u; m < 3u; m++)
    {
      start();
      Platform_SetSwitchRequest(SWITCH_CLOSE);
      while (Platform_BridgeDirection() != 2u)
      {
        cycle();
      }
      pulses(3333u, NO_LIMIT);
      cycles(((k == 2u) && (m == 0u)) ? 1u : moments[m]);
      TEST_ASSERT_EQUAL(FALSE, request());
      Platform_InjectDetectionInput(inputs[k], values[k]);
      cycle();
      Platform_InjectDetectionInput(PLATFORM_INJECT_NONE, 0u);
      TEST_ASSERT_EQUAL(TRUE, request());
      if (m == 1u)
      {
        cycles(399u);
        TEST_ASSERT_EQUAL(TRUE, request());
        cycle();
        TEST_ASSERT_EQUAL(FALSE, request());
      }
    }
  }

  /* Step 4: the same values while the drive is stopped and while it opens. */
  for (k = 0u; k < 3u; k++)
  {
    start();
    cycles(8u);
    Platform_InjectDetectionInput(inputs[k], values[k]);
    cycle();
    Platform_InjectDetectionInput(PLATFORM_INJECT_NONE, 0u);
    TEST_ASSERT_EQUAL(FALSE, request());
    Platform_SetSwitchRequest(SWITCH_OPEN);
    pulses(3333u, NO_LIMIT);
    cycles(20u);
    Platform_InjectDetectionInput(inputs[k], values[k]);
    cycle();
    Platform_InjectDetectionInput(PLATFORM_INJECT_NONE, 0u);
    TEST_ASSERT_EQUAL(FALSE, request());
  }
}

/* SQT-0007: priority of the reversal request (SWR-0007) */
static void test_SQT_0007_reversal_priority(void)
{
  static const uint8 requests[3] = {SWITCH_NONE, SWITCH_OPEN, SWITCH_CLOSE};
  static const uint8 commands[3] = {0u, 1u, 2u};
  uint32 k;
  uint32 i;

  /* Step 1: CLOSE with the opening not available, 150 mm/s for 1 s, then 129 mm/s. */
  start();
  Platform_SetSwitchRequest(SWITCH_CLOSE);
  cycles(5u);
  pulses(3333u, NO_LIMIT);
  cycles(200u);
  TEST_ASSERT_EQUAL(2u, command());
  TEST_ASSERT_EQUAL(2u, Platform_BridgeDirection());
  TEST_ASSERT(drop_until_request(10u) <= 2u);
  TEST_ASSERT_EQUAL(1u, Platform_BridgeDirection());
  TEST_ASSERT_EQUAL(100u, Platform_BridgeDuty());

  /* Step 2: NONE, OPEN, CLOSE for 100 ms each while the request is set. */
  change_period(3333u);
  for (k = 0u; k < 3u; k++)
  {
    Platform_SetSwitchRequest(requests[k]);
    for (i = 0u; i < 20u; i++)
    {
      cycle();
      TEST_ASSERT_EQUAL(TRUE, request());
      TEST_ASSERT_EQUAL(1u, Platform_BridgeDirection());
      TEST_ASSERT_EQUAL(100u, Platform_BridgeDuty());
    }
    TEST_ASSERT_EQUAL(commands[k], command());
  }

  /* Step 3: the cycle in which the request is cleared. */
  for (i = 0u; (i < 400u) && (request() == TRUE); i++)
  {
    cycle();
  }
  TEST_ASSERT_EQUAL(FALSE, request());
  TEST_ASSERT_EQUAL(2u, Platform_BridgeDirection());
}

/* SQT-0008: automatic closing (SWR-0008) */
static void test_SQT_0008_automatic_closing(void)
{
  uint32 n;
  uint32 i;

  /* Step 1: at 300.0 mm, AUTO_CLOSE for 60 ms, then NONE; the glass closes at 150 mm/s to the end stop. */
  start_referenced();
  move_pulses(SWITCH_CLOSE, 360u);
  TEST_ASSERT_EQUAL(600u, position());
  sync_command();
  Platform_SetSwitchRequest(SWITCH_AUTO);
  for (n = 0u; (n < 12u) && (command() != 2u); n++)
  {
    cycle();
  }
  TEST_ASSERT(n <= 8u);
  cycles(12u - n);
  Platform_SetSwitchRequest(SWITCH_NONE);
  pulses(3333u, NO_LIMIT);
  for (i = 0u; (i < 600u) && (position() > 0u); i++)
  {
    cycle();
    TEST_ASSERT_EQUAL(2u, command());
  }
  TEST_ASSERT_EQUAL(0u, position());
  no_pulses();
  for (i = 0u; (i < 40u) && (speed() > 0u); i++)
  {
    cycle();
    TEST_ASSERT_EQUAL(2u, command());
  }
  TEST_ASSERT_EQUAL(0u, speed());
  cycles(39u);                                  /* 195 ms at 0 mm/s */
  TEST_ASSERT_EQUAL(2u, command());
  cycles(5u);                                   /* 220 ms */
  TEST_ASSERT_EQUAL(0u, command());

  /* Step 2: OPEN while closing automatically. */
  start_referenced();
  sync_command();
  Platform_SetSwitchRequest(SWITCH_AUTO);
  cycles(12u);
  Platform_SetSwitchRequest(SWITCH_NONE);
  pulses(3333u, NO_LIMIT);
  cycles(100u);
  TEST_ASSERT_EQUAL(2u, command());
  sync_command();
  Platform_SetSwitchRequest(SWITCH_OPEN);
  cycles(8u);
  TEST_ASSERT(command() != 2u);

  /* Step 3: the reversal request while closing automatically. */
  start_referenced();
  sync_command();
  Platform_SetSwitchRequest(SWITCH_AUTO);
  cycles(12u);
  Platform_SetSwitchRequest(SWITCH_NONE);
  pulses(3333u, NO_LIMIT);
  cycles(200u);
  TEST_ASSERT(drop_until_request(10u) <= 2u);
  cycles(8u);
  TEST_ASSERT_EQUAL(0u, command());
  change_period(3333u);
  for (i = 0u; (i < 400u) && (request() == TRUE); i++)
  {
    cycle();
    TEST_ASSERT_EQUAL(0u, command());
  }
  for (i = 0u; i < 40u; i++)
  {
    cycle();
    TEST_ASSERT_EQUAL(0u, command());
  }

  /* Step 4: AUTO_CLOSE with the opening not available. */
  start();
  Platform_SetSwitchRequest(SWITCH_AUTO);
  cycles(12u);
  Platform_SetSwitchRequest(SWITCH_NONE);
  for (i = 0u; i < 40u; i++)
  {
    cycle();
    TEST_ASSERT_EQUAL(0u, command());
    TEST_ASSERT_EQUAL(0u, Platform_BridgeDirection());
  }
}

/** One manual movement: the request held for 500 ms; the command follows within 40 ms at both ends. */
static void manual(uint8 switch_request, uint8 direction)
{
  uint32 n;
  uint32 i;

  sync_command();
  Platform_SetSwitchRequest(switch_request);
  for (n = 0u; (n < 100u) && (command() != direction); n++)
  {
    cycle();
  }
  TEST_ASSERT(n <= 8u);
  for (i = n; i < 100u; i++)
  {
    cycle();
    TEST_ASSERT_EQUAL(direction, command());
  }
  Platform_SetSwitchRequest(SWITCH_NONE);
  for (n = 0u; (n < 100u) && (command() != 0u); n++)
  {
    cycle();
  }
  TEST_ASSERT(n <= 8u);
  for (i = 0u; i < 40u; i++)
  {
    cycle();
    TEST_ASSERT_EQUAL(0u, command());
  }
}

/* SQT-0009: manual movement (SWR-0009) */
static void test_SQT_0009_manual_movement(void)
{
  uint8 value;
  uint32 n;

  /* Steps 1 and 2: CLOSE for 500 ms; OPEN for 500 ms. */
  start_referenced();
  pulses(3333u, NO_LIMIT);
  manual(SWITCH_CLOSE, 2u);
  manual(SWITCH_OPEN, 1u);

  /* Step 3: OPEN, then each of the values 4 to 7. */
  for (value = 4u; value <= 7u; value++)
  {
    sync_command();
    Platform_SetSwitchRequest(SWITCH_OPEN);
    cycles(20u);
    TEST_ASSERT_EQUAL(1u, command());
    Platform_SetSwitchRequest(value);
    for (n = 0u; (n < 20u) && (command() != 0u); n++)
    {
      cycle();
    }
    TEST_ASSERT(n <= 8u);
  }

  /* Step 4: OPEN, then the frames stop: the stack keeps OPEN for 100 ms, then delivers 7. */
  Platform_SetSwitchRequest(SWITCH_OPEN);
  cycles(20u);
  cycles(20u);
  TEST_ASSERT_EQUAL(1u, command());
  Platform_SetSwitchRequest(7u);
  for (n = 0u; (n < 20u) && (command() != 0u); n++)
  {
    cycle();
  }
  TEST_ASSERT(n <= 8u);
}

int main(void)
{
  TEST_RUN("SQT-0001", test_SQT_0001_opening_from_pulses);
  TEST_RUN("SQT-0002", test_SQT_0002_reference);
  TEST_RUN("SQT-0003", test_SQT_0003_speed);
  TEST_RUN("SQT-0004", test_SQT_0004_detection);
  TEST_RUN("SQT-0005", test_SQT_0005_end_of_reversal);
  TEST_RUN("SQT-0006", test_SQT_0006_unsupervised_closing);
  TEST_RUN("SQT-0007", test_SQT_0007_reversal_priority);
  TEST_RUN("SQT-0008", test_SQT_0008_automatic_closing);
  TEST_RUN("SQT-0009", test_SQT_0009_manual_movement);
  return TEST_EXIT_CODE();
}
