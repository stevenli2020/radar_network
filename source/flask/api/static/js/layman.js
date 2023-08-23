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

roomI = window.location.href.split("=")[1];

const historicalButton = document.getElementById("historical-button")
historicalButton.addEventListener("click", function () {
  window.location.href=`${host}/Detail?room=${roomI}`
});

roomD = {
  room_id: roomI,
};

Object.assign(roomD, RequestData());
fetch(`${host}/api/getRoomLaymanDetail`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(roomD),
}).then((response) => response.json()).then((data) => {
    if ("data" in data){
        if ("room_name" in data["data"] && data["data"]["room_name"]){
            roomName.innerText = data["data"]["room_name"]
        }
        if ("sleeping_hour" in data["data"]){
            sleepingWeeklyAverage.innerText = data["data"]["sleeping_hour"]["average"]
            sleepingWeeklyLongest.innerText = data["data"]["sleeping_hour"]["longest"]
            sleepingWeeklyShortest.innerText = data["data"]["sleeping_hour"]["shortest"]
            sleepingExWeeklyAverage.innerText = data["data"]["sleeping_hour"]["previous_average"]
        }

        if ("bed_time" in data["data"]){
            bedWeeklyAverage.innerText = data["data"]["bed_time"]["average"]
            bedWeeklyLongest.innerText = data["data"]["bed_time"]["latest"]
            bedWeeklyShortest.innerText = data["data"]["bed_time"]["earliest"]
            bedExWeeklyAverage.innerText = data["data"]["bed_time"]["previous_average"]
        }

        if ("wake_up_time" in data["data"]){
            wakeWeeklyAverage.innerText = data["data"]["wake_up_time"]["average"]
            wakeWeeklyLongest.innerText = data["data"]["wake_up_time"]["latest"]
            wakeWeeklyShortest.innerText = data["data"]["wake_up_time"]["earliest"]
            wakeExWeeklyAverage.innerText = data["data"]["wake_up_time"]["previous_average"]
        }

        if ("time_in_bed" in data["data"]){
            inbedWeeklyAverage.innerText = data["data"]["time_in_bed"]["average"]
            inbedWeeklyLongest.innerText = data["data"]["time_in_bed"]["longest"]
            inbedWeeklyShortest.innerText = data["data"]["time_in_bed"]["shortest"]
            inbedExWeeklyAverage.innerText = data["data"]["time_in_bed"]["previous_average"]
        }

        if ("in_room" in data["data"]){
            inroomWeeklyAverage.innerText = data["data"]["in_room"]["average"]
            inroomWeeklyLongest.innerText = data["data"]["in_room"]["longest"]
            inroomWeeklyShortest.innerText = data["data"]["in_room"]["shortest"]
            inroomExWeeklyAverage.innerText = data["data"]["in_room"]["previous_average"]
        }

        if ("sleep_disruption" in data["data"]){
            disruptionWeeklyAverage.innerText = data["data"]["sleep_disruption"]["average"]
            disruptionWeeklyMost.innerText = data["data"]["sleep_disruption"]["most"]
            disruptionWeeklyLeast.innerText = data["data"]["sleep_disruption"]["least"]
            disruptionExWeeklyAverage.innerText = data["data"]["sleep_disruption"]["previous_average"]
        }

        if ("breath_rate" in data["data"]){
            breathWeeklyAverage.innerText = data["data"]["breath_rate"]["average"]
            breathWeeklyHighest.innerText = data["data"]["breath_rate"]["highest"]
            breathWeeklyLowest.innerText = data["data"]["breath_rate"]["lowest"]
            breathExWeeklyAverage.innerText = data["data"]["breath_rate"]["previous_average"]
        }

        if ("heart_rate" in data["data"]){
            heartWeeklyAverage.innerText = data["data"]["heart_rate"]["average"]
            heartWeeklyHighest.innerText = data["data"]["heart_rate"]["highest"]
            heartWeeklyLowest.innerText = data["data"]["heart_rate"]["lowest"]
            heartExWeeklyAverage.innerText = data["data"]["heart_rate"]["previous_average"]
        }
    }
})



