import mqtt from 'mqtt';

const MQTT_BROKER_URL = 'your_mqtt_broker_url';

let client;

const mqttConnect = (host, mqttOption) => {
  setConnectStatus('Connecting');
  client = mqtt.connect(host, mqttOption)
};

const mqttSub = (subscription) => {
  if (client) {
    const { topic, qos } = subscription;
    client.subscribe(topic, { qos }, (error) => {
      if (error) {
        console.log('Subscribe to topics error', error)
        return
      }
      setIsSub(true)
    });
  }
};

const mqttUnSub = (subscription) => {
  if (client) {
    const { topic } = subscription;
    client.unsubscribe(topic, error => {
      if (error) {
        console.log('Unsubscribe error', error)
        return
      }
      setIsSub(false);
    });
  }
};

const mqttPublish = (context) => {
  if (client) {
    const { topic, qos, payload } = context;
    client.publish(topic, payload, { qos }, error => {
      if (error) {
        console.log('Publish error: ', error);
      }
    });
  }
}

const mqttDisconnect = () => {
  if (client) {
    client.end(() => {
      setConnectStatus('Connect');
    });
  }
}

export { mqttConnect, mqttSub, mqttUnSub, mqttPublish, mqttDisconnect };