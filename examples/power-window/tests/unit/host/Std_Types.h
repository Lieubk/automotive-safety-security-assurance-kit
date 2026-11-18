/**
 * @file    Std_Types.h
 * @brief   Host stand-in for the standard types header of the basic software.
 *
 * On the target this header comes with the basic software platform (CMP-0006).
 * The stand-in defines only what the delivered units use, so that they compile
 * and run on a development host. It is test equipment, not product code.
 */
#ifndef STD_TYPES_H
#define STD_TYPES_H

#include <stdint.h>

/** Unsigned integer of exactly 8 bits. */
typedef uint8_t uint8;
/** Unsigned integer of exactly 16 bits. */
typedef uint16_t uint16;
/** Unsigned integer of exactly 32 bits. */
typedef uint32_t uint32;
/** Truth value; holds TRUE or FALSE only. */
typedef uint8_t boolean;
/** Result of a service function; holds E_OK or E_NOT_OK. */
typedef uint8_t Std_ReturnType;

#define TRUE      ((boolean)1u)
#define FALSE     ((boolean)0u)
#define E_OK      ((Std_ReturnType)0u)
#define E_NOT_OK  ((Std_ReturnType)1u)
#define NULL_PTR  ((void *)0)

#endif /* STD_TYPES_H */
