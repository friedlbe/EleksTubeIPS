#include <ArduinoJson.h>

#include "TFTs.h"
#include "staticfaces.h"
#include "ColorConversion.h"
#include "IPSClock.h"

#include <math.h>


char* StaticFaces::digitToName[] = {
    "0",
    "1",
    "2",
    "3",
    "4",
    "5"
};

StaticFaces::StaticFaces() {
    oldIcons = getStaticFacePack().value;
    displayTimer.init(millis(), 0);
}

void StaticFaces::drawDisplay(int index, int display) {
  
    tfts->setDigit(indexToScreen[display], digitToName[index], TFTs::yes);
    tfts->drawImage(indexToScreen[display]);    
}

void StaticFaces::checkIconPack() {
    if (getStaticFacePack().value != oldIcons) {
        oldIcons = getStaticFacePack().value;
        imageUnpacker->unpackImages("/ips/sfaces/" + getStaticFacePack().value, "/ips/sf_cache");
        tfts->claim();
        tfts->invalidateAllDigits();
        tfts->release();
        _redraw = true;
    }
}

bool StaticFaces::preDraw(uint8_t dimming) {
    unsigned long nowMs = millis();

    if (_redraw || displayTimer.expired(nowMs)) {
        _redraw = false;

        tfts->claim();
    	tfts->setShowDigits(2);
        // tfts->invalidateAllDigits();
        tfts->setDimming(dimming);

        displayTimer.init(nowMs, 10000);

        return true;
    }

    return false;
}

void StaticFaces::postDraw() {
    tfts->release();
}

void StaticFaces::loop(uint8_t dimming) {

    checkIconPack();
    
    tfts->setImageJustification(TFTs::MIDDLE_CENTER);
    tfts->setBox(tfts->width(), tfts->height());

    if (preDraw(dimming)) {
        tfts->checkStatus();
        tfts->enableAllDisplays();

        for (int i=0; i<6; i++) 
        {
            drawDisplay(6-i, i);
        }

        postDraw();
   }
}

