const macAddress = document.getElementById("device-mac")
const timeSelect = document.getElementById("time-select")
const dateTimeRow = document.getElementById("date-time-row")
const dateRangePicker = document.getElementById("date-range-picker")

async function getSelectedData() {
  let response = [];
  let Rdata = {};
  if(timeSelect.value == "Custom")
    Rdata = {
      CUSTOM: 1,
      TIME: dateRangePicker.value,
      DEVICEMAC: macAddress.value,
    };
  else
    Rdata = {
      CUSTOM: 0,
      TIME: timeSelect.value,
      DEVICEMAC: macAddress.value,
    };
  console.log(Rdata)
  console.time("timer1")
  await fetch(`${host}/getData`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(Rdata),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data)
      console.timeEnd("timer1")
      // if(data["CODE"] == 0)
      // response = data["DATA"];
      response = data;
    })
    .catch((error) => {
      console.error("Error:", error);
    });
  // console.log(response);
  return response;
}

// new DateTimePickerComponent.DateTimeRangePicker('start', 'end');
$(function() {
  $('input[name="datetimes"]').daterangepicker({
    timePicker: true,
    showDropdowns: true,
    minYear: 1901,
    maxYear: parseInt(moment().format('YYYY'),10),
    startDate: moment().startOf('hour'),
    endDate: moment().startOf('hour').add(32, 'hour'),
    // timePicker24Hour: true, 
    locale: {
      format: 'YYYY/M/DD H:mm:ss'
    }
  });
});

timeSelect.addEventListener("change", e => {
  if(e.target.value == "Custom"){
    dateTimeRow.style.display = ""
  } else {
    dateTimeRow.style.display = "none"
  }
})