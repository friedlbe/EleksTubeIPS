#ifndef _IPSCLOCK_STATICFACES_H
#define _IPSCLOCK_STATICFACES_H

#include <GLOBAL_DEFINES.h>

#if defined(USE_SYNC_CLIENT) || defined(USE_HTTPCLIENT)
#include <WiFiClientSecure.h>
#ifdef USE_HTTPCLIENT
#include <HTTPClient.h>
#endif
#else
#include <ESPAsyncHTTPClient.h>
#endif
#include <ConfigItem.h>
//#include <TimeSync.h>

#include "ClockTimer.h"

#include "ImageUnpacker.h"

class StaticFaces {
public:
    StaticFaces();

    static StringConfigItem& getStaticFacePack() { static StringConfigItem staticfaces_icons("staticfaces_icons", 25, "dom2"); return staticfaces_icons; }	// <staticfaces_icons>.tar.gz, max length is 31

    void setImageUnpacker(ImageUnpacker *imageUnpacker) { this->imageUnpacker = imageUnpacker; }

    void loop(uint8_t dimming);
    void redraw() { _redraw = true; }
private:
    const int indexToScreen[NUM_DIGITS] = {
        SECONDS_ONES,
        SECONDS_TENS,
        MINUTES_ONES,
        MINUTES_TENS,
        HOURS_ONES,
        HOURS_TENS
    };
    
    void drawDisplay(int index, int display);
    bool preDraw(uint8_t dimming);
    void postDraw();
    void checkIconPack();

    static char* digitToName[10];

    ClockTimer::Timer displayTimer;
    String oldIcons;
    ImageUnpacker *imageUnpacker;
    bool _redraw = false;
};
#endif