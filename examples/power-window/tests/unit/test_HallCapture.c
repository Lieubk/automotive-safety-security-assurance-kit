/**
 * @file    test_HallCapture.c
 * @brief   Unit tests of unit HallCapture (UNT-0001), test cases UT-0001 to UT-0005.
 *
 * Built from this file and src/windowpos/HallCapture.c. The exclusive area
 * services are defined here and count their calls.
 */
#include "test_support.h"
#include "HallCapture.h"
#include "SchM_WindowPos.h"

/*------------------------------------------------------------------------------
 * Test doubles
 *----------------------------------------------------------------------------*/

static unsigned int exclusive_enter_calls = 0u;
static unsigned int exclusive_exit_calls = 0u;
static unsigned int exclusive_depth = 0u;
static unsigned int exclusive_depth_max = 0u;

void SchM_Enter_WindowPos_HallData(void)
{
  exclusive_enter_calls++;
  exclusive_depth++;
  if (exclusive_depth > exclusive_depth_max)
  {
    exclusive_depth_max = exclusive_depth;
  }
}

void SchM_Exit_WindowPos_HallData(void)
{
  exclusive_exit_calls++;
  exclusive_depth--;
}

static void exclusive_reset(void)
{
  exclusive_enter_calls = 0u;
  exclusive_exit_calls = 0u;
  exclusive_depth = 0u;
  exclusive_depth_max = 0u;
}

/*------------------------------------------------------------------------------
 * Test cases
 *----------------------------------------------------------------------------*/

/* UT-0001: first edge after initialisation */
static void test_UT_0001_first_edge_after_init(void)
{
  HallCapture_SnapshotType snapshot;

  HallCapture_Init();
  TEST_ASSERT_EQUAL(E_OK, HallCapture_GetSnapshot(&snapshot));
  TEST_ASSERT_EQUAL(0u, snapshot.pulse_count);
  TEST_ASSERT_EQUAL(0u, snapshot.rejected_count);
  TEST_ASSERT_EQUAL(0u, snapshot.period_us);

  HallCapture_OnEdge(1000u);
  TEST_ASSERT_EQUAL(E_OK, HallCapture_GetSnapshot(&snapshot));
  TEST_ASSERT_EQUAL(1u, snapshot.pulse_count);
  TEST_ASSERT_EQUAL(0u, snapshot.rejected_count);
  TEST_ASSERT_EQUAL(1000u, snapshot.last_edge_us);
  TEST_ASSERT_EQUAL(0u, snapshot.period_us);

  /* A second initialisation clears everything, including the memory of the first edge. */
  HallCapture_OnEdge(5000u);
  HallCapture_Init();
  TEST_ASSERT_EQUAL(E_OK, HallCapture_GetSnapshot(&snapshot));
  TEST_ASSERT_EQUAL(0u, snapshot.pulse_count);
  TEST_ASSERT_EQUAL(0u, snapshot.last_edge_us);
  TEST_ASSERT_EQUAL(0u, snapshot.period_us);

  HallCapture_OnEdge(5100u);
  TEST_ASSERT_EQUAL(E_OK, HallCapture_GetSnapshot(&snapshot));
  TEST_ASSERT_EQUAL(1u, snapshot.pulse_count);
  TEST_ASSERT_EQUAL(0u, snapshot.rejected_count);
  TEST_ASSERT_EQUAL(0u, snapshot.period_us);
}

/* UT-0002: pulse period, also across a wrap of the capture timer */
static void test_UT_0002_period_and_timer_wrap(void)
{
  HallCapture_SnapshotType snapshot;

  HallCapture_Init();
  HallCapture_OnEdge(10000u);
  HallCapture_OnEdge(13333u);
  TEST_ASSERT_EQUAL(E_OK, HallCapture_GetSnapshot(&snapshot));
  TEST_ASSERT_EQUAL(2u, snapshot.pulse_count);
  TEST_ASSERT_EQUAL(13333u, snapshot.last_edge_us);
  TEST_ASSERT_EQUAL(3333u, snapshot.period_us);

  HallCapture_OnEdge(20000u);
  TEST_ASSERT_EQUAL(E_OK, HallCapture_GetSnapshot(&snapshot));
  TEST_ASSERT_EQUAL(3u, snapshot.pulse_count);
  TEST_ASSERT_EQUAL(6667u, snapshot.period_us);

  /* 0xFFFFFF00 -> 0x00000F00: 256 us before the wrap plus 3840 us after it. */
  HallCapture_Init();
  HallCapture_OnEdge(0xFFFFFF00u);
  HallCapture_OnEdge(0x00000F00u);
  TEST_ASSERT_EQUAL(E_OK, HallCapture_GetSnapshot(&snapshot));
  TEST_ASSERT_EQUAL(2u, snapshot.pulse_count);
  TEST_ASSERT_EQUAL(0x00000F00u, snapshot.last_edge_us);
  TEST_ASSERT_EQUAL(4096u, snapshot.period_us);
}

/* UT-0003: shortest accepted pulse interval */
static void test_UT_0003_minimum_interval_boundary(void)
{
  HallCapture_SnapshotType snapshot;

  HallCapture_Init();
  HallCapture_OnEdge(1000u);

  /* 399 us after the accepted edge: rejected, nothing but the rejected counter changes. */
  HallCapture_OnEdge(1399u);
  TEST_ASSERT_EQUAL(E_OK, HallCapture_GetSnapshot(&snapshot));
  TEST_ASSERT_EQUAL(1u, snapshot.pulse_count);
  TEST_ASSERT_EQUAL(1u, snapshot.rejected_count);
  TEST_ASSERT_EQUAL(1000u, snapshot.last_edge_us);
  TEST_ASSERT_EQUAL(0u, snapshot.period_us);

  /* 400 us after the accepted edge: accepted; the rejected edge does not shorten the period. */
  HallCapture_OnEdge(1400u);
  TEST_ASSERT_EQUAL(E_OK, HallCapture_GetSnapshot(&snapshot));
  TEST_ASSERT_EQUAL(2u, snapshot.pulse_count);
  TEST_ASSERT_EQUAL(1u, snapshot.rejected_count);
  TEST_ASSERT_EQUAL(1400u, snapshot.last_edge_us);
  TEST_ASSERT_EQUAL(400u, snapshot.period_us);

  /* The same time stamp again (interval 0): rejected. */
  HallCapture_OnEdge(1400u);
  TEST_ASSERT_EQUAL(E_OK, HallCapture_GetSnapshot(&snapshot));
  TEST_ASSERT_EQUAL(2u, snapshot.pulse_count);
  TEST_ASSERT_EQUAL(2u, snapshot.rejected_count);
  TEST_ASSERT_EQUAL(400u, snapshot.period_us);
}

/* UT-0004: limits of the pulse counter and of the rejected edge counter */
static void test_UT_0004_counter_limits(void)
{
  HallCapture_SnapshotType snapshot;
  unsigned long edge;

  /* 65535 accepted edges, 1000 us apart: the counter is at its largest value. */
  HallCapture_Init();
  for (edge = 0u; edge < 65535u; edge++)
  {
    HallCapture_OnEdge((uint32)(edge * 1000u));
  }
  TEST_ASSERT_EQUAL(E_OK, HallCapture_GetSnapshot(&snapshot));
  TEST_ASSERT_EQUAL(65535u, snapshot.pulse_count);

  /* The next two edges wrap it to 0 and then to 1. */
  HallCapture_OnEdge((uint32)(65535u * 1000u));
  TEST_ASSERT_EQUAL(E_OK, HallCapture_GetSnapshot(&snapshot));
  TEST_ASSERT_EQUAL(0u, snapshot.pulse_count);
  HallCapture_OnEdge((uint32)(65536u * 1000u));
  TEST_ASSERT_EQUAL(E_OK, HallCapture_GetSnapshot(&snapshot));
  TEST_ASSERT_EQUAL(1u, snapshot.pulse_count);
  TEST_ASSERT_EQUAL(1000u, snapshot.period_us);
  TEST_ASSERT_EQUAL(0u, snapshot.rejected_count);

  /* 65535 rejected edges: the counter is at its limit and stays there. */
  HallCapture_Init();
  HallCapture_OnEdge(0u);
  for (edge = 0u; edge < 65535u; edge++)
  {
    HallCapture_OnEdge(1u);
  }
  TEST_ASSERT_EQUAL(E_OK, HallCapture_GetSnapshot(&snapshot));
  TEST_ASSERT_EQUAL(65535u, snapshot.rejected_count);
  HallCapture_OnEdge(1u);
  TEST_ASSERT_EQUAL(E_OK, HallCapture_GetSnapshot(&snapshot));
  TEST_ASSERT_EQUAL(65535u, snapshot.rejected_count);
  TEST_ASSERT_EQUAL(1u, snapshot.pulse_count);
}

/* UT-0005: snapshot inside the exclusive area, and null pointer */
static void test_UT_0005_snapshot_and_null_pointer(void)
{
  HallCapture_SnapshotType snapshot;

  HallCapture_Init();
  HallCapture_OnEdge(2000u);
  HallCapture_OnEdge(5000u);
  HallCapture_OnEdge(5100u);

  exclusive_reset();
  TEST_ASSERT_EQUAL(E_OK, HallCapture_GetSnapshot(&snapshot));
  TEST_ASSERT_EQUAL(1u, exclusive_enter_calls);
  TEST_ASSERT_EQUAL(1u, exclusive_exit_calls);
  TEST_ASSERT_EQUAL(1u, exclusive_depth_max);
  TEST_ASSERT_EQUAL(0u, exclusive_depth);
  TEST_ASSERT_EQUAL(2u, snapshot.pulse_count);
  TEST_ASSERT_EQUAL(1u, snapshot.rejected_count);
  TEST_ASSERT_EQUAL(5000u, snapshot.last_edge_us);
  TEST_ASSERT_EQUAL(3000u, snapshot.period_us);

  /* Null pointer: refused before the exclusive area is entered. */
  exclusive_reset();
  TEST_ASSERT_EQUAL(E_NOT_OK, HallCapture_GetSnapshot(NULL_PTR));
  TEST_ASSERT_EQUAL(0u, exclusive_enter_calls);
  TEST_ASSERT_EQUAL(0u, exclusive_exit_calls);
}

/*------------------------------------------------------------------------------
 * Test program
 *----------------------------------------------------------------------------*/

int main(void)
{
  TEST_RUN("UT-0001", test_UT_0001_first_edge_after_init);
  TEST_RUN("UT-0002", test_UT_0002_period_and_timer_wrap);
  TEST_RUN("UT-0003", test_UT_0003_minimum_interval_boundary);
  TEST_RUN("UT-0004", test_UT_0004_counter_limits);
  TEST_RUN("UT-0005", test_UT_0005_snapshot_and_null_pointer);
  return TEST_EXIT_CODE();
}
