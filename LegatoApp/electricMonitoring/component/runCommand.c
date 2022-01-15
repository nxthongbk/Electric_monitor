#include "legato.h"
#include <stdio.h>
#include <math.h>
#include <inttypes.h>
#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

//--------------------------------------------------------------------------------------------------
/**
 * This function simply send system command on target.
 *
 */
//--------------------------------------------------------------------------------------------------
bool RunSystemCommand
(
    char *commandStringPtr
)
{
    int systemResult;

    if (NULL == commandStringPtr)
    {
        LE_ERROR("ERROR Parameter is NULL.");
        return false;
    }
    if ('\0' == *commandStringPtr)
    {
        LE_INFO("INFO Nothing to execute.");
        return false;
    }

    systemResult = system(commandStringPtr);
    // Return value of -1 means that the fork() has failed (see man system).
    if (0 == WEXITSTATUS(systemResult))
    {
        LE_INFO("Success: %s", commandStringPtr);
    }
    else
    {
        LE_ERROR("Error %s Failed: (%d)", commandStringPtr, systemResult);
        return false;
    }
    return true;
}