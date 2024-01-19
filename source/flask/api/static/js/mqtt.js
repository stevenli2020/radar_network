// const chartTime = document.getElementById("chartTime");
// const lineChart = document.getElementById('lineChart')
var mqtt;
var reconnectTimeout = 2000;
var Mhost = "143.198.199.16";
var port = 8888;
var prevLe = 0;
var msgInterval = 0;
var vitalLenCounter = 0;

function addLineChart(heartR, breathR){
  heartRateData.innerText = Math.round(heartR, 1)
  breathRateData.innerText = Math.round(breathR, 1)
  vitalData.shift();
  if(vitalLenCounter <= 100){
    vitalLenCounter++;
  }
  const averageHeartRate = Math.round(vitalData.reduce((total, next) => total + next.value, 0) / vitalLenCounter, 2);
  const averageBreathRate = Math.round(vitalData2.reduce((total, next) => total + next.value, 0) / vitalLenCounter, 2);
  avgHeartRateData.innerHTML = `Average: ${averageHeartRate} BPM`
  avgBreathRateData.innerHTML = `Average: ${averageBreathRate} BPM`
  // console.log(averageBreathRate, averageBreathRate)
  // if(Math.round(heartR, 1)<101 && Math.round(heartR, 1)>59){
  if(Math.round(heartR, 1)<(averageHeartRate+(averageHeartRate*0.2)) && Math.round(heartR, 1)>(averageHeartRate-(averageHeartRate*0.2))){
    vitalData.push({value: Math.round(heartR, 1), itemStyle: { color: brightGreen}});
  } else {
    // vitalData.push({value: Math.round(heartR, 1), itemStyle: { color: brightOrange}});
	vitalData.push({value: Math.round(heartR, 1), itemStyle: { color: brightGreen}});
  }
  // vitalData.push(Math.round(heartR, 1));
  
  categories.shift();
  categories.push(getCutTimeWithMilli("Minute"));
  vitalData2.shift();
  // if(Math.round(breathR, 1)<20 && Math.round(breathR, 1)>12){
  if(Math.round(breathR, 1)<(averageBreathRate+(averageBreathRate*0.2)) && Math.round(breathR, 1)>(averageBreathRate-(averageBreathRate*0.2))){
    // vitalData2.shift();
    vitalData2.push({value: Math.round(breathR, 1), itemStyle: { color: brightGreen}});
  } else {
    vitalData2.push({value: Math.round(breathR, 1), itemStyle: { color: brightOrange}});
  }
  // vitalData2.push(Math.round(breathR, 1));
  
  vitalChart.setOption({
    xAxis: [
      {
        show: true,
        data: categories,
      },
      {
        show: true,
        data: categories,
        gridIndex: 1,
      },
    ],
    series: [
      {
        data: vitalData,
      },
      {
        data: vitalData2,
        xAxisIndex: 1,
        yAxisIndex: 1,
      },
    ],
  });
  
  // return new Promise(function(resolve){
  //   setTimeout(function () {
  //     data.shift();
  //     data.push(heartR);
  //     categories.shift();
  //     categories.push(getCutTimeWithMilli("Minute"));
  //     data2.shift();
  //     data2.push(breathR);
  //     lineChart.setOption({
  //       xAxis: [
  //         {
  //           data: categories,
  //         },
  //         {
  //           data: categories,
  //           gridIndex: 1,
  //         },
  //       ],
  //       series: [
  //         {
  //           data: data2,
  //         },
  //         {
  //           data: data3,
  //           xAxisIndex: 1,
  //           yAxisIndex: 1,
  //         },
  //       ],
  //     });
  //     resolve()
  //   }, 200)
  // })
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
  mqtt.subscribe("/GMT/DEV/+/DATA/+/JSON");
  mqtt.subscribe("/GMT/USVC/DECODE_PUBLISH/C/UPDATE_DEV_CONF");
  console.log("subscribed to /GMT/USVC/DECODE_PUBLISH/C/UPDATE_DEV_CONF" );
  // mqtt.subscribe("/GMT/DEV/#");
}

async function onMessageArrived(message) {
  // console.log("onMessageArrived: " + message.payloadString, message.destinationName.split('/'), message);

  // console.log(message.destinationName)
  let Topic = message.destinationName; 
  if (Topic == "/GMT/USVC/DECODE_PUBLISH/C/UPDATE_DEV_CONF"){
	  console.log("Update request received");
	  location.reload();
	  return;
  }
  let mac = message.destinationName.split("/");
  let data;
  if ("DATA" in JSON.parse(message.payloadString)) {
    data = JSON.parse(message.payloadString).DATA;
  } else {
    data = JSON.parse(message.payloadString);
  }

  
  let ts = [];
  var num = 0;
  //  document.querySelector("#home-time-select").value == "REAL TIME"
  // console.log(macPos, macVital)
  if (
    data.length > 0 &&
    (macPos == mac[3] || macVital == mac[3])    
  ) {
    // console.log(homeMacVal, mac[3], mac, data.length > 0 && homeMacVal == mac[3])
    // console.log(message.payloadString);
    // console.log(data)
    
    timer = 1000;
    timer = parseInt(3000 / data.length);
    // timer = parseInt(1000 / data.length);
    // console.log(data, data.length, timer);
    // timeOutMultiLoop(data)
    
    if(realtimeHistVital.classList.contains("active")){
      if("heartRate" in data[num]){      
        // console.log(data)
        data.forEach(d => {
          // console.log(d)
          if("heartRate" in d)
            if(d.heartRate != "-" && d.heartRate != null){
              addLineChart(d.heartRate, d.breathRate)
              checkVitalDataEmpty = new Date()   
              checkRoomEmpty = new Date() 
              document.querySelector('#empty-lable').style.display = 'none'        
            }
              
        })
      }
    }
    
    if("numSubjects" in data[num]){
      var index = 0;
      var interval = setInterval(function () {        
        // if ("DATA" in JSON.parse(message.payloadString)) {
          // console.log(message.payloadString)
          // console.log(data, data[index], index)
          // if (data[index].timeStamp.toString().includes(":")) ts.push(data[index].timeStamp);
          // if (data[index].timeStamp.toString().includes("."))
          //   ts.push(new Date(parseFloat(data[index].timeStamp) * 1000));
          // if(data[index].hasOwnProperty("numSubjects")){
          if(parseInt(data[index]["numSubjects"]) > 0){
            document.querySelector('#empty-lable').style.display = 'none'
            document.querySelector('#status-label').style.display = 'block'
            checkRoomEmpty = new Date()
          }
          if (parseInt(data[index]["numSubjects"]) > 0) { 
            let series = [...radars]
            // [
            //   {
            //     name: "Radar",
            //     type: "scatter",
            //     data: [[radarX, radarY]],
            //   },
            // ];
            // if((radarX_1>0 || radarY_1>0)&&(radarX_2>0 || radarY_2>0)){
            // if(radars.length > 0){
            //   let radarNames = []
              
            //   radarX = radarX_1
            //   radarY = radarY_1
            //   legendD = ["Radar 1", "Radar 2"]
            //   seriesD = [
            //     {
            //       name: "Radar 1",
            //       type: "scatter",
            //       data: [[radarX_1, radarY_1]]
            //     },
            //     {
            //       name: "Radar 2",
            //       type: "scatter",
            //       emphasis: {
            //         focus: "series",
            //       },
            //       data: [[radarX_2, radarY_2]],
            //       symbol: "diamond",
            //       symbolSize: 30,
            //     }
            //   ]
            // } 
            // else if(radarX_1>0 || radarY_1>0){
            //   radarX = radarX_1
            //   radarY = radarY_1
            //   legendD = ["Radar"]
            //   seriesD = [
            //     {
            //       name: "Radar",
            //       type: "scatter",
            //       data: [[radarX_1, radarY_1]]
            //     }
            //   ]
            // } else if(radarX_2>0 || radarY_2>0){
            //   radarX = radarX_2
            //   radarY = radarY_2
            //   legendD = ["Radar"]
            //   seriesD = [
            //     {
            //       name: "Radar",
            //       type: "scatter",
            //       data: [[radarX_2, radarY_2]]
            //     }
            //   ]
            // }
            
            var object_list = []

            for (let i = 0 ; i < data.length ; i++){
              if (object_list.includes(data[i].trackIndex)){
                continue
              }

              object_list.push(data[i].trackIndex)

              if(data[i].velX == 0 && data[i].velY == 0)
                defaultSymbol = dashCircleFill
              else if(data[i].velX == 0 && data[i].velY > 0)
                defaultSymbol = arrowUpCircleFill
              else if(data[i].velX == 0 && data[i].velY < 0)
                defaultSymbol = arrowDownCircleFill
              else if(data[i].velX > 0 && data[i].velY == 0)
                defaultSymbol = arrowRightCircleFill
              else if(data[i].velX > 0 && data[i].velY > 0)
                defaultSymbol = arrowUpRightCircleFill
              else if(data[i].velX > 0 && data[i].velY < 0)
                defaultSymbol = arrowDownRightCircleFill
              else if(data[i].velX < 0 && data[i].velY == 0)
                defaultSymbol = arrowLeftCircleFill
              else if(data[i].velX < 0 && data[i].velY > 0)
                defaultSymbol = arrowUpLeftCircleFill
              else if(data[i].velX < 0 && data[i].velY < 0)
                defaultSymbol = arrowDownLeftCircleFill

              
              series.push({
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
                name: "Person ID:" + String(data[i].trackIndex),
                type: "scatter",
                symbol: defaultSymbol,
                symbolSize: 30,
                data: [
                  [
                    Math.abs((data[i].posX??0).toFixed(2)),
                    Math.abs((data[i].posY??0).toFixed(2)),
                  ],
                ],
                itemStyle: {
                  color: function () {
                    if (!("state" in data[i]) || data[i].state == null || data[i].state == "None") {
                      return '#080808';
                    } else if (data[i].state == "Moving") {
                      return '#f8fc03'; 
                    } else if (data[i].state == "Upright") {
                      return '#0918e3'; 
                    } else if (data[i].state == "Laying") {
                      return '#8d61be'; 
                    } else if (data[i].state == "Fall") {
                      return '#fc0303'; 
                    } else if (data[i].state == "Social") {
                      return '#20fc03'; 
                    } 
                  },
                },        
              });
            }
            const updatedOptions = {
              xAxis: [
                {
                  axisLabel: {
                    formatter: "{value} m",
                  },
                  min: 0,
                  max: roomX,
                },
              ],
              yAxis: [
                {
                  axisLabel: {
                    formatter: "{value} m",
                  },
                  min: 0,
                  max: roomY,
                },
              ],
              series: series, // Replace 'updatedSeries' with your new series data
            };
            
            // Update the chart with the new options
            scatterWeight.setOption(updatedOptions);
            
            // Resize the chart to fit the container (assuming 'scatterWeight' is your chart instance)
            scatterWeight.resize();
          }
          // }        
        // }
        index++;
        // console.log(index == data.length, index, data.length, timer)
        if (index == data.length) {
          clearInterval(interval);
        }
      }, timer);
    }
    
  } 
}

function MQTTconnect() {
  // console.log("connecting to "+host+" "+port);
  // mqtt = new Paho.MQTT.Client(host, port, "steven-fssn1234");
  let userData = RequestData()
  mqtt = new Paho.MQTT.Client(Mhost, port, userData.ID);
  // client.onConnectionLost = onConnectionLost;
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
