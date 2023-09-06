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


const dateInput = document.getElementById("dateInput");

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
              }
      
              if ("bed_time" in data["data"]){
                  bedWeeklyAverage.innerText = data["data"]["bed_time"]["average"]
                  bedWeeklyLongest.innerText = data["data"]["bed_time"]["max"]
                  bedWeeklyShortest.innerText = data["data"]["bed_time"]["min"]
                  bedExWeeklyAverage.innerText = data["data"]["bed_time"]["previous_average"]
              }
      
              if ("wake_up_time" in data["data"]){
                  wakeWeeklyAverage.innerText = data["data"]["wake_up_time"]["average"]
                  wakeWeeklyLongest.innerText = data["data"]["wake_up_time"]["max"]
                  wakeWeeklyShortest.innerText = data["data"]["wake_up_time"]["min"]
                  wakeExWeeklyAverage.innerText = data["data"]["wake_up_time"]["previous_average"]
              }
      
              if ("time_in_bed" in data["data"]){
                  inbedWeeklyAverage.innerText = data["data"]["time_in_bed"]["average"]
                  inbedWeeklyLongest.innerText = data["data"]["time_in_bed"]["max"]
                  inbedWeeklyShortest.innerText = data["data"]["time_in_bed"]["min"]
                  inbedExWeeklyAverage.innerText = data["data"]["time_in_bed"]["previous_average"]
              }
      
              if ("in_room" in data["data"]){
                  inroomWeeklyAverage.innerText = data["data"]["in_room"]["average"]
                  inroomWeeklyLongest.innerText = data["data"]["in_room"]["max"]
                  inroomWeeklyShortest.innerText = data["data"]["in_room"]["min"]
                  inroomExWeeklyAverage.innerText = data["data"]["in_room"]["previous_average"]
              }
      
              if ("sleep_disruption" in data["data"]){
                  disruptionWeeklyAverage.innerText = data["data"]["sleep_disruption"]["average"]
                  disruptionWeeklyMost.innerText = data["data"]["sleep_disruption"]["max"]
                  disruptionWeeklyLeast.innerText = data["data"]["sleep_disruption"]["min"]
                  disruptionExWeeklyAverage.innerText = data["data"]["sleep_disruption"]["previous_average"]
              }
      
              if ("breath_rate" in data["data"]){
                  breathWeeklyAverage.innerText = data["data"]["breath_rate"]["average"]
                  breathWeeklyHighest.innerText = data["data"]["breath_rate"]["max"]
                  breathWeeklyLowest.innerText = data["data"]["breath_rate"]["min"]
                  breathExWeeklyAverage.innerText = data["data"]["breath_rate"]["previous_average"]
              }
      
              if ("heart_rate" in data["data"]){
                  heartWeeklyAverage.innerText = data["data"]["heart_rate"]["average"]
                  heartWeeklyHighest.innerText = data["data"]["heart_rate"]["max"]
                  heartWeeklyLowest.innerText = data["data"]["heart_rate"]["min"]
                  heartExWeeklyAverage.innerText = data["data"]["heart_rate"]["previous_average"]
              }
          }
      })
}

dateInput.addEventListener("change", function () {
    setLaymanDetails()
});


setLaymanDetails()