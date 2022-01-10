 /**
  * This file contains the prototypes definitions for electrcic monitoring code.
  *
  * Copyright (C) Sierra Wireless Inc.
  *
  *
  *
  */

#include "legato.h"
#include <stdio.h>

//--------------------------------------------------------------------------------------------------
/**
 * This function use to start data connection.
 *
 */
//--------------------------------------------------------------------------------------------------
void DataConnection_Init
(
    void
);

//--------------------------------------------------------------------------------------------------
/**
 * This function simply send system command on target.
 *
 */
//--------------------------------------------------------------------------------------------------
bool RunSystemCommand
(
    char *commandStringPtr
);
