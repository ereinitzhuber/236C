#include <MD_Parola.h>
#include <MD_MAX72xx.h>
#include <SPI.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <Wire.h>



//YOUR  PORT  HERE
int port = 5005;

const char* ssid = ""; //YOUR WIFI SSID
const char* passwd = ""; //YOUR WIFI PASSWORD

WiFiUDP UDP;
char pktBuf[255];

// Define the number of devices we have in the chain and the hardware interface
// NOTE: These pin numbers will probably not work with your hardware and may
// need to be adapted
#define HARDWARE_TYPE MD_MAX72XX::FC16_HW //CHANGE TO YOUR DEVICE TYPE
#define MAX_DEVICES 4

#define CLK_PIN   25  //YOUR CLK PIN
#define DATA_PIN  27 //YOUR DATA PIN
#define CS_PIN    26 //YOUR CS PIN

// HARDWARE SPI
//MD_Parola P = MD_Parola(HARDWARE_TYPE, CS_PIN, MAX_DEVICES);
// SOFTWARE SPI
MD_Parola P = MD_Parola(HARDWARE_TYPE, DATA_PIN, CLK_PIN, CS_PIN, MAX_DEVICES);


// Global message buffers shared by Serial and Scrolling functions
#define  BUF_SIZE 255
char newMessage[BUF_SIZE];
bool newMessageAvailable = false;

void getCommand(void)
{
    if (UDP.parsePacket()) {
        UDP.read(pktBuf, 255);
        //Serial.println(pktBuf);
        strcpy(newMessage, pktBuf);
        newMessageAvailable = true;
    }
}

void setup()
{
    Serial.begin(57600);
    //WIFI SETUP
    WiFi.begin(ssid, passwd);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting...");
    }
    Serial.println("Connected!");
    Serial.println(WiFi.localIP());
    Serial.println(port);
    UDP.begin(port);

    //Set brightness of LED matrix 1-15
    P.setIntensity(6);
    P.begin();
    P.print("Hello!");
}

void loop()
{
    if (newMessageAvailable)
    {
        newMessageAvailable = false;
        P.displayClear();
        P.print(newMessage);
    }
    getCommand();
}
