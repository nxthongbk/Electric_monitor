//--------------------------------------------------------------------------------------------------
/**
 * @file electricMonitoring.c
 *
 * monitoring the electric
 *
 * Copyright (C) Sierra Wireless Inc.
 */
//--------------------------------------------------------------------------------------------------

#include "legato.h"
#include "interfaces.h"
#include <sys/socket.h> 
#include <netinet/in.h> 
#include <stdio.h> 
#include <stdlib.h> 
#include <errno.h> 
#include <string.h> 
#include <netdb.h> 
#include <sys/types.h> 
#include <unistd.h>
#include <arpa/inet.h>
#include <stdint.h>
#include "inc/lib.h"

//--------------------------------------------------------------------------------------------------
/**
 * Server TCP port.
 *
 * @note this is an arbitrary value and can be changed as required
 */
//--------------------------------------------------------------------------------------------------
#define TCP_SERVER_PORT 5002
#define TCP_SERVER_ADDRESS "192.168.13.32"
#define PERIOD 30
static int sockFd;
struct sockaddr_in server_addr; //connector's address information

// modbus TCP message
// static char modbusMsg[20] = {0x00, 0x01, 0x00, 0x00, 0x00, 0x06, 0x01, 0x04, 0x00, 0x14, 0x00, 0x04}; // voltage and current
// static char modbusMsgP[20] = {0x00, 0x01, 0x00, 0x00, 0x00, 0x06, 0x01, 0x04, 0x00, 0x00, 0x00, 0x02}; // total power
static char modbusMsg[20] = {0x00, 0x01, 0x00, 0x00, 0x00, 0x06, 0x01, 0x04, 0x00, 0x00, 0x00, 0x18};

//reference to request data timer
le_timer_Ref_t dataRequestTimerRef = NULL;

//--------------------------------------------------------------------------------------------------
/**
 * Device IMEI, used as a unique device identifier
 */
//--------------------------------------------------------------------------------------------------
char DeviceIMEI[LE_INFO_IMEI_MAX_BYTES];

//--------------------------------------------------------------------------------------------------
/**
 * Thingsboard information
 */
//--------------------------------------------------------------------------------------------------
//const char mqttBrokerURI[] = "tcp://104.196.24.70:1883";  // demo.thingsboard.io
const char mqttBrokerURI[] = "tcp://iot.innovation.com.vn:3009";
const uint8_t mqttPassword[] = {'S', 'W', 'I'};
const char topicSubServerRPC[] = "v1/devices/me/rpc/request/+";
char topicTelemetry[] = "v1/devices/me/telemetry";

// MQTT session reference
mqtt_SessionRef_t MQTTSession;

//-------------------------------------------------------------------------------------------------
/**
 *
 * This function to calculate CRC-16 (Modbus) for Modbus RTU
 */
//-------------------------------------------------------------------------------------------------
/*
unsigned int CRC16(unsigned char *buf, int len)
{  
   unsigned int crc = 0xFFFF;
   unsigned int bHi,bLo;

   for (int pos = 0; pos < len; pos++)
   {
      crc ^= (unsigned int)buf[pos];    // XOR byte into least sig. byte of crc

      for (int i = 8; i != 0; i--) {    // Loop over each bit
         if ((crc & 0x0001) != 0) {      // If the LSB is set
            crc >>= 1;                    // Shift right and XOR 0xA001
            crc ^= 0xA001;
         }
         else                            // Else LSB is not set
            crc >>= 1;                    // Just shift right
         }
   }
   
   bHi =  (crc & 0x00FF) << 8;
   bLo =  (crc & 0xFF00) >> 8;
   crc = bHi | bLo;
   return crc;
}
*/

//--------------------------------------------------------------------------------------------------
/**
 * Call-back function called on lost connection
 */
//--------------------------------------------------------------------------------------------------
void OnConnectionLost
(
    void* context
)
{
    LE_ERROR("Connection lost!");
}

//--------------------------------------------------------------------------------------------------
/**
 * Publisher
 */
//--------------------------------------------------------------------------------------------------
void Publish
(
    char *data
)
{
    uint8_t payload[1024];
    snprintf((char*)payload, sizeof(payload), "%s", data);
    size_t payloadLen = strlen((char*)payload);
    const bool retain = false;

    const le_result_t publishResult = mqtt_Publish(
        MQTTSession,
        topicTelemetry,
        payload,
        payloadLen,
        MQTT_QOS0_TRANSMIT_ONCE,
        retain);
    LE_INFO("Published Topic %s data %s result %s", topicTelemetry, payload,
            LE_RESULT_TXT(publishResult));
}

//--------------------------------------------------------------------------------------------------
/**
 * Call-back function called on arrived message
 */
//--------------------------------------------------------------------------------------------------
void OnMessageArrived
(
    const char* topic,
    const uint8_t* payload,
    size_t payloadLen,
    void* context
)
{
    LE_INFO("arrived message");
    //TODO
}

//-------------------------------------------------------------------------------------------------
/**
 * This function convert raw string hex to float
 */
//-------------------------------------------------------------------------------------------------
float HexToFloat(char *dataString)
{
    float f;
    uint32_t data;
    sscanf(dataString, "%x", &data);
    f = *((float*)&data);
    LE_INFO("Raw data: 0x%08X. Readable data: %.3f", data, f);

    return f;
}

//-------------------------------------------------------------------------------------------------
/**
 * Callback handler
 * This function is called every 10 seconds to get data from electric device
 */
//-------------------------------------------------------------------------------------------------
void GetData(le_timer_Ref_t  timerRef)
{
    int numbytes;
    unsigned char buf[60];
    
    LE_INFO("Getting data");
    
    int error = 0;
    socklen_t len = sizeof (error);
    int retval = getsockopt (sockFd, SOL_SOCKET, SO_ERROR, &error, &len);
    if (retval != 0) 
    {
        LE_ERROR("Socket error.");
        while(1){
            sleep(10);
            LE_INFO("Reconnecting");
            if (connect(sockFd, (struct sockaddr *)&server_addr, sizeof(struct sockaddr)) == -1) {
                LE_ERROR("Connection with the device failed...\n");
                close(sockFd);
            }
            else{
                LE_INFO("Re-connected to electric device..\n");
            }
        }
        
    }
    
    // get voltage and current
    if (send(sockFd, modbusMsg, sizeof(modbusMsg), 0) == -1){
        LE_ERROR("Unable to send data request");
    }

    if ((numbytes=recv(sockFd, buf, sizeof(buf), 0)) == -1){
        LE_ERROR("Failed to recieve data");
    }
    
    for(int i=0; i < sizeof(buf)/sizeof(buf[0]); i++){
        LE_INFO("%02X", buf[i]);
    }
 
    // convert raw hex data to float
    // voltage
    char voltage[10];
    float volt;
    snprintf(voltage, sizeof(voltage), "%02X%02X%02X%02X", buf[51], buf[52], buf[49], buf[50]);
    volt = HexToFloat(voltage);
    
    // current
    char current[10];
    float curr;
    snprintf(current, sizeof(current), "%02X%02X%02X%02X", buf[55], buf[56], buf[53], buf[54]);;
    curr = HexToFloat(current);

    // total active energy
    char totalEnergy[10];
    float energy;
    snprintf(totalEnergy, sizeof(totalEnergy), "%02X%02X%02X%02X", buf[11], buf[12], buf[9], buf[10]);
    energy = HexToFloat(totalEnergy);
    
    char publishData[128];
    snprintf(publishData, sizeof(publishData), "{\"voltage\":\"%.3f\", \"current\":\"%.3f\", \"total energy\":\"%.3f\"}", volt, curr, energy);
    Publish(publishData);

}

//--------------------------------------------------------------------------------------------------
/**
 * Main function
 */
//--------------------------------------------------------------------------------------------------
COMPONENT_INIT
{
    LE_INFO("Dataconnection init");
    DataConnection_Init();

    LE_INFO("Thingsboard init");
    LE_ASSERT_OK(le_info_GetImei(DeviceIMEI, NUM_ARRAY_MEMBERS(DeviceIMEI)));
    char clientId[32];
    snprintf(clientId, sizeof(clientId), "%s", DeviceIMEI);
    LE_INFO("IMEI: %s",clientId);
    LE_ASSERT_OK(mqtt_CreateSession(mqttBrokerURI, clientId, &MQTTSession));

    const uint16_t keepAliveInSeconds = 60;
    const bool cleanSession = true;
    const char* username = DeviceIMEI;
    const uint16_t connectTimeout = 20;
    const uint16_t retryInterval = 10;
    mqtt_SetConnectOptions(
        MQTTSession,
        keepAliveInSeconds,
        cleanSession,
        username,
        mqttPassword,
        NUM_ARRAY_MEMBERS(mqttPassword),
        connectTimeout,
        retryInterval);

    mqtt_AddConnectionLostHandler(MQTTSession, &OnConnectionLost, NULL);
    mqtt_AddMessageArrivedHandler(MQTTSession, &OnMessageArrived, NULL);

    int connectResult;
    while (1){
        connectResult = mqtt_Connect(MQTTSession);
        if (connectResult != LE_OK)
        {
            LE_ERROR("Connection failed! error %d\n", connectResult);
            LE_INFO("Retry after 10 seconds\n");
            sleep(10);
        }
        else{
            LE_INFO("Connected to server '%s'\n", mqttBrokerURI);
            break;
        }
    }

    // mqtt Subcriber
    char subscribeTopic[64];
    snprintf(subscribeTopic, sizeof(subscribeTopic), "%s", topicSubServerRPC);
    LE_FATAL_IF(
        mqtt_Subscribe(MQTTSession, subscribeTopic, MQTT_QOS0_TRANSMIT_ONCE) != LE_OK,
        "failed to subscribe to %s",
        subscribeTopic);
    LE_INFO("Subscribed to topic (%s)", subscribeTopic);
    
    // socket
    struct timeval timeout;      
    timeout.tv_sec = 10;
    timeout.tv_usec = 0;

    LE_INFO("Start monitoring electric consumption");
    if ((sockFd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        LE_ERROR("creating socket failed\n");
        return;
    }
    bzero(&server_addr, sizeof(server_addr)); //zero the rest of the struct
    
    // assign IP, PORT
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr(TCP_SERVER_ADDRESS);
    server_addr.sin_port = htons(TCP_SERVER_PORT);
    
    // add send & receive timeout
    if (setsockopt (sockFd, SOL_SOCKET, SO_RCVTIMEO, &timeout,
                sizeof timeout) < 0)
    {
        LE_ERROR("Setsockopt failed");
    }

    if (setsockopt (sockFd, SOL_SOCKET, SO_SNDTIMEO, &timeout,
                sizeof timeout) < 0)
    {
        LE_ERROR("Setsockopt failed");
    }

    // connect the client socket to server socket
    if (connect(sockFd, (struct sockaddr *)&server_addr, sizeof(struct sockaddr)) == -1) {
        LE_ERROR("Connection with the device failed...\n");
        close(sockFd);
    }
    else
        LE_INFO("Connected to electric device..\n");
    
    // create timer
    dataRequestTimerRef = le_timer_Create("dataRequestTimer");
    le_clk_Time_t dataRequestInterval = { PERIOD, 0 };
    le_timer_SetInterval(dataRequestTimerRef, dataRequestInterval);
    le_timer_SetRepeat(dataRequestTimerRef, 0);                   //set repeat to always
    le_timer_SetHandler(dataRequestTimerRef, GetData);
    le_timer_Start(dataRequestTimerRef);

}
