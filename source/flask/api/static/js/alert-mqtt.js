var mqtt;
var reconnectTimeout = 2000;
var Mhost = "143.198.199.16";
var port = 8888;

var room_id = "f3f6a64bec6e4715925ab25c41fdbf02"

function onConnect() {
  mqtt.subscribe("/GMT/DEV/ROOM/"+room_id+"/ALERT");
  // console.log("subscribed to /GMT/DEV/ROOM/"+room_id+"/ALERT" );
}

async function onMessageArrived(message) {
  // console.log("onMessageArrived: " + message.payloadString, message.destinationName.split('/'), message);

  let Topic = message.destinationName; 
  if (Topic == "/GMT/DEV/ROOM/"+room_id+"/ALERT"){
	  // console.log("New alert received");
    getAlerts()
  }
  
}

function MQTTconnect() {
  let userData = RequestData()
  mqtt = new Paho.MQTT.Client(Mhost, port, userData.ID);
  mqtt.onMessageArrived = onMessageArrived;
  var options = {
    timeout: 3,
    onSuccess: onConnect,
    onFailure: doFail,
    userName: userData.Username,
    password: "c764eb2b5fa2d259dc667e2b9e195218",
    // useSSL: true
  };
  mqtt.connect(options);
}

function doFail(e) {
  console.log(e);
}

MQTTconnect();