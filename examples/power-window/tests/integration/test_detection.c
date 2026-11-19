/**
 * @file    test_detection.c
 * @brief   Integration tests of step "detection" (PLN-0004): WindowPos and AntiPinch built
 *          from their units, MotorDrive, WindowCmd and the platform as doubles.
 *
 * One test function per software-integration-test item; the item is the specification.
 */
#include "test_support.h"
#include "Platform_double.h"
#include "MotorDrive_double.h"
#include "WindowPos.h"
#include "AntiPinch.h"

/* ---- helpers: time, Hall edges and 5 ms cycles ------------------------------------- */

static uint32 time_us;            /* time of the last 5 ms cycle */
static uint32 next_edge_us;       /* time stamp of the next Hall edge */
static uint32 edge_period_us;     /* 0: no edges */

static void start(void)
{
  Platform_Reset();
  Platform_Start();
  time_us = 0u;
  edge_period_us = 0u;
}

/** From now on a Hall edge every period_us, the first one period_us after the last cycle. */
static void edges_every(uint32 period_us)
{
  edge_period_us = period_us;
  next_edge_us = time_us + period_us;
}

/** From the next edge on, edges come period_us apart (the pulse train changes its speed). */
static void change_period(uint32 period_us)
{
  next_edge_us = next_edge_us - edge_period_us + period_us;
  edge_period_us = period_us;
}

/** n cycles of 5 ms; the edges of a cycle reach the capture interrupt before the task runs. */
static void cycles(uint32 n)
{
  uint32 i;
  for (i = 0u; i < n; i++)
  {
    time_us += 5000u;
    while ((edge_period_us != 0u) && (next_edge_us <= time_us))
    {
      Platform_HallEdge(next_edge_us);
      next_edge_us += edge_period_us;
    }
    Platform_SetTime(time_us);
    Platform_Task5ms();
  }
}

/** The window rests at the open end stop with the drive opening until the position is referenced. */
static void reference_at_open_end(void)
{
  MotorDriveDouble_SetApplied(1u);
  edge_period_us = 0u;
  cycles(40u);
}

static uint16 position(void)
{
  uint16 value = 0u;
  (void)WindowPos_GetPosition(&value);
  return value;
}

static uint16 speed(void)
{
  uint16 value = 0u;
  (void)WindowPos_GetSpeed(&value);
  return value;
}

static AntiPinch_StatusType detection(void)
{
  AntiPinch_StatusType status = {0u, FALSE, 0u};
  (void)AntiPinch_GetStatus(&status);
  return status;
}

/* ---- test cases --------------------------------------------------------------------- */

/* SIT-0001: Hall edges and the capture time become window position and speed */
static void test_SIT_0001_edges_and_time_base(void)
{
  uint16 value = 0u;
  uint32 last_edge;

  /* Step 1: referenced at the open end stop. */
  start();
  reference_at_open_end();
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&value));
  TEST_ASSERT_EQUAL(960u, value);

  /* Step 2: closing, 100 edges 3000 us apart. */
  MotorDriveDouble_SetApplied(2u);
  edges_every(3000u);
  cycles(60u);
  TEST_ASSERT_EQUAL(860u, position());
  TEST_ASSERT_EQUAL(166u, speed());

  /* Step 3: an edge 399 us after the last accepted one, another 400 us after it. */
  last_edge = time_us;
  edge_period_us = 0u;
  Platform_HallEdge(last_edge + 399u);
  Platform_HallEdge(last_edge + 400u);
  cycles(1u);
  TEST_ASSERT_EQUAL(859u, position());
}

/* SIT-0002: the motor state decides the counting direction and the supervision */
static void test_SIT_0002_motor_state(void)
{
  AntiPinch_StatusType status;

  /* Step 1: referenced. */
  start();
  reference_at_open_end();
  TEST_ASSERT_EQUAL(960u, position());

  /* Step 2: closing, 20 edges. */
  MotorDriveDouble_SetApplied(2u);
  edges_every(3000u);
  cycles(12u);
  TEST_ASSERT_EQUAL(940u, position());

  /* Step 3: stopped, 3 run-out edges. */
  MotorDriveDouble_SetApplied(0u);
  edges_every(3000u);
  cycles(2u);
  TEST_ASSERT_EQUAL(937u, position());

  /* Step 4: opening, 10 edges; no supervision. */
  MotorDriveDouble_SetApplied(1u);
  edges_every(3000u);
  cycles(6u);
  TEST_ASSERT_EQUAL(947u, position());
  status = detection();
  TEST_ASSERT_EQUAL(ANTIPINCH_STATE_IDLE, status.state);

  /* Step 5: closing again; supervision starts. */
  MotorDriveDouble_SetApplied(2u);
  cycles(1u);
  status = detection();
  TEST_ASSERT_EQUAL(ANTIPINCH_STATE_SETTLING, status.state);

  /* Step 6: a motor state outside the specification during the closing movement. */
  MotorDriveDouble_SetApplied(3u);
  edge_period_us = 0u;
  cycles(1u);
  status = detection();
  TEST_ASSERT_EQUAL(TRUE, status.reversal_request);
  TEST_ASSERT_EQUAL(TRUE, MotorDriveDouble_LastReversalRequest());
}

/* SIT-0003: an obstacle reaches the motor actuation in the cycle it is detected */
static void test_SIT_0003_detection_to_motor(void)
{
  AntiPinch_StatusType status;

  /* Step 1: referenced, then 1 s closing at 150 mm/s. */
  start();
  reference_at_open_end();
  MotorDriveDouble_SetApplied(2u);
  edges_every(3333u);
  cycles(200u);
  status = detection();
  TEST_ASSERT_EQUAL(ANTIPINCH_STATE_MONITORING, status.state);
  TEST_ASSERT_EQUAL(150u, MotorDriveDouble_LastSpeed());
  TEST_ASSERT_EQUAL(FALSE, MotorDriveDouble_LastReversalRequest());

  /* Step 2: one cycle at 129 mm/s. */
  change_period(3870u);
  cycles(1u);
  TEST_ASSERT_EQUAL(129u, MotorDriveDouble_LastSpeed());
  TEST_ASSERT_EQUAL(FALSE, detection().reversal_request);
  TEST_ASSERT_EQUAL(FALSE, MotorDriveDouble_LastReversalRequest());

  /* Step 3: a second cycle at 129 mm/s. */
  cycles(1u);
  status = detection();
  TEST_ASSERT_EQUAL(ANTIPINCH_STATE_REVERSING, status.state);
  TEST_ASSERT_EQUAL(TRUE, status.reversal_request);
  TEST_ASSERT_EQUAL(TRUE, MotorDriveDouble_LastReversalRequest());
}

int main(void)
{
  TEST_RUN("SIT-0001", test_SIT_0001_edges_and_time_base);
  TEST_RUN("SIT-0002", test_SIT_0002_motor_state);
  TEST_RUN("SIT-0003", test_SIT_0003_detection_to_motor);
  return TEST_EXIT_CODE();
}
