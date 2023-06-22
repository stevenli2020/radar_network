const detailPageHeader = document.getElementById("detail-page-header");
const homeMacAddrSelect = document.getElementById("home-device-mac");
const homeTimeSelect = document.getElementById("home-time-select");
const homeDateTimeRow = document.getElementById("home-date-time-row");
// const homeTimeSelectSubmitRow = document.getElementById("home-time-select-submit-row");
const homeDateRangePicker = document.getElementById("date-range-picker");
const homeTimeSelectSubmitBtn = document.getElementById(
  "home-time-select-submit-btn"
);
const progress = document.querySelector(".progress");
const progressBar = document.querySelector(".progress-bar");
const heartIcon = document.getElementById("heartIcon");
const breathIcon = document.getElementById("breathIcon");
const trackChartRow = document.getElementById("track-chart-row");
// history of location
const hourHistLoc = document.getElementById("hour-loc-tab");
const dayHistLoc = document.getElementById("day-loc-tab");
const weekHistLoc = document.getElementById("week-loc-tab");
const monthHistLoc = document.getElementById("month-loc-tab");
// history of vital
const realtimeHistVital = document.getElementById("real-vital-tab");
const hourHistVital = document.getElementById("hour-vital-tab");
const dayHistVital = document.getElementById("day-vital-tab");
const weekHistVital = document.getElementById("week-vital-tab");
const monthHistVital = document.getElementById("month-vital-tab");
const heartRateData = document.getElementById('heart-rate-data')
const breathRateData = document.getElementById('breath-rate-data')
// history of posture
// const hourHistPosture = document.getElementById("hour-posture-tab");
// const dayHistPosture = document.getElementById("day-posture-tab");
// const weekHistPosture = document.getElementById("week-posture-tab");
// const monthHistPosture = document.getElementById("month-posture-tab");
const inRoomHour = document.getElementById("in-room-hour")
const inBedHour = document.getElementById("in-bed-hour")
const inRoomDay = document.getElementById("in-room-day")
const inBedDay = document.getElementById("in-bed-day")
const inRoomWeek = document.getElementById("in-room-week")
const inBedWeek = document.getElementById("in-bed-week")
const inRoomMonth = document.getElementById("in-room-month")
const inBedMonth = document.getElementById("in-bed-month")
var homeMacVal, homeTimeSelVal;
var macPos, macVital
var initLegendD = []
var intiSeriesD = []
let radarX_1 = 0
let radarY_1 = 0
let radarX_2 = 0
let radarY_2 = 0
var roomXD, roomYD
var heartReal = []
var breathReal = []
var xAxisReal = []
// check room empty
var checkRoomEmpty = new Date()
var checkVitalDataEmpty = new Date() 
var sampleLocData = []
var realTimeLocationRadarInRoom = 1
var realTimeLocationPerson = 1
setInterval(function(){
  // console.log(Math.round((new Date() - checkRoomEmpty)/1000))
  if(Math.round((new Date() - checkRoomEmpty)/1000)>180){
    document.querySelector('#empty-lable').style.display = ''
    scatterWeight.setOption({
      series: [
        {
          name: "Radar 1",
          type: "scatter",
          data: [[radarX_1, radarY_1]],
        },
        // {
        //   name: "Radar 2",
        //   type: "scatter",
        //   data: [[radarX_2, radarY_2]],
        // },
        {
          name: "Person 1",
          type: "scatter",
          data: [],
        },
      ],
    });
  }
  if(Math.round((new Date() - checkVitalDataEmpty)/1000)>180){
    heartRateData.innerText = "-"
    breathRateData.innerText = "-"
  }
}, 5000)

if (!checkLogin()) {
  window.location.href = loginPage;
}

roomI = window.location.href.split("=")[1];

roomD = {
  ROOM_UUID: roomI,
  // DETAIL_PAGE: "detail"
};
Object.assign(roomD, RequestData());
fetch(`${host}/api/getRLMacRoom`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(roomD),
})
  .then((response) => response.json())
  .then((data) => {
    // console.log(data)
    if ("DATA" in data){
      data.DATA.forEach(d => {
        if(d.TYPE == "1" || d.TYPE == "2"){
          macPos = d.MAC
          radarX_1 = d.DEPLOY_X
          radarY_1 = d.DEPLOY_Y
        }
        if(d.TYPE == "3"){
          // if(macPos == null){
          //   macPos = d.MAC
          //   radarX_1 = d.DEPLOY_X
          //   radarY_1 = d.DEPLOY_Y
          // }
          macVital = d.MAC
          radarX_2 = d.DEPLOY_X
          radarY_2 = d.DEPLOY_Y
        }
      })
      fetch(`${host}/api/getRoomDetail`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(roomD),
      })
        .then((response) => response.json())
        .then((data) => {
          // console.log(data);
          // use graphic
          if ("DATA" in data) {
            detailPageHeader.innerHTML = `<h1>${data.DATA[0]['ROOM_NAME']} @ ${data.DATA[0]['ROOM_LOC']}</h1>`
            data.DATA.forEach((element) => {
              // console.log("x")
              var heatMapImage = new Image();
              // macPos = element.POS_MAC
              // macVital = element.VITAL_MAC
              getAnalyticData()
              heatMapImage.src =
                "http://143.198.199.16:5000/static/uploads/" + element.IMAGE_NAME;
              heatMapImage.onload = function () {
                const rectheatmap = hisotryLocHeatmapChart._api
                  .getCoordinateSystems()[0]
                  .getRect();
                heatMapImage.width = rectheatmap.width;
                heatMapImage.height = rectheatmap.height;
                roomX = element.ROOM_X;
                roomY = element.ROOM_Y;
                roomXD = roomX
                roomYD = roomY
                X = [];
                Y = [];
                let i = 0;
                while (i < roomX) {
                  // X.push(i.toFixed(1));
                  X.push(i.toFixed(2));
                  // i += 0.01;
                  i += 0.1;
                }
                let j = 0;
                while (j < roomY) {
                  // Y.push(j.toFixed(1));
                  Y.push(j.toFixed(2));
                  // j += 0.01;
                  j += 0.1;
                }
                // console.log(element.ROOM_X, element.ROOM_Y)
                
                for(i=0; i<(element.ROOM_X*10); i++){
                  for(j=0; j<(element.ROOM_Y*10); j++){
                    sampleLocData.push([parseFloat(i.toFixed(1)), parseFloat(j.toFixed(1)), 0])
                  }
                }
                // console.log(sampleLocData);
                // console.log(roomX, roomY, X, Y)
                hisotryLocHeatmapChart.setOption({
                  graphic: [
                    {
                      id: "bg",
                      type: "image",
                      style: {
                        image: image,
                        x: rectheatmap.x,
                        y: rectheatmap.y,
                      },
                    },
                  ],
                  xAxis: {
                    data: X,
                  },
                  yAxis: {
                    // textStyle: {
                    //   color: "#fff",
                    // },
                    data: Y,
                  },
                });
              };
              getHistorOfPos("HOUR", roomXD, roomYD);
              // getHistOfVital("1 HOUR");
              var image = new Image();
              image.src =
                "http://143.198.199.16:5000/static/uploads/" + element.IMAGE_NAME;
              image.onload = function () {
                const rect = scatterWeight._api.getCoordinateSystems()[0].getRect();
                image.width = rect.width;
                image.height = rect.height;
                
                // if(element.POS_X > 0 || element.POS_Y > 0){
                //   radarX_1 = element.POS_X;
                //   radarY_1 = element.POS_Y;
                // }
                // if(element.VITAL_X > 0 || element.VITAL_Y > 0){
                //   radarX_2 = element.VITAL_X;
                //   radarY_2 = element.VITAL_Y;
                // }
                roomX = element.ROOM_X;
                roomY = element.ROOM_Y;
      
                scatterWeight.setOption({
                  graphic: [
                    {
                      id: "bg",
                      type: "image",
                      style: {
                        image: image,
                        x: rect.x,
                        y: rect.y,
                      },
                    },
                  ],
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
                  series: [
                    {
                      name: "Radar 1",
                      type: "scatter",
                      data: [[radarX_1, radarY_1]],
                    },
                    // {
                    //   name: "Radar 2",
                    //   type: "scatter",
                    //   data: [[radarX_2, radarY_2]],
                    // },
                    {
                      name: "Person 1",
                      type: "scatter",
                      data: [],
                    },
                  ],
                });
                // TODO listen to resize, update the width/height/x/y of image according to the grid rect
              };
              
            });
            // console.log(initLegendD, intiSeriesD)
          }
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    }
  })
  .catch((error) => {
    console.error("Error:", error);
  });

mac = window.location.href.split("=")[1];
homeMacVal = mac;

function getHistorOfPos(t, XD, YD) {
  console.time()
  lData = {
    DEVICEMAC: macPos?macPos:macVital,
    TIME: t,
  };
  Object.assign(lData, RequestData());
  hisotryLocHeatmapChart.showLoading();
  fetch(`${host}/api/getSummaryPositionData`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(lData),
  })
    .then((response) => response.json())
    .then((data) => {
      // console.log(data);
      console.timeEnd()
      hisotryLocHeatmapChart.hideLoading();
      minX = 0;
      maxX = 2;
      if (t == "HOUR") {
        maxX = .1;
      } else if (t == "DAY") {
        maxX = 1;
      } else if (t == "WEEK") {
        maxX = 7;
      } else if (t == "MONTH") {
        maxX = 30;
      }
      if("DATA" in data){
        if (data.DATA.length > 0) {
          data.SAMPLE.forEach(d => {
            // xyChange = d.map(function (item) {
            //   // return [item[0] * 100, item[1] * 100, item[2] || "-"];
            //   return [item[0], item[1], item[2] || "-"];
            // });
            // console.log(xyChange);
            console.log(d)
            hisotryLocHeatmapChart.setOption({
              visualMap: {
                min: minX,
                max: maxX,
              },
              series: [
                {
                  name: "Person most spend time",
                  type: "heatmap",
                  data: d,
                },
              ],
            });
          })
          // data.DATA.forEach((d) => {
          //   // formatD = d.split(",");
          //   // let j = 0;
          //   // farr = [];
          //   // sarr = [];
          //   // formatD.forEach((d) => {
          //   //   // console.log(d)
          //   //   let x;
          //   //   x = d.replace(/\[\[|\[|\]/g, "");
          //   //   // console.log(x);
          //   //   if (j < 3) {
          //   //     sarr.push(parseFloat(x));
          //   //     j++;
          //   //   } else {
          //   //     // console.log(sarr);
          //   //     farr.push(sarr);
          //   //     j = 1;
          //   //     sarr = [];
          //   //     sarr.push(parseFloat(x));
          //   //   }
          //   // });
          //   // console.log(farr)
          //   // for(var i=0; i<XD; i+=0.01){
          //   //   for(j=0; j<YD; j+=0.01){
          //   //     // console.log(i.toFixed(2), j.toFixed(2))
          //   //     let tempArr = [i, j]
          //   //     farr.forEach(d => {
          //   //       if(d[0][1] == tempArr[i, j]){
          //   //         console.log(d)
          //   //       } else {
          //   //         farr.push([i,j,0])
          //   //       }
          //   //     })
          //   //   }
          //   // }
          //   // console.log(farr)
          //   xyChange = d.map(function (item) {
          //     // return [item[0] * 100, item[1] * 100, item[2] || "-"];
          //     return [item[0], item[1], item[2] || "-"];
          //   });
          //   // console.log(xyChange);
          //   hisotryLocHeatmapChart.setOption({
          //     visualMap: {
          //       min: minX,
          //       max: maxX,
          //     },
          //     series: [
          //       {
          //         name: "Person most spend time",
          //         type: "heatmap",
          //         data: xyChange,
          //       },
          //     ],
          //   });
          // });
        }
      }
      if("ERROR" in data){
        // console.log(sampleLocData)
        xyChange = sampleLocData.map(function (item) {
          // return [item[0] * 100, item[1] * 100, item[2] || "-"];
          return [item[0], item[1], item[2] || "-"];
        });
        // console.log(xyChange);
        hisotryLocHeatmapChart.setOption({
          visualMap: {
            min: minX,
            max: maxX,
          },
          series: [
            {
              name: "Person most spend time",
              type: "heatmap",
              data: xyChange,
            },
          ],
        });
      }
      
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

async function getAnalyticData(){
  console.time('history')
  aData = {
    // DEVICEMAC: mac,
    CUSTOM: 0,
    ROOM_UUID: roomI,
    // TIME: t
  };
  Object.assign(aData, RequestData());
  multiBarHoriChart.showLoading();
  fetch(`${host}/api/getAnalyticData`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(aData),
  })
    .then((response) => response.json())
    .then((data) => {
      console.timeEnd('history')
      console.log(data)
      // console.log(data.DATA[0]['IN_ROOM_PCT'], data.DATA[0]['IN_BED_PCT']);
      multiBarHoriChart.hideLoading();
      if (data.DATA) { 
          if(data.DATA[0]['IN_BED_SECONDS_HOUR'] > 0){
            inBedHour.innerHTML = `${data.DATA[0]['IN_BED_SECONDS_HOUR']} S` 
            console.log(parseFloat(data.DATA[0]['IN_BED_PCT_HOUR']) > 85)
            if(parseFloat(data.DATA[0]['IN_BED_PCT_HOUR']) > 85){              
              inBedHour.style.right = "45%"
            }
          } else 
            inBedHour.innerHTML = '0 S'
          if(data.DATA[0]['IN_ROOM_SECONDS_HOUR'] > 0){
            inRoomHour.innerHTML = `${data.DATA[0]['IN_ROOM_SECONDS_HOUR']} S`
            if(parseFloat(data.DATA[0]['IN_ROOM_PCT_HOUR']) > 85){
              inRoomHour.style.right = "45%"
            }
          } else
            inRoomHour.innerHTML = '0 S'
          if(data.DATA[0]['IN_BED_SECONDS_DAY'] > 0) {
            inBedDay.innerHTML = `${secondsToHours(data.DATA[0]['IN_BED_SECONDS_DAY'])} H`
            if(parseFloat(data.DATA[0]['IN_BED_PCT_DAY']) > 85){
              inBedDay.style.right = "45%"
            }
          } else 
            inBedDay.innerHTML = '0 H'
          if(data.DATA[0]['IN_ROOM_SECONDS_DAY'] > 0) {
            inRoomDay.innerHTML = `${secondsToHours(data.DATA[0]['IN_ROOM_SECONDS_DAY'])} H`
            if(parseFloat(data.DATA[0]['IN_ROOM_PCT_DAY']) > 85){
              inRoomDay.style.right = "45%"
            }
          } else
            inRoomDay.innerHTML = '0 H'
          if(data.DATA[0]['IN_BED_SECONDS_WEEK'] > 0) {
            inBedWeek.innerHTML = `${secondsToHours(data.DATA[0]['IN_BED_SECONDS_WEEK'])} H`
            if(parseFloat(data.DATA[0]['IN_BED_PCT_WEEK']) > 85){
              inBedWeek.style.right = "45%"
            }
          } else 
            inBedWeek.innerHTML = '0 H'
          if(data.DATA[0]['IN_ROOM_SECONDS_WEEK'] > 0) {
            inRoomWeek.innerHTML = `${secondsToHours(data.DATA[0]['IN_ROOM_SECONDS_WEEK'])} H`
            if(parseFloat(data.DATA[0]['IN_ROOM_PCT_WEEK']) > 85){
              inRoomWeek.style.right = "45%"
            }
          } else
            inRoomWeek.innerHTML = '0 H'
          if(data.DATA[0]['IN_BED_SECONDS_MONTH'] > 0) {
            inBedMonth.innerHTML = `${secondsToHours(data.DATA[0]['IN_BED_SECONDS_MONTH'])} H` 
            if(parseFloat(data.DATA[0]['IN_BED_PCT_MONTH']) > 85){
              inBedMonth.style.right = "45%"
            }
          } else 
            inBedMonth.innerHTML = '0 H'
          if(data.DATA[0]['IN_ROOM_SECONDS_MONTH'] > 0) {
            inRoomMonth.innerHTML = `${secondsToHours(data.DATA[0]['IN_ROOM_SECONDS_MONTH'])} H`
            if(parseFloat(data.DATA[0]['IN_ROOM_PCT_MONTH']) > 85){
              inRoomMonth.style.right = "45%"
            }
          } else
            inRoomMonth.innerHTML = ''
          multiBarHoriChart.setOption({
            xAxis: {
              max: 100
            },
            yAxis: {
              type: "category",
              data: ["Month", "Week", "Day", "Hour"],
            },
            series: [
              {
                name: "In Bed",
                label: {
                  show: true,
                  position: 'right',
                  valueAnimation: true,
                  formatter: `{c} %`,
                },
                data: [data.DATA[0]['IN_BED_PCT_MONTH'], data.DATA[0]['IN_BED_PCT_WEEK'], data.DATA[0]['IN_BED_PCT_DAY'], data.DATA[0]['IN_BED_PCT_HOUR']],
                // {value: d[1], itemStyle: { color: brightRed}}
              },
              {
                name: "In Room",
                label: {
                  show: true,
                  position: 'right',
                  valueAnimation: true,
                  formatter: `{c} %`,
                },
                data: [data.DATA[0]['IN_ROOM_PCT_MONTH'], data.DATA[0]['IN_ROOM_PCT_WEEK'], data.DATA[0]['IN_ROOM_PCT_DAY'], data.DATA[0]['IN_ROOM_PCT_HOUR']],
                // {value: d[1], itemStyle: { color: brightRed}}
              }
            ],
          })
        // if (data.DATA.length > 2) {
        //   // console.log(data.DATA[0].totalCountInOutRoom, data.DATA[1].countInRoom, data.DATA[2].countInBed)
        //   totalCountInOutRoom = convertStrtoInt(data.DATA[0].totalCountInOutRoom);
        //   countInRoom = convertStrtoInt(data.DATA[1].countInRoom);
        //   countInBed = convertStrtoInt(data.DATA[2].countInBed);
        //   // console.log(totalCountInOutRoom, countInRoom, countInBed)
        //   last1HourInRoom = isWhatPercentOf(
        //     countInRoom[0],
        //     totalCountInOutRoom[0]
        //   );
        //   last1HourInBed = isWhatPercentOf(countInBed[0], totalCountInOutRoom[0]);
        //   last6HourInRoom = isWhatPercentOf(
        //     countInRoom[1],
        //     totalCountInOutRoom[1]
        //   );
        //   last6HourInBed = isWhatPercentOf(countInBed[1], totalCountInOutRoom[1]);
        //   last1DayInRoom = isWhatPercentOf(
        //     countInRoom[2],
        //     totalCountInOutRoom[2]
        //   );
        //   last1DayInBed = isWhatPercentOf(countInBed[2], totalCountInOutRoom[2]);
        //   last1WeekInRoom = isWhatPercentOf(
        //     countInRoom[3],
        //     totalCountInOutRoom[3]
        //   );
        //   last1WeekInBed = isWhatPercentOf(countInBed[3], totalCountInOutRoom[3]);
        //   last1MonthInRoom = isWhatPercentOf(
        //     countInRoom[4],
        //     totalCountInOutRoom[4]
        //   );
        //   last1MonthInBed = isWhatPercentOf(
        //     countInBed[4],
        //     totalCountInOutRoom[4]
        //   );
        //   if (isNaN(last1HourInRoom)) last1HourInRoom = 0;
        //   if (isNaN(last1HourInBed)) last1HourInBed = 0;
        //   if (isNaN(last6HourInRoom)) last6HourInRoom = 0;
        //   if (isNaN(last6HourInBed)) last6HourInBed = 0;
        //   if (isNaN(last1DayInRoom)) last1DayInRoom = 0;
        //   if (isNaN(last1DayInBed)) last1DayInBed = 0;
        //   if (isNaN(last1WeekInRoom)) last1WeekInRoom = 0;
        //   if (isNaN(last1WeekInBed)) last1WeekInBed = 0;
        //   if (isNaN(last1MonthInRoom)) last1MonthInRoom = 0;
        //   if (isNaN(last1MonthInBed)) last1MonthInBed = 0;
          
        //   multiBarHoriChart.setOption({
        //     yAxis: {
        //       type: "category",
        //       data: ["1 Hour", "6 Hour", "1 Day", "1 Week", "1 Month"],
        //     },
        //     series: [
        //       {
        //         name: "In Room",
        //         label: {
        //           formatter: `{c} %`,
        //         },
        //         data: [
        //           Math.round(last1HourInRoom, 2),
        //           Math.round(last6HourInRoom, 2),
        //           Math.round(last1DayInRoom, 2),
        //           Math.round(last1WeekInRoom, 2),
        //           Math.round(last1MonthInRoom, 2),
        //         ],
        //       },
        //       {
        //         name: "In Bed",
        //         label: {
        //           formatter: `{c} %`,
        //         },
        //         data: [
        //           Math.round(last1HourInBed, 2),
        //           Math.round(last6HourInBed, 2),
        //           Math.round(last1DayInBed, 2),
        //           Math.round(last1WeekInBed, 2),
        //           Math.round(last1MonthInBed, 2),
        //         ],
        //       },
        //       {
        //         name: "Out Room",
        //         type: "bar",
        //         label: {
        //           formatter: `{c} %`,
        //         },
        //         data: [
        //           Math.round(100 - last1HourInRoom, 2),
        //           Math.round(100 - last6HourInRoom, 2),
        //           Math.round(100 - last1DayInRoom, 2),
        //           Math.round(100 - last1WeekInRoom, 2),
        //           Math.round(100 - last1MonthInRoom, 2),
        //         ],
        //       },
        //     ],
        //   });
        // }
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}



function convertStrtoInt(arr) {
  total = arr.split(",");
  total[0] = total[0].replace("[", "");
  total[4] = total[4].replace("]", "");
  newArr = [];
  // console.log(total)
  total.forEach((t) => {
    newArr.push(parseInt(t));
  });
  // console.log(newArr)
  return newArr;
}




async function getHistOfVital(t) {
  if(t != "REALTIME"){
    vData = {
      CUSTOM: 0,
      TIME: t,
      ROOM_UUID: roomI,
    };
    Object.assign(vData, RequestData());
    await fetch(`${host}/api/getHistOfVital`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(vData),
    })
      .then((response) => response.json())
      .then((data) => {        
        // console.log(data.DATA.length)
        console.log(data);
        vitalChart.hideLoading();
        histVitalData = []
        histVitalData2 = []
        histVitalTime = []
        if ("DATA" in data) {          
          if (data.DATA.length > 0) {
            data.DATA[0].forEach((d) => {
              // categories.shift();
              // console.log(d)
              if (t == "1 HOUR" || t == "1 DAY") {
                histVitalTime.push(d[0].substring(11, 16));
              } else if (t == "1 WEEK" || t == "1 MONTH") {
                histVitalTime.push(d[0].substring(0, 16));
              }
              // vitalData.shift();
              // vitalData.push(d.HEART_RATE);
              // vitalData2.push(d.BREATH_RATE);
              if(d[1]<100 && d[1]>60){
                histVitalData.push({value: d[1], itemStyle: { color: brightGreen}});
              } else {
                histVitalData.push({value: d[1], itemStyle: { color: brightRed}});
              }
              if(d[2]<20 && d[2]>12){
                // vitalData2.shift();
                histVitalData2.push({value: d[2], itemStyle: { color: brightGreen}});
              } else {
                histVitalData2.push({value: d[2], itemStyle: { color: brightRed}});
              }
            });
            // console.log(`heartRate: ${heartRate} \n breathRate: ${breathRate} \n time: ${timeStamp}`)
            // heartRateData.innerText = data.AVG[0][0]?data.AVG[0][0]+" (Avg)":0 
            // breathRateData.innerText = data.AVG[0][1]?data.AVG[0][1]+" (Avg)":0 
            // console.log(data.AVG[0][0], data.AVG[0][1])            
          }
        } else {
          histVitalData = randR()
          histVitalData2 = randR()
          histVitalTime = gen2STime()
        }

        vitalChart.setOption({
          xAxis: [
            {
              data: histVitalTime,
            },
            {
              data: histVitalTime,
              gridIndex: 1,
            },
          ],
          series: [
            {
              name: "Heart Waveform",
              type: "bar",
              smooth: true,
              emphasis: {
                focus: "series",
              },
              data: histVitalData,                  
            },
            {
              name: "Breath Waveform",
              type: "bar",
              smooth: true,
              emphasis: {
                focus: "series",
              },
              data: histVitalData2,
              xAxisIndex: 1,
              yAxisIndex: 1,                  
            },
          ],
        });
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  } else {
    vitalChart.hideLoading()
    // heartRateData.innerText = "-" 
    // breathRateData.innerText = "-" 
    vitalChart.setOption({
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
          name: "Heart Rate",
          type: "bar",
          smooth: true,
          emphasis: {
            focus: "series",
          },
          data: vitalData,
        },
        {
          name: "Breathing Rate",
          type: "bar",
          smooth: true,
          emphasis: {
            focus: "series",
          },
          data: vitalData2,
          xAxisIndex: 1,
          yAxisIndex: 1,
        },
      ],
    });
  }  
}

// get history of data
async function getSelectedData() {
  // clearInterval(interval)
  vitalChart.showLoading();
  homeTimeSelectSubmitBtn.disabled = true;
  let response = [];
  let Rdata = {};
  if (homeTimeSelect.value == "CUSTOM")
    Rdata = {
      CUSTOM: 1,
      TIME: homeDateRangePicker.value,
      DEVICEMAC: homeMacVal,
    };
  else
    Rdata = {
      CUSTOM: 0,
      TIME: homeTimeSelect.value,
      DEVICEMAC: homeMacVal,
    };
  // console.log(Rdata)
  console.time("timer1");
  Object.assign(Rdata, RequestData());
  await fetch(`${host}/api/getData`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(Rdata),
  })
    .then((response) => response.json())
    .then((data) => {
      console.timeEnd("timer1");
      homeTimeSelectSubmitBtn.disabled = false;
      progress.hidden = false; // progress bar will show if real time is not selected
      // console.log(data.DATA.length)
      console.log(data);
      vitalChart.hideLoading();
      if ("DATA" in data) {
        if (data.DATA.length > 0) {
          breathRate = [];
          heartRate = [];
          timeStamp = [];
          data.DATA.forEach((d) => {
            if (d.BREATH_RATE != null) {
              breathRate.push(d.BREATH_RATE);
              if (
                (homeTimeSelect.value != "CUSTOM") &
                (homeTimeSelect.value != "REAL TIME")
              ) {
                timeStamp.push(d.TIMESTAMP.substring(17, 25));
              } else if (homeTimeSelect.value == "CUSTOM") {
                date = homeDateRangePicker.value.split(" - ");
                date1 = new Date(date[0]);
                date2 = new Date(date[1]);
                diff = date2 - date1;
                hours = diff / 3600000;
                if (hours < 24) {
                  timeStamp.push(d.TIMESTAMP.substring(17, 25));
                } else {
                  date = new Date(d.TIMESTAMP);
                  dateS =
                    date.getFullYear() +
                    "/" +
                    date.getMonth() +
                    1 +
                    "/" +
                    date.getDate() +
                    " " +
                    date.getHours() +
                    ":" +
                    date.getMinutes() +
                    ":" +
                    date.getSeconds();
                  timeStamp.push(dateS);
                }
              }
            }
            if (d.HEART_RATE != null) {
              heartRate.push(d.HEART_RATE);
            }
          });
          // console.log(`heartRate: ${heartRate} \n breathRate: ${breathRate} \n time: ${timeStamp}`)

          vitalChart.setOption({
            xAxis: [
              {
                gridIndex: 0,
                data: timeStamp,
              },
              {
                gridIndex: 1,
                data: timeStamp,
              },
            ],
            series: [
              {
                data: heartRate,
                xAxisIndex: 0,
                yAxisIndex: 0,
              },
              {
                data: breathRate,
                xAxisIndex: 1,
                yAxisIndex: 1,
              },
            ],
          });
        }
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      progressBar.style.width = 100 + "%";
      progressBar.innerHTML = "100 %";
      homeTimeSelectSubmitBtn.disabled = false;
      // alert('Selected time have some issues, please try select different time')
    });
  // console.log(response);
  return response;
}

// new DateTimePickerComponent.DateTimeRangePicker('start', 'end');
// $(function () {
//   $('input[name="datetimes"]').daterangepicker({
//     timePicker: true,
//     showDropdowns: true,
//     minYear: 1901,
//     maxYear: parseInt(moment().format("YYYY"), 10),
//     startDate: moment().startOf("hour"),
//     endDate: moment().startOf("hour").add(32, "hour"),
//     // timePicker24Hour: true,
//     locale: {
//       format: "YYYY/M/DD H:mm:ss",
//     },
//   });
// });

hourHistLoc.addEventListener("click", function () {
  getHistorOfPos("HOUR", roomXD, roomYD);
});

dayHistLoc.addEventListener("click", function () {
  getHistorOfPos("DAY", roomXD, roomYD);
});

weekHistLoc.addEventListener("click", function () {
  getHistorOfPos("WEEK", roomXD, roomYD);
});

monthHistLoc.addEventListener("click", function () {
  getHistorOfPos("MONTH", roomXD, roomYD);
});

realtimeHistVital.addEventListener("click", function () {
  vitalChart.showLoading()
  getHistOfVital("REALTIME");
});

hourHistVital.addEventListener("click", function () {
  vitalChart.showLoading()
  getHistOfVital("1 HOUR");
});

dayHistVital.addEventListener("click", function () {
  vitalChart.showLoading()
  getHistOfVital("1 DAY");
});

weekHistVital.addEventListener("click", function () {
  vitalChart.showLoading()
  getHistOfVital("1 WEEK");
});

monthHistVital.addEventListener("click", function () {
  vitalChart.showLoading()
  getHistOfVital("1 MONTH");
});

// hourHistPosture.addEventListener("click", function () {
//   multiBarHoriChart.showLoading()
//   getAnalyticData("1 HOUR");
// });

// dayHistPosture.addEventListener("click", function () {
//   multiBarHoriChart.showLoading()
//   getAnalyticData("1 DAY");
// });

// weekHistPosture.addEventListener("click", function () {
//   multiBarHoriChart.showLoading()
//   getAnalyticData("1 WEEK");
// });

// monthHistPosture.addEventListener("click", function () {
//   multiBarHoriChart.showLoading()
//   getAnalyticData("1 MONTH");
// });
