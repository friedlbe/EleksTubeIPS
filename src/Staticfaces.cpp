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
    "5",
    "6",
    "7",
    "8",
    "9"
};

StaticFaces::StaticFaces() {
    oldIcons = getIconPack().value;
}

//const int tzOffset = -18000;

void StaticFaces::drawDisplay(int index, int display) {
    //char txt[10];

    // Load 'space' glyph if any
    //tfts->setShowDigits(1);
    //tfts->setImageJustification(TFTs::MIDDLE_CENTER);
    //tfts->setDigit(SECONDS_ONES, "space", TFTs::no);
    //TFT_eSprite &sprite = tfts->drawImage(SECONDS_ONES);
    //tfts->setShowDigits(1);

    //tfts->setImageJustification(TFTs::TOP_CENTER);
    //tfts->setBox(128, 128);

    //uint16_t rgb565 = hsv2rgb565(getWeatherHue(), getWeatherSaturation(), getWeatherValue());

    //uint16_t TEMP_COLOR = tfts->dimColor(rgb565);
    //uint16_t HILO_COLOR = TEMP_COLOR;
    //uint16_t DAY_FG_COLOR = tfts->dimColor(TFT_GOLD);
    //uint16_t DAY_BG_COLOR = tfts->dimColor(TFT_RED);
	//tfts->setMonochromeColor(rgb565);
  
    tfts->setDigit(indexToScreen[display], digitToName[index], TFTs::yes);
    tfts->drawImage(indexToScreen[display]);

    
}


void StaticFaces::checkIconPack() {
    if (getIconPack().value != oldIcons) {
        oldIcons = getIconPack().value;
        imageUnpacker->unpackImages("/ips/staticfaces/" + getIconPack().value, "/ips/staticfaces_cache");
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

    //if (getIconPack().value != oldIcons) {
    //    oldIcons = getIconPack().value;
    //    imageUnpacker->unpackImages("/ips/staticfaces/" + getIconPack().value, "/ips/staticfaces_cache");
    //    tfts->claim();
    //    tfts->invalidateAllDigits();
    //    tfts->release();
    //    _redraw = true;
    //}
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

