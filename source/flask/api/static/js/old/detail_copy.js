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
const hourHistVital = document.getElementById("hour-vital-tab");
const dayHistVital = document.getElementById("day-vital-tab");
const weekHistVital = document.getElementById("week-vital-tab");
const monthHistVital = document.getElementById("month-vital-tab");
var homeMacVal, homeTimeSelVal;

if (!checkLogin()) {
  window.location.href = loginPage;
}

macI = window.location.href.split("=")[1];

roomD = {
  MAC: macI,
};
Object.assign(roomD, RequestData());
fetch(`${host}/api/getRoomDetails`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(roomD),
})
  .then((response) => response.json())
  .then((data) => {
    console.log(data);
    // use graphic
    if ("DATA" in data) {
      data.DATA.forEach((element) => {
        var heatMapImage = new Image();
        heatMapImage.src =
          `${host}/static/images/` + element.IMAGE_NAME;
        heatMapImage.onload = function () {
          const rectheatmap = hisotryLocHeatmapChart._api
            .getCoordinateSystems()[0]
            .getRect();
          heatMapImage.width = rectheatmap.width;
          heatMapImage.height = rectheatmap.height;
          roomX = element.ROOM_X;
          roomY = element.ROOM_Y;
          X = [];
          Y = [];
          let i = 0;
          while (i < roomX) {
            X.push(i.toFixed(2));
            i += 0.01;
            // i += 0.1;
          }
          let j = 0;
          while (j < roomY) {
            Y.push(j.toFixed(2));
            j += 0.01;
            // j += 0.1;
          }
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
        getHistorOfPos("HOUR");
        var image = new Image();
        image.src =
          "${host}/static/images/" + element.IMAGE_NAME;
        image.onload = function () {
          const rect = scatterWeight._api.getCoordinateSystems()[0].getRect();
          image.width = rect.width;
          image.height = rect.height;
          radarX = element.RADAR_X_LOC;
          radarY = element.RADAR_Y_LOC;
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
                name: "Radar",
                type: "scatter",
                data: [[element.RADAR_X_LOC, element.RADAR_Y_LOC]],
              },
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
    }
  })
  .catch((error) => {
    console.error("Error:", error);
  });
mac = window.location.href.split("=")[1];
homeMacVal = mac;
// rData = {
//   MAC: mac,
// };
// Object.assign(rData, RequestData());

// fetch(`${host}/getRegDevice`, {
//   method: "POST",
//   headers: {
//     "Content-Type": "application/json",
//   },
//   body: JSON.stringify(rData),
// })
//   .then((response) => response.json())
//   .then((data) => {
//     console.log(data);
//     if (data.DATA) {
//       data.DATA.forEach((d) => {
//         let option = document.createElement("option");
//         option.setAttribute("value", d.MAC);
//         option.innerText = d.NAME;
//         homeMacAddrSelect.appendChild(option);
//       });
//       homeMacVal = homeMacAddrSelect.value;
//       homeTimeSelVal = homeTimeSelect.value;
//     }
//   })
//   .catch((error) => {
//     console.error("Error:", error);
//   });

function getHistorOfPos(t) {
  lData = {
    DEVICEMAC: mac,
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
      hisotryLocHeatmapChart.hideLoading();
      minX = 0;
      maxX = 30;
      if (t == "HOUR") {
        maxX = 30;
      } else if (t == "DAY") {
        maxX = 50;
      } else if (t == "WEEK") {
        maxX = 100;
      } else if (t == "MONTH") {
        maxX = 150;
      }
      if (data.DATA.length > 0) {
        data.DATA.forEach((d) => {
          formatD = d.split(",");
          let j = 0;
          farr = [];
          sarr = [];
          formatD.forEach((d) => {
            // console.log(d)
            let x;
            x = d.replace(/\[\[|\[|\]/g, "");
            // console.log(x);
            if (j < 3) {
              sarr.push(parseFloat(x));
              j++;
            } else {
              // console.log(sarr);
              farr.push(sarr);
              j = 1;
              sarr = [];
              sarr.push(parseFloat(x));
            }
          });

          xyChange = farr.map(function (item) {
            return [item[0] * 100, item[1] * 100, item[2] || "-"];
            // return [item[0] * 10, item[1] * 10, item[2] || "-"];
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
        });
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

aData = {
  DEVICEMAC: mac,
  CUSTOM: 0,
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
    console.log(data);
    if (data.DATA) {
      multiBarHoriChart.hideLoading();
      if (data.DATA.length > 2) {
        // console.log(data.DATA[0].totalCountInOutRoom, data.DATA[1].countInRoom, data.DATA[2].countInBed)
        totalCountInOutRoom = convertStrtoInt(data.DATA[0].totalCountInOutRoom);
        countInRoom = convertStrtoInt(data.DATA[1].countInRoom);
        countInBed = convertStrtoInt(data.DATA[2].countInBed);
        // console.log(totalCountInOutRoom, countInRoom, countInBed)
        last1HourInRoom = isWhatPercentOf(
          countInRoom[0],
          totalCountInOutRoom[0]
        );
        last1HourInBed = isWhatPercentOf(countInBed[0], totalCountInOutRoom[0]);
        last6HourInRoom = isWhatPercentOf(
          countInRoom[1],
          totalCountInOutRoom[1]
        );
        last6HourInBed = isWhatPercentOf(countInBed[1], totalCountInOutRoom[1]);
        last1DayInRoom = isWhatPercentOf(
          countInRoom[2],
          totalCountInOutRoom[2]
        );
        last1DayInBed = isWhatPercentOf(countInBed[2], totalCountInOutRoom[2]);
        last1WeekInRoom = isWhatPercentOf(
          countInRoom[3],
          totalCountInOutRoom[3]
        );
        last1WeekInBed = isWhatPercentOf(countInBed[3], totalCountInOutRoom[3]);
        last1MonthInRoom = isWhatPercentOf(
          countInRoom[4],
          totalCountInOutRoom[4]
        );
        last1MonthInBed = isWhatPercentOf(
          countInBed[4],
          totalCountInOutRoom[4]
        );
        if (isNaN(last1HourInRoom)) last1HourInRoom = 0;
        if (isNaN(last1HourInBed)) last1HourInBed = 0;
        if (isNaN(last6HourInRoom)) last6HourInRoom = 0;
        if (isNaN(last6HourInBed)) last6HourInBed = 0;
        if (isNaN(last1DayInRoom)) last1DayInRoom = 0;
        if (isNaN(last1DayInBed)) last1DayInBed = 0;
        if (isNaN(last1WeekInRoom)) last1WeekInRoom = 0;
        if (isNaN(last1WeekInBed)) last1WeekInBed = 0;
        if (isNaN(last1MonthInRoom)) last1MonthInRoom = 0;
        if (isNaN(last1MonthInBed)) last1MonthInBed = 0;
        // console.log(
        //   last1HourInRoom,
        //   last1HourInBed,
        //   last6HourInRoom,
        //   last6HourInBed,
        //   last1DayInRoom,
        //   last1DayInBed,
        //   last1WeekInRoom,
        //   last1WeekInBed,
        //   last1MonthInRoom,
        //   last1MonthInBed
        // );
        multiBarHoriChart.setOption({
          yAxis: {
            type: "category",
            data: ["1 Hour", "6 Hour", "1 Day", "1 Week", "1 Month"],
          },
          series: [
            {
              name: "In Room",
              label: {
                formatter: `{c} %`,
              },
              data: [
                Math.round(last1HourInRoom, 2),
                Math.round(last6HourInRoom, 2),
                Math.round(last1DayInRoom, 2),
                Math.round(last1WeekInRoom, 2),
                Math.round(last1MonthInRoom, 2),
              ],
            },
            {
              name: "In Bed",
              label: {
                formatter: `{c} %`,
              },
              data: [
                Math.round(last1HourInBed, 2),
                Math.round(last6HourInBed, 2),
                Math.round(last1DayInBed, 2),
                Math.round(last1WeekInBed, 2),
                Math.round(last1MonthInBed, 2),
              ],
            },
            {
              name: "Out Room",
              type: "bar",
              label: {
                formatter: `{c} %`,
              },
              data: [
                Math.round(100 - last1HourInRoom, 2),
                Math.round(100 - last6HourInRoom, 2),
                Math.round(100 - last1DayInRoom, 2),
                Math.round(100 - last1WeekInRoom, 2),
                Math.round(100 - last1MonthInRoom, 2),
              ],
            },
          ],
        });
      }
    }
  })
  .catch((error) => {
    console.error("Error:", error);
  });

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

// check real time or custom time select
// homeTimeSelect.addEventListener("change", (e) => {
//   homeTimeSelVal = e.target.value;
//   if (e.target.value == "CUSTOM") {
//     homeDateTimeRow.style.display = "";
//     // homeTimeSelectSubmitRow.style.display = "";
//     // console.log(homeDateRangePicker.value)
//     linechartDom.style.display = "none";
//     trackChartRow.style.display = "none";
//     vitalDom.style.display = "";
//     vitalAnalyticChart.resize();
//     vitalAnalyticChart.showLoading();
//   } else if (e.target.value == "REAL TIME") {
//     homeDateTimeRow.style.display = "none";
//     vitalDom.style.display = "none";
//     trackChartRow.style.display = "";
//     linechartDom.style.display = "";
//     // heartIcon.style.display = '';
//     // breathIcon.style.display = '';
//     scatter3d.resize();
//     scatterWeight.resize();
//     lineChart.resize();
//     // homeTimeSelectSubmitRow.style.display = "none";
//     progress.hidden = true;
//   } else {
//     homeDateTimeRow.style.display = "none";
//     linechartDom.style.display = "none";
//     trackChartRow.style.display = "none";
//     // heartIcon.style.display = 'none';
//     // breathIcon.style.display = 'none';
//     vitalDom.style.display = "";
//     vitalAnalyticChart.resize();
//     vitalAnalyticChart.showLoading();
//     // homeTimeSelectSubmitRow.style.display = "none";
//     // progress.hidden = false
//     getSelectedData();
//   }
//   // console.log(homeTimeSelVal)
// });

// homeMacAddrSelect.addEventListener("change", (e) => {
//   // console.log(e.target.value)
//   homeMacVal = e.target.value;
// });

getHistOfVital("1 HOUR");

async function getHistOfVital(t) {
  vData = {
    CUSTOM: 0,
    TIME: t,
    DEVICEMAC: mac,
  };
  Object.assign(vData, RequestData());
  await fetch(`${host}/api/getData`, {
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
      vitalAnalyticChart.hideLoading();
      if ("DATA" in data) {
        if (data.DATA.length > 0) {
          breathRate = [];
          heartRate = [];
          timeStamp = [];
          data.DATA.forEach((d) => {
            if (d.BREATH_RATE != null) {
              breathRate.push(d.BREATH_RATE);
              if (t == "1 HOUR" || t == "1 DAY") {
                timeStamp.push(d.TIMESTAMP.substring(17, 25));
              } else if (t == "1 WEEK" || t == "1 MONTH") {
                date = new Date(d.TIMESTAMP);
                dateS =
                  date.getFullYear() +
                  "/" +
                  date.getMonth() +
                  1 +
                  "/" +
                  date.getDate()
                timeStamp.push(dateS);
              }
            }
            if (d.HEART_RATE != null) {
              heartRate.push(d.HEART_RATE);
            }
          });
          // console.log(`heartRate: ${heartRate} \n breathRate: ${breathRate} \n time: ${timeStamp}`)

          vitalAnalyticChart.setOption({
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
    });
}

// get history of data
async function getSelectedData() {
  // clearInterval(interval)
  vitalAnalyticChart.showLoading();
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
      vitalAnalyticChart.hideLoading();
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

          vitalAnalyticChart.setOption({
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
      // if('DATA' in data){ // check data receiving?
      //   preve = 0
      //   document.querySelector
      //   var index=0;
      //   var interval = setInterval(function(){ // set time interval to display recived data
      //     d = data.DATA
      //     // console.log(d[index].timestamp, d[index].trackData[0][1], d[index].trackData[0][2], d[index].trackData[0][3], d[index].numDetectedTracks)
      //     scatter3D = [['x', 'y', 'z'],[0,0,0]]
      //     legendD = ['Radar']
      //     for (i=1; i<=d[index].trackData.length; i++){
      //       legendD.push('Person '+i)
      //     }
      //     seriesD = [{
      //       name: "Radar",
      //       type: 'scatter',
      //       data: [[0,0]]
      //     }]
      //     for (i=0;i<d[index].trackData.length; i++){
      //       scatter3D.push([d[index].trackData[i][1].toFixed(2), d[index].trackData[i][2].toFixed(2), d[index].trackData[i][3].toFixed(2)])
      //       seriesD.push({
      //         name: 'Person ' +(i+1),
      //         type: 'scatter',
      //         data: [[d[index].trackData[i][1].toFixed(2), d[index].trackData[i][2].toFixed(2)]],
      //         markArea: {
      //           silent: true,
      //           itemStyle: {
      //             color: 'transparent',
      //             borderWidth: 1,
      //             borderType: 'dashed'
      //           },
      //           data: [
      //             [
      //               {
      //                 name: 'Person '+(i+1),
      //                 xAxis: 'min',
      //                 yAxis: 'min'
      //               },
      //               {
      //                 xAxis: 'max',
      //                 yAxis: 'max'
      //               }
      //             ]
      //           ]
      //         },
      //         markPoint: {
      //           data: [
      //             { type: 'max', name: 'Max' },
      //             { type: 'min', name: 'Min' }
      //           ],
      //           symbol: 'pin'
      //         },
      //       })
      //     }
      //     if(preve > legendD.length){
      //       for(i=0; i<preve-legendD.length; i++){
      //         seriesD.push({
      //           name: '',
      //           type: '',
      //           data: [],
      //           markArea: {data:[]},
      //           markPoint: {data:[]}
      //         })
      //       }
      //     }
      //     setData(scatter3D)
      //     preve = legendD.length
      //     // seriesD.push({})
      //     chartTime.innerHTML = "Time: "+d[index].timestamp
      //     scatterWeight.setOption({
      //       legend:{
      //         data: legendD
      //       },
      //       xAxis: [{
      //         axisLabel: {
      //           formatter: '{value} m'
      //         },
      //         min: -3,
      //         max: 3
      //       }],
      //       yAxis: [{
      //         axisLabel: {
      //           formatter: '{value} m'
      //         },
      //         min: 0,
      //         max: 3
      //       }],
      //       series: seriesD
      //     })
      //     data2.shift()
      //     data2.push(d[index]['numDetectedTracks'])
      //     categories.shift();
      //     categories.push(d[index].timestamp.substring(11))
      //     lineChart.setOption({
      //       xAxis: [
      //         {
      //           data: categories
      //         }
      //       ],
      //       series: [
      //         {
      //           data: data2
      //         }
      //       ]
      //     });
      //     index++
      //     progressBar.style.width = isWhatPercentOf(index, d.length).toFixed(2) +"%"
      //     progressBar.innerHTML = isWhatPercentOf(index, d.length).toFixed(2)+' %'
      //     if(index == d.length){
      //       clearInterval(interval)
      //       index = 0
      //       progressBar.style.width = 100+'%'
      //       progressBar.innerHTML = '100 %'
      //       homeTimeSelectSubmitBtn.disabled = false
      //     }

      //   }, 200)

      // } else {
      //   progressBar.style.width = 100+'%'
      //   progressBar.innerHTML = '100 %'
      //   alert('No data to show on selected time')
      //   homeTimeSelectSubmitBtn.disabled = false
      // }
      // response = data;
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
$(function () {
  $('input[name="datetimes"]').daterangepicker({
    timePicker: true,
    showDropdowns: true,
    minYear: 1901,
    maxYear: parseInt(moment().format("YYYY"), 10),
    startDate: moment().startOf("hour"),
    endDate: moment().startOf("hour").add(32, "hour"),
    // timePicker24Hour: true,
    locale: {
      format: "YYYY/M/DD H:mm:ss",
    },
  });
});

hourHistLoc.addEventListener("click", function () {
  getHistorOfPos("HOUR");
});

dayHistLoc.addEventListener("click", function () {
  getHistorOfPos("DAY");
});

weekHistLoc.addEventListener("click", function () {
  getHistorOfPos("WEEK");
});

monthHistLoc.addEventListener("click", function () {
  getHistorOfPos("MONTH");
});

hourHistVital.addEventListener("click", function () {
  vitalAnalyticChart.showLoading()
  getHistOfVital("1 HOUR");
});

dayHistVital.addEventListener("click", function () {
  vitalAnalyticChart.showLoading()
  getHistOfVital("1 DAY");
});

weekHistVital.addEventListener("click", function () {
  vitalAnalyticChart.showLoading()
  getHistOfVital("1 WEEK");
});

monthHistVital.addEventListener("click", function () {
  vitalAnalyticChart.showLoading()
  getHistOfVital("1 MONTH");
});
