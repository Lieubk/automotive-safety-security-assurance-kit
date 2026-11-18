/**
 * @file    test_support.h
 * @brief   Minimal assertion and reporting support for the unit test programs.
 *
 * A test case is a function without parameters. TEST_ASSERT... records the
 * first failed check of the running test case and leaves the test function.
 * TEST_RUN prints one line per test case:
 *
 *   UT-0001 PASS
 *   UT-0001 FAIL <file>:<line>
 *
 * Include this header in exactly one source file per test program.
 */
#ifndef TEST_SUPPORT_H
#define TEST_SUPPORT_H

#include <stdio.h>

/** File of the first failed check of the running test case; null while none failed. */
static const char *test_failed_file = 0;
/** Line of the first failed check of the running test case. */
static int test_failed_line = 0;
/** Number of failed test cases of the program. */
static int test_failed_count = 0;

/** Check a condition; on failure record the location and leave the test function. */
#define TEST_ASSERT(condition) \
  do \
  { \
    if (!(condition)) \
    { \
      test_failed_file = __FILE__; \
      test_failed_line = __LINE__; \
      return; \
    } \
  } while (0)

/** Check two unsigned integer values of up to 32 bits for equality. */
#define TEST_ASSERT_EQUAL(expected, actual) \
  TEST_ASSERT(((unsigned long)(expected)) == ((unsigned long)(actual)))

/** Run one test case and print its verdict line. */
#define TEST_RUN(id, function) \
  do \
  { \
    test_failed_file = 0; \
    test_failed_line = 0; \
    function(); \
    if (test_failed_file == 0) \
    { \
      printf("%s PASS\n", (id)); \
    } \
    else \
    { \
      printf("%s FAIL %s:%d\n", (id), test_failed_file, test_failed_line); \
      test_failed_count++; \
    } \
  } while (0)

/** Exit code of the test program: 0 when every test case passed, 1 otherwise. */
#define TEST_EXIT_CODE() ((test_failed_count == 0) ? 0 : 1)

#endif /* TEST_SUPPORT_H */
