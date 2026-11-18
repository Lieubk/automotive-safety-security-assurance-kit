/**
 * @file    SchM_WindowPos.h
 * @brief   Host stand-in for the exclusive area services of component WindowPos.
 *
 * On the target the basic software platform (CMP-0006) generates this header
 * from its configuration and implements the two services as a lock of the Hall
 * capture interrupt. On the host each test program defines them itself, which
 * lets a test observe that the area is entered and left. Test equipment, not
 * product code.
 */
#ifndef SCHM_WINDOWPOS_H
#define SCHM_WINDOWPOS_H

/** Enter exclusive area HallData: the Hall capture interrupt cannot run until the area is left. */
void SchM_Enter_WindowPos_HallData(void);

/** Leave exclusive area HallData. */
void SchM_Exit_WindowPos_HallData(void);

#endif /* SCHM_WINDOWPOS_H */
