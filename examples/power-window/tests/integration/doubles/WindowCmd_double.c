/**
 * @file    WindowCmd_double.c
 * @brief   Double of WindowCmd (CMP-0002) for integration steps that do not integrate it.
 *
 * Test equipment. Same functions as reused/windowcmd/WindowCmd.h; the command logic
 * only consumes interfaces, so the double does nothing.
 */
#include "WindowCmd.h"

void WindowCmd_Init(void)
{
}

void WindowCmd_Step(uint8 switch_request)
{
  (void)switch_request;
}
