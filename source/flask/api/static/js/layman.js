const roomName = document.getElementById("room-name");

// Sleeping Hour
const sleepingWeeklyAverage = document.getElementById("sleeping-weekly-average");
const sleepingWeeklyLongest = document.getElementById("sleeping-weekly-longest");
const sleepingWeeklyShortest = document.getElementById("sleeping-weekly-shortest");
const sleepingExWeeklyAverage = document.getElementById("sleeping-ex-weekly-average");

// Bed Time
const bedWeeklyAverage = document.getElementById("bed-weekly-average");
const bedWeeklyLongest = document.getElementById("bed-weekly-longest");
const bedWeeklyShortest = document.getElementById("bed-weekly-shortest");
const bedExWeeklyAverage = document.getElementById("bed-ex-weekly-average");

// Morning Wake Up Time
const wakeWeeklyAverage = document.getElementById("wake-weekly-average");
const wakeWeeklyLongest = document.getElementById("wake-weekly-longest");
const wakeWeeklyShortest = document.getElementById("wake-weekly-shortest");
const wakeExWeeklyAverage = document.getElementById("wake-ex-weekly-average");

// Time In Bed
const inbedWeeklyAverage = document.getElementById("inbed-weekly-average");
const inbedWeeklyLongest = document.getElementById("inbed-weekly-longest");
const inbedWeeklyShortest = document.getElementById("inbed-weekly-shortest");
const inbedExWeeklyAverage = document.getElementById("inbed-ex-weekly-average");

// In Room
const inroomWeeklyAverage = document.getElementById("inroom-weekly-average");
const inroomWeeklyLongest = document.getElementById("inroom-weekly-longest");
const inroomWeeklyShortest = document.getElementById("inroom-weekly-shortest");
const inroomExWeeklyAverage = document.getElementById("inroom-ex-weekly-average");

// Sleep disruption
const disruptionWeeklyAverage = document.getElementById("disruption-weekly-average");
const disruptionWeeklyMost = document.getElementById("disruption-weekly-most");
const disruptionWeeklyLeast = document.getElementById("disruption-weekly-least");
const disruptionExWeeklyAverage = document.getElementById("disruption-ex-weekly-average");

// breath Rate
const breathWeeklyAverage = document.getElementById("breath-weekly-average");
const breathWeeklyHighest = document.getElementById("breath-weekly-highest");
const breathWeeklyLowest = document.getElementById("breath-weekly-lowest");
const breathExWeeklyAverage = document.getElementById("breath-ex-weekly-average");

// Heart Rate
const heartWeeklyAverage = document.getElementById("heart-weekly-average");
const heartWeeklyHighest = document.getElementById("heart-weekly-highest");
const heartWeeklyLowest = document.getElementById("heart-weekly-lowest");
const heartExWeeklyAverage = document.getElementById("heart-ex-weekly-average");

const barColors = ['#35A29F', '#088395', '#071952'];

const dateInput = document.getElementById("dateInput");

const sleepPieDom = document.getElementById('sleepPieChart');
const roomPieDom = document.getElementById('roomPieChart');
const bedPieDom = document.getElementById('bedPieChart');
const disruptionBarDom = document.getElementById('disruptionBarChart');
const heartBarDom = document.getElementById('heartBarChart');
const breathBarDom = document.getElementById('breathBarChart');

var sleepClockDom = document.getElementById('sleepClock');
var wakeClockDom = document.getElementById('wakeClock');

const current= new Date();
const current_year = current.getFullYear();
const current_month = String(current.getMonth() + 1).padStart(2, '0');
const current_day = String(current.getDate()).padStart(2, '0');
const formattedDate = `${current_year}-${current_month}-${current_day}`;
dateInput.value = formattedDate;

// Set today as maximum date
dateInput.max = formattedDate

const prevWeekButton = document.getElementById("prev-week");
const nextWeekButton = document.getElementById("next-week");


const closeModalBtn = document.getElementById('closeModalBtn');
const modal = document.getElementById('alertModal');
const noAlertText = document.getElementById('no-alert-text');

closeModalBtn.addEventListener('click', () => {
    modal.style.display = 'none';
});

// Add event listeners to the buttons
prevWeekButton.addEventListener("click", () => changeWeek(-1));
nextWeekButton.addEventListener("click", () => changeWeek(1));

// Function to change the selected week
function changeWeek(weekChange) {
    let curr = new Date(dateInput.value)
    curr.setDate(curr.getDate() + (7 * weekChange ));

    const curr_year = curr.getFullYear();
    const curr_month = String(curr.getMonth() + 1).padStart(2, '0');
    const curr_day = String(curr.getDate()).padStart(2, '0');
    const currformattedDate = `${curr_year}-${curr_month}-${curr_day}`;
    dateInput.value = currformattedDate;

    setLaymanDetails()
}

roomI = window.location.href.split("=")[1];

const historicalButton = document.getElementById("historical-button")
historicalButton.addEventListener("click", function () {
  window.location.href=`${host}/Detail?room=${roomI}`
});

roomD = {
  room_id: roomI,
};

Object.assign(roomD, RequestData());
getAlerts()

const alertHistoryButton = document.getElementById("alert-history-button")
alertHistoryButton.addEventListener("click", function () {
  getAlerts(unread=false)
  modal.style.display = 'flex';
});

function getAlerts(unread=true){

    let body = Object.assign({}, roomD);
    body["unread"] = unread

    fetch(`${host}/api/getRoomAlerts`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      }).then((response) => response.json()).then((data) => {
        
            const table = document.getElementById('dataTable');
          if (data["DATA"].length > 0){

            
            const tableBody = document.getElementById('tableBody');

            while (tableBody.firstChild) {
                tableBody.removeChild(tableBody.firstChild);
            }

            let alerts_id = []

            // Iterate through the data and create table rows
            data["DATA"].forEach(item => {
                alerts_id.push(item.ID)
                const newRow = document.createElement('tr');
                let urgency = ''
                if (item.URGENCY == 0){
                    urgency = `<td style="color:green;">Information</td>`
                }else if (item.URGENCY == 1){
                    urgency = `<td style="color:yellow;">Attention</td>`
                }else if (item.URGENCY == 2){
                    urgency = `<td style="color:orange;">Escalated</td>`
                }else{
                    urgency = `<td style="color:red;">Urgent</td>`
                }

                newRow.innerHTML = `
                    <td>${item.TIMESTAMP}</td>
                    ${urgency}
                    <td>${item.DETAILS}</td>
                `;
                tableBody.appendChild(newRow);
            });

            let read_body = {
                alerts: alerts_id
            }

            console.log(read_body)

            Object.assign(read_body, RequestData());

            if (alerts_id.length > 0){
                fetch(`${host}/api/readRoomAlerts`, {
                    method: "POST",
                    headers: {
                      "Content-Type": "application/json",
                    },
                    body: JSON.stringify(read_body),
                  }).then((response) => response.json()).then((data) => {
                    console.log(data)
                  })
            }

            table.style.display = 'table';
            noAlertText.style.display = 'none';
            modal.style.display = 'flex';
          }else{
            table.style.display = 'none';
            noAlertText.style.display = 'block';
          }

          
      })
}

function timeStringToMinutes(timeString) {
  // Split the string to extract hours and minutes
  var timeParts = timeString.split("h");

  // Initialize hours and minutes
  var hours = 0;
  var minutes = 0;

  if (timeParts.length > 0) {
    hours = parseInt(timeParts[0]);
  }

  // Check if there's a minutes part
  if (timeParts.length > 1) {
    // Extract minutes from the second part
    var minutesPart = timeParts[1].replace("m", "");
    if (minutesPart !== "") {
      minutes = parseInt(minutesPart);
    }
  }

  // Convert hours to minutes and add to the minutes
  var totalMinutes = hours * 60 + minutes;

  return totalMinutes;
}

function extractHourAndMinute(timeString) {
  const timeStr = timeString.split(" ")[0]
  const timeArr = timeStr.split(":")
  console.log(timeArr)
  const hour = parseFloat(timeArr[0]) + (parseInt(timeArr[1])/60)
  const minute = parseInt(timeArr[1])
  return [hour, minute]
}

function setLaymanDetails(){
    let body = Object.assign({}, roomD);
    let curr = dateInput.value
    body["eow"] = curr
    fetch(`${host}/api/getRoomLaymanDetail`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      }).then((response) => response.json()).then((data) => {
          if ("data" in data){
              if ("room_name" in data["data"] && data["data"]["room_name"]){
                  roomName.innerText = data["data"]["room_name"]
              }
              if ("sleeping_hour" in data["data"]){
                  sleepingWeeklyAverage.innerText = data["data"]["sleeping_hour"]["average"]
                  sleepingWeeklyLongest.innerText = data["data"]["sleeping_hour"]["max"]
                  sleepingWeeklyShortest.innerText = data["data"]["sleeping_hour"]["min"]
                  sleepingExWeeklyAverage.innerText = data["data"]["sleeping_hour"]["previous_average"]

                  if (data["data"]["sleeping_hour"]["average"] != "-"){
                    sleepPieDom.style.height = "30vh"
                    var sleepChart = echarts.init(sleepPieDom);
                    var sleepOption;
                    var sleeping_min = 0

                    sleeping_min = timeStringToMinutes(data["data"]["sleeping_hour"]["average"])

                    sleepOption = {
                      legend: {
                        orient: 'vertical',
                        right: '0%',     // Adjust the 'right' property to move it to the right
                        bottom: '10%'     // Adjust the 'bottom' property to move it to the bottom
                      },
                      dataset: [
                        {
                          source: [
                            { value: sleeping_min, name: 'Sleeping' },
                            { value: (60*24)-sleeping_min, name: 'Not Sleeping' }
                          ],
                          
                        }
                      ],
                      series: [
                        {
                          type: 'pie',
                          radius: '70%',
                          center: ['50%', '50%'], // Center the pie chart both horizontally and vertically
                          label: {
                            position: 'inside',
                            formatter: '{d}%',
                            color: 'black',
                            fontSize: 10
                          },
                          percentPrecision: 0,
                          emphasis: {
                            label: { show: true },
                            itemStyle: {
                              shadowBlur: 10,
                              shadowOffsetX: 0,
                              shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                          },
                          // Set colors for each name (category)
                          data: [
                            {
                              value: sleeping_min,
                              name: 'Sleeping',
                              itemStyle: { color: '#088395' } // Set the color for 'Sleeping'
                            },
                            {
                              value: (60 * 24) - sleeping_min,
                              name: 'Not Sleeping',
                              itemStyle: { color: '#35A29F' } // Set the color for 'Not Sleeping'
                            }
                          ]
                        }
                      ]
                    };

                    sleepOption && sleepChart.setOption(sleepOption);
                  }
              }
      
              if ("bed_time" in data["data"]){
                  bedWeeklyAverage.innerText = data["data"]["bed_time"]["average"]
                  bedWeeklyLongest.innerText = data["data"]["bed_time"]["max"]
                  bedWeeklyShortest.innerText = data["data"]["bed_time"]["min"]
                  bedExWeeklyAverage.innerText = data["data"]["bed_time"]["previous_average"]

                  if (data["data"]["bed_time"]["average"] != "-"){
                    sleepClockDom.style.height = "30vh"
                    var sleepClockChart = echarts.init(sleepClockDom);
                    var sleepClockOption;
                    console.log(data["data"]["bed_time"]["average"])
                    const extractedBedData = extractHourAndMinute(data["data"]["bed_time"]["average"])
                    console.log(extractedBedData)

                    sleepClockOption = {
                      series: [
                        {
                          name: 'hour',
                          type: 'gauge',
                          startAngle: 90,
                          endAngle: -270,
                          min: 0,
                          max: 12,
                          splitNumber: 12,
                          clockwise: true,
                          axisLine: {
                            lineStyle: {
                              width: 4,
                              color: [[1, '#071952']],
                            }
                          },
                          axisLabel: {
                            fontSize: 10,
                            distance: 5,
                            formatter: function (value) {
                              if (value === 0) {
                                return '';
                              }
                              return value + '';
                            }
                          },
                          pointer: {
                            icon: 'path://M2.9,0.7L2.9,0.7c1.4,0,2.6,1.2,2.6,2.6v115c0,1.4-1.2,2.6-2.6,2.6l0,0c-1.4,0-2.6-1.2-2.6-2.6V3.3C0.3,1.9,1.4,0.7,2.9,0.7z',
                            width: 4,
                            length: '40%',
                            offsetCenter: [0, '2%'],
                            itemStyle: {
                              color: '#088395',
                              shadowColor: 'rgba(0, 0, 0, 0.3)',
                              shadowBlur: 8,
                              shadowOffsetX: 2,
                              shadowOffsetY: 4
                            }
                          },
                          detail: {
                            show: false
                          },
                          data: [
                            {
                              value: extractedBedData[0]
                            }
                          ]
                        },
                        {
                          name: 'minute',
                          type: 'gauge',
                          startAngle: 90,
                          endAngle: -270,
                          min: 0,
                          max: 60,
                          clockwise: true,
                          axisLine: {
                            show: false
                          },
                          splitLine: {
                            show: false
                          },
                          axisTick: {
                            show: false
                          },
                          axisLabel: {
                            show: false
                          },
                          pointer: {
                            icon: 'path://M2.9,0.7L2.9,0.7c1.4,0,2.6,1.2,2.6,2.6v115c0,1.4-1.2,2.6-2.6,2.6l0,0c-1.4,0-2.6-1.2-2.6-2.6V3.3C0.3,1.9,1.4,0.7,2.9,0.7z',
                            width: 2,
                            length: '60%',
                            offsetCenter: [0, '8%'],
                            itemStyle: {
                              color: '#35A29F',
                              shadowColor: 'rgba(0, 0, 0, 0.3)',
                              shadowBlur: 8,
                              shadowOffsetX: 2,
                              shadowOffsetY: 4
                            }
                          },
                          anchor: {
                            show: true,
                            size: 3,
                            showAbove: false,
                            itemStyle: {
                              borderWidth: 4,
                              borderColor: '#35A29F',
                              shadowColor: 'rgba(0, 0, 0, 0.3)',
                              shadowBlur: 8,
                              shadowOffsetX: 2,
                              shadowOffsetY: 4
                            }
                          },
                          detail: {
                            show: false
                          },
                          title: {
                            offsetCenter: ['0%', '-4%']
                          },
                          data: [
                            {
                              value: extractedBedData[1]
                            }
                          ]
                        }
                      ]
                    };

                    sleepClockOption && sleepClockChart.setOption(sleepClockOption);
                  }

                  
              }
      
              if ("wake_up_time" in data["data"]){
                  wakeWeeklyAverage.innerText = data["data"]["wake_up_time"]["average"]
                  wakeWeeklyLongest.innerText = data["data"]["wake_up_time"]["max"]
                  wakeWeeklyShortest.innerText = data["data"]["wake_up_time"]["min"]
                  wakeExWeeklyAverage.innerText = data["data"]["wake_up_time"]["previous_average"]

                  if (data["data"]["wake_up_time"]["average"] != "-"){
                    wakeClockDom.style.height = "30vh"
                    var wakeClockChart = echarts.init(wakeClockDom);
                    var wakeClockOption;

                    const extractedWakeData = extractHourAndMinute(data["data"]["wake_up_time"]["average"])
                    console.log(extractedWakeData)

                    wakeClockOption = {
                      series: [
                        {
                          name: 'hour',
                          type: 'gauge',
                          startAngle: 90,
                          endAngle: -270,
                          min: 0,
                          max: 12,
                          splitNumber: 12,
                          clockwise: true,
                          axisLine: {
                            lineStyle: {
                              width: 4,
                              color: [[1, '#071952']],
                            }
                          },
                          axisLabel: {
                            fontSize: 10,
                            distance: 5,
                            formatter: function (value) {
                              if (value === 0) {
                                return '';
                              }
                              return value + '';
                            }
                          },
                          pointer: {
                            icon: 'path://M2.9,0.7L2.9,0.7c1.4,0,2.6,1.2,2.6,2.6v115c0,1.4-1.2,2.6-2.6,2.6l0,0c-1.4,0-2.6-1.2-2.6-2.6V3.3C0.3,1.9,1.4,0.7,2.9,0.7z',
                            width: 4,
                            length: '40%',
                            offsetCenter: [0, '2%'],
                            itemStyle: {
                              color: '#088395',
                              shadowColor: 'rgba(0, 0, 0, 0.3)',
                              shadowBlur: 8,
                              shadowOffsetX: 2,
                              shadowOffsetY: 4
                            }
                          },
                          detail: {
                            show: false
                          },
                          data: [
                            {
                              value: extractedWakeData[0]
                            }
                          ]
                        },
                        {
                          name: 'minute',
                          type: 'gauge',
                          startAngle: 90,
                          endAngle: -270,
                          min: 0,
                          max: 60,
                          clockwise: true,
                          axisLine: {
                            show: false
                          },
                          splitLine: {
                            show: false
                          },
                          axisTick: {
                            show: false
                          },
                          axisLabel: {
                            show: false
                          },
                          pointer: {
                            icon: 'path://M2.9,0.7L2.9,0.7c1.4,0,2.6,1.2,2.6,2.6v115c0,1.4-1.2,2.6-2.6,2.6l0,0c-1.4,0-2.6-1.2-2.6-2.6V3.3C0.3,1.9,1.4,0.7,2.9,0.7z',
                            width: 2,
                            length: '60%',
                            offsetCenter: [0, '8%'],
                            itemStyle: {
                              color: '#35A29F',
                              shadowColor: 'rgba(0, 0, 0, 0.3)',
                              shadowBlur: 8,
                              shadowOffsetX: 2,
                              shadowOffsetY: 4
                            }
                          },
                          anchor: {
                            show: true,
                            size: 3,
                            showAbove: false,
                            itemStyle: {
                              borderWidth: 4,
                              borderColor: '#35A29F',
                              shadowColor: 'rgba(0, 0, 0, 0.3)',
                              shadowBlur: 8,
                              shadowOffsetX: 2,
                              shadowOffsetY: 4
                            }
                          },
                          detail: {
                            show: false
                          },
                          title: {
                            offsetCenter: ['0%', '-4%']
                          },
                          data: [
                            {
                              value: extractedWakeData[1]
                            }
                          ]
                        }
                      ]
                    };

                    wakeClockOption && wakeClockChart.setOption(wakeClockOption);
                  }
              }
      
              if ("time_in_bed" in data["data"]){
                  inbedWeeklyAverage.innerText = data["data"]["time_in_bed"]["average"]
                  inbedWeeklyLongest.innerText = data["data"]["time_in_bed"]["max"]
                  inbedWeeklyShortest.innerText = data["data"]["time_in_bed"]["min"]
                  inbedExWeeklyAverage.innerText = data["data"]["time_in_bed"]["previous_average"]

                  if (data["data"]["time_in_bed"]["average"] != "-"){
                    bedPieDom.style.height = "30vh"
                    var bedChart = echarts.init(bedPieDom);
                    var bedOption;
                    var bed_min = 0

                    bed_min = timeStringToMinutes(data["data"]["time_in_bed"]["average"])

                    bedOption = {
                      legend: {
                        orient: 'vertical',
                        right: '0%',     // Adjust the 'right' property to move it to the right
                        bottom: '10%'     // Adjust the 'bottom' property to move it to the bottom
                      },
                      dataset: [
                        {
                          source: [
                            { value: bed_min, name: 'On Bed' },
                            { value: (60*24)-bed_min, name: 'Not On Bed' }
                          ]
                        }
                      ],
                      series: [
                        {
                          type: 'pie',
                          radius: '70%',
                          center: ['50%', '50%'], // Center the pie chart both horizontally and vertically
                          label: {
                            position: 'inside',
                            formatter: '{d}%',
                            color: 'black',
                            fontSize: 10
                          },
                          percentPrecision: 0,
                          emphasis: {
                            label: { show: true },
                            itemStyle: {
                              shadowBlur: 10,
                              shadowOffsetX: 0,
                              shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                          },
                          // Set colors for each name (category)
                          data: [
                            {
                              value: bed_min,
                              name: 'On Bed',
                              itemStyle: { color: '#088395' } // Set the color for 'Sleeping'
                            },
                            {
                              value: (60 * 24) - bed_min,
                              name: 'Not On Bed',
                              itemStyle: { color: '#35A29F' } // Set the color for 'Not Sleeping'
                            }
                          ]
                        }
                      ]
                    };

                    bedOption && bedChart.setOption(bedOption);
                  }

              }
      
              if ("in_room" in data["data"]){
                  inroomWeeklyAverage.innerText = data["data"]["in_room"]["average"]
                  inroomWeeklyLongest.innerText = data["data"]["in_room"]["max"]
                  inroomWeeklyShortest.innerText = data["data"]["in_room"]["min"]
                  inroomExWeeklyAverage.innerText = data["data"]["in_room"]["previous_average"]

                  if (data["data"]["in_room"]["average"] != "-"){
                    roomPieDom.style.height = "30vh"
                    var roomChart = echarts.init(roomPieDom);
                    var roomOption;
                    var room_min = 0

                    room_min = timeStringToMinutes(data["data"]["in_room"]["average"])

                    roomOption = {
                      legend: {
                        orient: 'vertical',
                        right: '0%',     // Adjust the 'right' property to move it to the right
                        bottom: '10%'     // Adjust the 'bottom' property to move it to the bottom
                      },
                      dataset: [
                        {
                          source: [
                            { value: room_min, name: 'In Room' },
                            { value: (60*24)-room_min, name: 'Not In Room' }
                          ]
                        }
                      ],
                      series: [
                        {
                          type: 'pie',
                          radius: '70%',
                          center: ['50%', '50%'], // Center the pie chart both horizontally and vertically
                          label: {
                            position: 'inside',
                            formatter: '{d}%',
                            color: 'black',
                            fontSize: 10
                          },
                          percentPrecision: 0,
                          emphasis: {
                            label: { show: true },
                            itemStyle: {
                              shadowBlur: 10,
                              shadowOffsetX: 0,
                              shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                          },
                          // Set colors for each name (category)
                          data: [
                            {
                              value: room_min,
                              name: 'In Room',
                              itemStyle: { color: '#088395' } // Set the color for 'Sleeping'
                            },
                            {
                              value: (60 * 24) - room_min,
                              name: 'Not In Room',
                              itemStyle: { color: '#35A29F' } // Set the color for 'Not Sleeping'
                            }
                          ]
                        }
                      ]
                    };

                    roomOption && roomChart.setOption(roomOption);
                  }
              }
      
              if ("sleep_disruption" in data["data"]){
                  disruptionWeeklyAverage.innerText = data["data"]["sleep_disruption"]["average"]
                  disruptionWeeklyMost.innerText = data["data"]["sleep_disruption"]["max"]
                  disruptionWeeklyLeast.innerText = data["data"]["sleep_disruption"]["min"]
                  disruptionExWeeklyAverage.innerText = data["data"]["sleep_disruption"]["previous_average"]

                  if (data["data"]["sleep_disruption"]["average"] != "-"){
                    disruptionBarDom.style.height = "30vh"
                    var disruptionChart = echarts.init(disruptionBarDom);
                    var disruptionOption;

                    disruptionOption = {
                      xAxis: {                   // Use xAxis for horizontal bars
                        type: 'value'
                      },
                      yAxis: {                   // Use yAxis for categories
                        type: 'category',        // Specify the axis type as category
                        data: ['Min', 'Avg', 'Max']
                      },
                      series: [
                        {
                          data: [
                            {
                              value: data["data"]["sleep_disruption"]["min"],
                              itemStyle: {
                                color: barColors[0] // Set the color for the 'Min' bar
                              }
                            },
                            {
                              value: data["data"]["sleep_disruption"]["average"],
                              itemStyle: {
                                color: barColors[1] // Set the color for the 'Average' bar
                              }
                            },
                            {
                              value: data["data"]["sleep_disruption"]["max"],
                              itemStyle: {
                                color: barColors[2] // Set the color for the 'Max' bar
                              }
                            }
                          ],
                          type: 'bar',
                          showBackground: true,
                          backgroundStyle: {
                            color: 'rgba(180, 180, 180, 0.2)'
                          }
                        }
                      ]
                    };
                    
                    disruptionOption && disruptionChart.setOption(disruptionOption);
                  }
              }
      
              if ("breath_rate" in data["data"]){
                  breathWeeklyAverage.innerText = data["data"]["breath_rate"]["average"]
                  breathWeeklyHighest.innerText = data["data"]["breath_rate"]["max"]
                  breathWeeklyLowest.innerText = data["data"]["breath_rate"]["min"]
                  breathExWeeklyAverage.innerText = data["data"]["breath_rate"]["previous_average"]

                  if (data["data"]["breath_rate"]["average"] != "-"){
                    breathBarDom.style.height = "30vh"
                    var breathChart = echarts.init(breathBarDom);
                    var breathOption;

                    breathOption = {
                      xAxis: {                   // Use xAxis for horizontal bars
                        type: 'value'
                      },
                      yAxis: {                   // Use yAxis for categories
                        type: 'category',        // Specify the axis type as category
                        data: ['Min', 'Avg', 'Max']
                      },
                      series: [
                        {
                          data: [
                            {
                              value: data["data"]["breath_rate"]["min"],
                              itemStyle: {
                                color: barColors[0] // Set the color for the 'Min' bar
                              }
                            },
                            {
                              value: data["data"]["breath_rate"]["average"],
                              itemStyle: {
                                color: barColors[1] // Set the color for the 'Average' bar
                              }
                            },
                            {
                              value: data["data"]["breath_rate"]["max"],
                              itemStyle: {
                                color: barColors[2] // Set the color for the 'Max' bar
                              }
                            }
                          ],
                          type: 'bar',
                          showBackground: true,
                          backgroundStyle: {
                            color: 'rgba(180, 180, 180, 0.2)'
                          }
                        }
                      ]
                    };
                    
                    breathOption && breathChart.setOption(breathOption);
                  }
              }
      
              if ("heart_rate" in data["data"]){
                  heartWeeklyAverage.innerText = data["data"]["heart_rate"]["average"]
                  heartWeeklyHighest.innerText = data["data"]["heart_rate"]["max"]
                  heartWeeklyLowest.innerText = data["data"]["heart_rate"]["min"]
                  heartExWeeklyAverage.innerText = data["data"]["heart_rate"]["previous_average"]

                  if (data["data"]["heart_rate"]["average"] != "-"){
                    heartBarDom.style.height = "30vh"
                    var heartChart = echarts.init(heartBarDom);
                    var heartOption;

                    heartOption = {
                      xAxis: {                   // Use xAxis for horizontal bars
                        type: 'value'
                      },
                      yAxis: {                   // Use yAxis for categories
                        type: 'category',        // Specify the axis type as category
                        data: ['Min', 'Avg', 'Max']
                      },
                      series: [
                        {
                          data: [
                            {
                              value: data["data"]["heart_rate"]["min"],
                              itemStyle: {
                                color: barColors[0] // Set the color for the 'Min' bar
                              }
                            },
                            {
                              value: data["data"]["heart_rate"]["average"],
                              itemStyle: {
                                color: barColors[1] // Set the color for the 'Average' bar
                              }
                            },
                            {
                              value: data["data"]["heart_rate"]["max"],
                              itemStyle: {
                                color: barColors[2] // Set the color for the 'Max' bar
                              }
                            }
                          ],
                          type: 'bar',
                          showBackground: true,
                          backgroundStyle: {
                            color: 'rgba(180, 180, 180, 0.2)'
                          }
                        }
                      ]
                    };
                    
                    heartOption && heartChart.setOption(heartOption);
                  }
              }
          }
      })
}

dateInput.addEventListener("change", function () {
    setLaymanDetails()
});


setLaymanDetails()