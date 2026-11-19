/**
 * @file    test_application.c
 * @brief   Integration tests of step "application" (PLN-0004): the complete application -
 *          WindowPos and AntiPinch from their units, WindowCmd and MotorDrive as received -
 *          with the platform as a double.
 *
 * One test function per software-integration-test item; the item is the specification.
 */
#include "test_support.h"
#include "Platform_double.h"
#include "WindowPos.h"
#include "AntiPinch.h"
#include "MotorDrive.h"

/* ---- helpers: time, Hall edges, 5 ms and 20 ms tasks ------------------------------- */

static uint32 time_us;            /* time of the last 5 ms cycle */
static uint32 cycle_count;        /* 5 ms cycles since the start */
static uint32 next_edge_us;       /* time stamp of the next Hall edge */
static uint32 edge_period_us;     /* 0: no edges */

static void start(void)
{
  Platform_Reset();
  Platform_Start();
  time_us = 0u;
  cycle_count = 0u;
  edge_period_us = 0u;
}

static void edges_every(uint32 period_us)
{
  edge_period_us = period_us;
  next_edge_us = time_us + period_us;
}

static void change_period(uint32 period_us)
{
  next_edge_us = next_edge_us - edge_period_us + period_us;
  edge_period_us = period_us;
}

/** One 5 ms cycle; with_command: every fourth cycle the 20 ms task runs after it, as in VIEW-0004. */
static void cycle(boolean with_command)
{
  time_us += 5000u;
  while ((edge_period_us != 0u) && (next_edge_us <= time_us))
  {
    Platform_HallEdge(next_edge_us);
    next_edge_us += edge_period_us;
  }
  Platform_SetTime(time_us);
  Platform_Task5ms();
  cycle_count++;
  if ((with_command == TRUE) && ((cycle_count % 4u) == 0u))
  {
    Platform_Task20ms();
  }
}

static void cycles(uint32 n)
{
  uint32 i;
  for (i = 0u; i < n; i++)
  {
    cycle(TRUE);
  }
}

static AntiPinch_StatusType detection(void)
{
  AntiPinch_StatusType status = {0u, FALSE, 0u};
  (void)AntiPinch_GetStatus(&status);
  return status;
}

/* ---- test cases --------------------------------------------------------------------- */

/* SIT-0004: the switch request reaches the bridge through command logic and motor actuation */
static void test_SIT_0004_switch_to_bridge(void)
{
  /* Step 1: CLOSE for 40 ms. */
  start();
  edges_every(3333u);
  Platform_SetSwitchRequest(2u);
  cycles(8u);
  TEST_ASSERT_EQUAL(2u, Platform_BridgeDirection());
  TEST_ASSERT_EQUAL(40u, Platform_BridgeDuty());
  TEST_ASSERT_EQUAL(2u, MotorDrive_GetAppliedDirection());

  /* Step 2: NONE for 40 ms. */
  Platform_SetSwitchRequest(0u);
  cycles(8u);
  TEST_ASSERT_EQUAL(0u, Platform_BridgeDirection());

  /* Step 3: OPEN for 40 ms. */
  Platform_SetSwitchRequest(1u);
  cycles(8u);
  TEST_ASSERT_EQUAL(1u, Platform_BridgeDirection());

  /* Step 4: the invalid value 7 the stack delivers after a reception time-out. */
  Platform_SetSwitchRequest(7u);
  cycles(8u);
  TEST_ASSERT_EQUAL(0u, Platform_BridgeDirection());

  /* Step 5: OPEN, then the reserved value 5. */
  Platform_SetSwitchRequest(1u);
  cycles(8u);
  TEST_ASSERT_EQUAL(1u, Platform_BridgeDirection());
  Platform_SetSwitchRequest(5u);
  cycles(8u);
  TEST_ASSERT_EQUAL(0u, Platform_BridgeDirection());
}

/* SIT-0005: the movement command operation, every return value */
static void test_SIT_0005_movement_command(void)
{
  /* Step 1: closing at 100 %. */
  start();
  edges_every(3333u);
  TEST_ASSERT_EQUAL(E_OK, MotorDrive_RequestMovement(2u, 100u));
  cycle(FALSE);
  TEST_ASSERT_EQUAL(2u, Platform_BridgeDirection());
  TEST_ASSERT_EQUAL(30u, Platform_BridgeDuty());

  /* Step 2: direction 3. */
  TEST_ASSERT_EQUAL(E_NOT_OK, MotorDrive_RequestMovement(3u, 100u));
  cycle(FALSE);
  TEST_ASSERT_EQUAL(0u, Platform_BridgeDirection());

  /* Step 3: opening at 29 %, then at 30 %. */
  TEST_ASSERT_EQUAL(E_NOT_OK, MotorDrive_RequestMovement(1u, 29u));
  cycle(FALSE);
  TEST_ASSERT_EQUAL(0u, Platform_BridgeDirection());
  TEST_ASSERT_EQUAL(E_OK, MotorDrive_RequestMovement(1u, 30u));
  cycle(FALSE);
  TEST_ASSERT_EQUAL(1u, Platform_BridgeDirection());
  TEST_ASSERT_EQUAL(30u, Platform_BridgeDuty());

  /* Step 4: opening at 101 %. */
  TEST_ASSERT_EQUAL(E_NOT_OK, MotorDrive_RequestMovement(1u, 101u));
  cycle(FALSE);
  TEST_ASSERT_EQUAL(0u, Platform_BridgeDirection());

  /* Step 5: stopped, duty 0. */
  TEST_ASSERT_EQUAL(E_OK, MotorDrive_RequestMovement(0u, 0u));
  cycle(FALSE);
  TEST_ASSERT_EQUAL(0u, Platform_BridgeDirection());
}

/* SIT-0006: an obstacle reverses the bridge in the cycle it is detected and ends the automatic closing */
static void test_SIT_0006_reversal_through_the_application(void)
{
  uint16 position = 0u;
  uint32 i;
  boolean reversed = FALSE;

  /* Step 1: OPEN for 300 ms at the open end stop, no edges. */
  start();
  Platform_SetSwitchRequest(1u);
  cycles(60u);
  TEST_ASSERT_EQUAL(E_OK, WindowPos_GetPosition(&position));
  TEST_ASSERT_EQUAL(960u, position);
  TEST_ASSERT_EQUAL(0u, Platform_BridgeDirection());

  /* Step 2: NONE for 40 ms, AUTO_CLOSE for 60 ms, NONE; edges at 150 mm/s; 1 s in all. */
  Platform_SetSwitchRequest(0u);
  cycles(8u);
  Platform_SetSwitchRequest(3u);
  edges_every(3333u);
  cycles(12u);
  Platform_SetSwitchRequest(0u);
  cycles(188u);
  TEST_ASSERT_EQUAL(2u, Platform_BridgeDirection());
  TEST_ASSERT_EQUAL(100u, Platform_BridgeDuty());
  TEST_ASSERT_EQUAL(ANTIPINCH_STATE_MONITORING, detection().state);

  /* Step 3: edges at 129 mm/s, cycle by cycle until the reversal request is set. */
  change_period(3870u);
  for (i = 0u; (i < 2u) && (reversed == FALSE); i++)
  {
    cycle(TRUE);
    reversed = detection().reversal_request;
  }
  TEST_ASSERT_EQUAL(TRUE, reversed);
  TEST_ASSERT_EQUAL(1u, Platform_BridgeDirection());
  TEST_ASSERT_EQUAL(100u, Platform_BridgeDuty());

  /* Step 4: edges at 150 mm/s for 1 s, then none for 100 ms. */
  change_period(3333u);
  cycles(200u);
  edge_period_us = 0u;
  cycles(20u);
  TEST_ASSERT_EQUAL(FALSE, detection().reversal_request);
  TEST_ASSERT_EQUAL(0u, Platform_BridgeDirection());
  TEST_ASSERT_EQUAL(0u, MotorDrive_GetAppliedDirection());
}

/* SIT-0007: a fault of the bridge driver is published as standstill and the command is repeated */
static void test_SIT_0007_bridge_fault(void)
{
  uint32 calls;

  /* Step 1: CLOSE for 40 ms. */
  start();
  edges_every(3333u);
  Platform_SetSwitchRequest(2u);
  cycles(8u);
  TEST_ASSERT_EQUAL(2u, MotorDrive_GetAppliedDirection());

  /* Step 2: the bridge driver answers E_NOT_OK for one cycle. */
  Platform_SetBridgeResult(E_NOT_OK);
  calls = Platform_BridgeCalls();
  cycle(FALSE);
  TEST_ASSERT_EQUAL(calls + 1u, Platform_BridgeCalls());
  TEST_ASSERT_EQUAL(0u, MotorDrive_GetAppliedDirection());

  /* Step 3: one more cycle with the fault. */
  cycle(FALSE);
  TEST_ASSERT_EQUAL(calls + 2u, Platform_BridgeCalls());
  TEST_ASSERT_EQUAL(2u, Platform_BridgeDirection());
  TEST_ASSERT_EQUAL(0u, MotorDrive_GetAppliedDirection());

  /* Step 4: the fault is gone. */
  Platform_SetBridgeResult(E_OK);
  cycle(FALSE);
  TEST_ASSERT_EQUAL(2u, MotorDrive_GetAppliedDirection());
}

int main(void)
{
  TEST_RUN("SIT-0004", test_SIT_0004_switch_to_bridge);
  TEST_RUN("SIT-0005", test_SIT_0005_movement_command);
  TEST_RUN("SIT-0006", test_SIT_0006_reversal_through_the_application);
  TEST_RUN("SIT-0007", test_SIT_0007_bridge_fault);
  return TEST_EXIT_CODE();
}
