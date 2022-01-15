 /**
  * Data connection control
  *
  *
  */
#include "legato.h"
#include "interfaces.h"
#include <le_mdc_interface.h>
#include <stdio.h>
#include <math.h>
#include <inttypes.h>
#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include "inc/lib.h"

//static char ipWanAddr[20] = {0};

void DataConnection_Init
(
    void
)
{
    le_mdc_ProfileRef_t profileRef = NULL;
    le_mdc_ConState_t state = LE_MDC_DISCONNECTED;
    le_result_t res;

    profileRef = le_mdc_GetProfile(LE_MDC_DEFAULT_PROFILE);
    //le_mdc_AddSessionStateHandler(profileRef, SessionState, profileRef);
    //le_mdc_SetPDP(profileRef, LE_MDC_PDP_IPV4);
    res = le_mdc_GetSessionState(profileRef, &state);
    if (res != LE_OK){
        LE_ERROR("\nFailed to get state of data session\n");
    }
    else{
        while(state != LE_MDC_CONNECTED)
        {
            RunSystemCommand("#/bin/bash \n");
            RunSystemCommand("/mnt/legato/system/bin/cm data connect");
            res = le_mdc_GetSessionState(profileRef, &state);
            if (res != LE_OK){
                LE_ERROR("\nFailed to get state of data session\n");
            }
        }
    }
}
