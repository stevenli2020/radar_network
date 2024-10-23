const chartTime = document.getElementById("chartTime");
// const lineChart = document.getElementById('lineChart')
var mqtt;
var reconnectTimeout = 2000;
var Mhost = "143.198.199.16";
var port = 8888;
var prevLe = 0;
var msgInterval = 0;

function addLineChart(heartR, heartW, breathR, breathW){
  return new Promise(function(resolve){
    setTimeout(function () {
      data2.shift();
      data2.push(heartW);
      categories.shift();
      categories.push(getCutTimeWithMilli());
      data3.shift();
      data3.push(breathW);
      lineChart.setOption({
        title: [
          {
            text: `Heart rate: ${heartR}`,
          },
          {
            text: `Breath rate: ${breathR}`,
          },
        ],
        xAxis: [
          {
            data: categories,
          },
          {
            data: categories,
            gridIndex: 1,
          },
        ],
        series: [
          {
            data: data2,
          },
          {
            data: data3,
            xAxisIndex: 1,
            yAxisIndex: 1,
          },
        ],
      });
      resolve()
    }, 200)
  })
}

async function timeOutMultiLoop(data){
  for(let i=0; i<data.length; i++){
    if('heartRate' in data[i]){
      if(data[i].heartWaveform.length > 0){
        for(let j=0; j<15; j++){
          await addLineChart(data[i].heartRate, data[i].heartWaveform[j], data[i].breathRate, data[i].breathWaveform[j])
        }
      }
    }
    
  }
}

function onConnect() {
  // console.log('Connected')
  // message = new Paho.MQTT.Message('Hello World');
  // message.destinationName = 'sensor1';
  // mqtt.send(message);
  mqtt.subscribe("/GMT/DEV/+/DATA/JSON");
}

async function onMessageArrived(message) {
  // console.log("onMessageArrived: " + message.payloadString, message.destinationName.split('/'), message);

  // console.log(message)
  let mac = message.destinationName.split("/");
  let data;
  if ("DATA" in JSON.parse(message.payloadString)) {
    data = JSON.parse(message.payloadString).DATA;
  } else {
    data = JSON.parse(message.payloadString);
  }

  
  let ts = [];
  var index = 0;
  //  document.querySelector("#home-time-select").value == "REAL TIME"
  if (
    data.length > 0 &&
    homeMacVal == mac[3]    
  ) {
    // console.log(homeMacVal, mac[3], mac, data.length > 0 && homeMacVal == mac[3])
    // console.log(message.payloadString);

    timer = 500;
    timer = parseInt(5000 / data.length);
    // timer = parseInt(1000 / data.length);
    // console.log(data, data.length, timer);
    timeOutMultiLoop(data)
    var interval = setInterval(function () {
      if ("trackData" in data[index]) {
        if (data[index].timestamp.includes(":")) ts.push(data[index].timestamp);
        if (data[index].timestamp.includes("."))
          ts.push(new Date(parseFloat(data[index].timestamp) * 1000));
        if (data[index]["numDetectedTracks"]) {
          scatter3D = [
            ["x", "y", "z"],
            [radarX, radarY, radarZ],
          ];
          legendD = ["Radar"];
          for (i = 1; i <= data[index].trackData.length; i++) {
            legendD.push("Person " + i);
          }
          seriesD = [
            {
              name: "Radar",
              type: "scatter",
              data: [[radarX, radarY]],
            },
          ];
          for (i = 0; i < data[index].trackData.length; i++) {
            // scatter3D.push([
            //   data[index].trackData[i][1].toFixed(2),
            //   data[index].trackData[i][2].toFixed(2),
            //   data[index].trackData[i][3].toFixed(2),
            // ]);
            // console.log((radarX - data[index].trackData[i][1]).toFixed(2),(radarY - data[index].trackData[i][2]).toFixed(2))
            // console.log(`absX: ${Math.abs((radarX - data[index].trackData[i][1])).toFixed(2)}, absY: ${Math.abs((radarY - data[index].trackData[i][2])).toFixed(2)}, radarX: ${radarX}, radarY: ${radarY}, X: ${data[index].trackData[i][1]}, Y: ${data[index].trackData[i][2]}`)
            seriesD.push({
              tooltip: {
                // trigger: 'axis',
                showDelay: 0,
                formatter: function (params) {
                  if (params.value.length > 1) {
                    return (
                      params.seriesName +
                      " :<br/>" +
                      params.value[0] +
                      "m " +
                      params.value[1] +
                      "m "
                    );
                  } else {
                    return (
                      params.seriesName +
                      " :<br/>" +
                      params.name +
                      " : " +
                      params.value +
                      "m "
                    );
                  }
                },
                axisPointer: {
                  show: true,
                  type: "cross",
                  lineStyle: {
                    type: "dashed",
                    width: 1,
                  },
                },
              },
              name: "Person " + (i + 1),
              type: "scatter",
              data: [
                [
                  // (radarX - Math.abs(data[index].trackData[i][1])).toFixed(2),
                  // (radarY - Math.abs(data[index].trackData[i][2])).toFixed(2),
                  Math.abs((radarX - data[index].trackData[i][1]).toFixed(2)),
                  Math.abs((radarY - data[index].trackData[i][2]).toFixed(2)),
                ],
              ],
              markArea: {
                silent: true,
                itemStyle: {
                  color: "transparent",
                  borderWidth: 1,
                  borderType: "dashed",
                },
                data: [
                  [
                    {
                      name: "Person " + (i + 1),
                      xAxis: "min",
                      yAxis: "min",
                    },
                    {
                      xAxis: "max",
                      yAxis: "max",
                    },
                  ],
                ],
              },
              markPoint: {
                data: [
                  { type: "max", name: "Max" },
                  { type: "min", name: "Min" },
                ],
              },
            });
          }
          if (prevLe > legendD.length) {
            for (i = 0; i < prevLe - legendD.length; i++) {
              seriesD.push({
                name: "",
                type: "",
                data: [],
                markArea: { data: [] },
                markPoint: { data: [] },
              });
            }
            // console.log(seriesD, prevLe, legendD.length);
          }
          // console.log("scatter: ", scatter3D);
          // setData(scatter3D);
          prevLe = legendD.length;

          chartTime.innerHTML = "Time: " + data[index].timestamp;
          scatterWeight.setOption({
            legend: {
              data: legendD,
            },
            xAxis: [
              {
                axisLabel: {
                  formatter: "{value} m",
                },
                // min: -6,
                // max: 6,
                min: 0,
                max: roomX
              },
            ],
            yAxis: [
              {
                axisLabel: {
                  formatter: "{value} m",
                },
                // min: 0,
                // max: 6,
                min: 0,
                max: roomY
              },
            ],
            series: seriesD,
          });
        }
      }
      index++;
      if (index == data.length) {
        clearInterval(interval);
      }
    }, timer);
  } 
}

function MQTTconnect() {
  // console.log("connecting to "+host+" "+port);
  // mqtt = new Paho.MQTT.Client(host, port, "steven-fssn1234");
  mqtt = new Paho.MQTT.Client(Mhost, port, "1234");
  // client.onConnectionLost = onConnectionLost;
  mqtt.onMessageArrived = onMessageArrived;
  var options = {
    timeout: 3,
    onSuccess: onConnect,
    onFailure: doFail,
    userName: "js-client",
    password: "c764eb2b5fa2d259dc667e2b9e195218",
    // useSSL: true
  };
  mqtt.connect(options);
}

function doFail(e) {
  console.log(e);
}

MQTTconnect();
