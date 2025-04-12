#include <WSMenuHandler.h>

String WSMenuHandler::clockMenu = "{\"1\": { \"url\" : \"clock.html\", \"title\" : \"Clock\" }}";
String WSMenuHandler::ledsMenu = "{\"2\": { \"url\" : \"leds.html\", \"title\" : \"LEDs\" }}";
String WSMenuHandler::facesMenu = "{\"3\": { \"url\" : \"faces.html\", \"title\" : \"Files\" }}";
String WSMenuHandler::mqttMenu = "{\"4\": { \"url\" : \"mqtt.html\", \"title\" : \"MQTT\" }}";
String WSMenuHandler::infoMenu = "{\"5\": { \"url\" : \"info.html\", \"title\" : \"Info\" }}";
String WSMenuHandler::networkMenu = "{\"6\": { \"url\" : \"network.html\", \"title\" : \"Network\" }}";
String WSMenuHandler::weatherMenu = "{\"7\": { \"url\" : \"weather.html\", \"title\" : \"Weather\" }}";
String WSMenuHandler::matrixMenu = "{\"8\": { \"url\" : \"matrix.html\", \"title\" : \"Screen Saver\" }}";

void WSMenuHandler::handle(AsyncWebSocketClient *client, char *data) {
	String json("{\"type\":\"sv.init.menu\", \"value\":[");
	char *sep = "";
	for (int i=0; items[i] != 0; i++) {
		json.concat(sep);json.concat(*items[i]);sep=",";
	}
	json.concat("]}");
	client->text(json);
}

void WSMenuHandler::setItems(String **items) {
	this->items = items;
}

