// status device

// save device
const saveDeviceUpdateButton = document.getElementById(
  "save-device-update-modal"
);
const saveDeviceDeleteButton = document.getElementById(
  "save-device-delete-modal"
);
const macAddress = document.getElementById("device-add-mac");
const timeSelect = document.getElementById("time-select");
const dateTimeRow = document.getElementById("date-time-row");
const dateRangePicker = document.getElementById("date-range-picker");
const addSaveDeviceSubmitBtn = document.getElementById(
  "add-device-save-data-submit-btn"
);
const updateSaveDeviceSubmitBtn = document.getElementById(
  "update-device-save-data-submit-btn"
);
const deleteSaveDeviceSubmitBtn = document.getElementById(
  "delete-device-save-data-submit-btn"
);
const macAddressAddError = document.getElementById("mac-address-error");
const timeSelectAddError = document.getElementById("time-select-error");
// Register Device
const registerDevAddMac = document.getElementById("register-device-add-mac");
const registerDevAddMacErr = document.getElementById(
  "register-mac-address-error"
);
const registerDevAddName = document.getElementById("register-device-add-name");
const registerDevAddNameErr = document.getElementById(
  "register-device-add-name-error"
);
const registerDevAddDesc = document.getElementById(
  "register-device-description"
);
const registerDevAddSubmitBtn = document.getElementById(
  "register-device-submit-btn"
);
const registerDeviceUpdateButton = document.getElementById(
  "register-device-update-modal"
);
// Update Register Device
const regDevUpdateMac = document.getElementById("register-device-update-mac");
const regDevUpdateMacErr = document.getElementById(
  "register-mac-address-update-error"
);
const regDevUpdateName = document.getElementById("register-device-update-name");
const regDevUpdateNameErr = document.getElementById(
  "register-device-update-name-error"
);
const regDevUpdateDesc = document.getElementById(
  "register-device-update-description"
);
const updateRegDevSubmitBtn = document.getElementById(
  "update-device-register-submit-btn"
);
// register tab
const regDevTab = document.getElementById("register-device-tab");
let option1 = document.createElement("option");
let option2 = document.createElement("option");
let option3 = document.createElement("option");
let option4 = document.createElement("option");
let option5 = document.createElement("option");

if(!checkLogin()){
  window.location.href = loginPage
}

// table
var table;

option1.value = "please select";
option1.innerText = "Please Select Date/Time";

option2.value = "day";
option2.innerText = "1 Day";

option3.value = "week";
option3.innerText = "1 Week";

option4.value = "month";
option4.innerText = "1 Month";

option5.value = "Custom";
option5.innerText = "Custom";

timeSelect.appendChild(option1);
timeSelect.appendChild(option2);
timeSelect.appendChild(option3);
timeSelect.appendChild(option4);
timeSelect.appendChild(option5);

fetch(`${host}/getStatusDevice`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(RequestData()),
})
  .then((response) => response.json())
  .then((data) => {
    // console.log(data);
    // console.timeEnd("timer1");
    // if(data["CODE"] == 0)
    // response = data["DATA"];
    response = data;
    if (data.DATA) {
      data.DATA.forEach((d) => {
        dateTime = String(d.TIMESTAMP);
        newRow = $(
          "<tr><td>" +
            d.NAME +
            "</td><td>" +
            d.MAC +
            "</td><td>" +
            d.STATUS +
            "</td><td>" +
            dateTime.substring(0, dateTime.length - 3) +
            "</td></tr>"
        );
        $("#status-device-table tbody").append(newRow);
      });
      $("#status-device-table").dataTable({
        order: [[3, "desc"]],
      });
    } else {
      $("#status-device-table").dataTable({
        order: [[3, "desc"]],
      });
    }
  })
  .catch((error) => {
    console.error("Error:", error);
  });

fetch(`${host}/getSaveDeviceRawData`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(RequestData()),
})
  .then((response) => response.json())
  .then((data) => {
    // console.log(data);
    // console.timeEnd("timer1");
    // if(data["CODE"] == 0)
    // response = data["DATA"];
    response = data;
    if (data.DATA) {
      data.DATA.forEach((d) => {
        start = String(d.Start);
        expired = String(d.Expired);
        newRow = $(
          "<tr><td>" +
            d.Id +
            "</td><td>" +
            d.MAC +
            "</td><td>" +
            start.substring(0, start.length - 3) +
            "</td><td>" +
            expired.substring(0, expired.length - 3) +
            "</td><td><button type='button' class='btn btn-info' data-bs-toggle='modal' data-bs-target='#save-device-update-modal' attr='update' data-bs-whatever=" +
            d.Id +
            ">Update</button>&nbsp;&nbsp;<button type='button' class='btn btn-danger' data-bs-toggle='modal' data-bs-target='#save-device-update-modal' attr='delete' data-bs-whatever=" +
            d.Id +
            ">Delete</button></td></tr>"
        );
        $("#save-device-table tbody").append(newRow);
      });
      $("#save-device-table").dataTable({
        order: [[0, "desc"]],
      });
    } else {
      $("#save-device-table").dataTable({
        order: [[0, "desc"]],
      });
    }
  })
  .catch((error) => {
    console.error("Error:", error);
  });

registerDeviceUpdateButton.addEventListener("show.bs.modal", async (event) => {
  // Button that triggered the modal
  const button = event.relatedTarget;
  // Extract info from data-bs-* attributes
  const deviceId = button.getAttribute("data-bs-whatever");
  const updateRegDevId = document.getElementById("update-register-device-id");
  const updateRegDevName = document.getElementById("update-register-name");
  const updateRegDevMac = document.getElementById("update-register-mac");
  const updateRegDevTime = document.getElementById(
    "update-register-device-last-modified-time"
  );
  const regAttr = button.getAttribute("attr");
  const updateRegDevForm = document.getElementById(
    "update-register-device-form"
  );
  const updateRegDevModalTitle = document.getElementById(
    "register-device-update-modalLabel"
  );
  Rdata = {
    Id: deviceId,
  };
  Object.assign(Rdata, RequestData())
  await fetch(`${host}/getRegDevice`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(Rdata),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      // if(data["CODE"] == 0)
      // response = data["DATA"];
      response = data;
      if (data.DATA) {
        data.DATA.forEach((d) => {
          start = String(d["LAST MODIFIED TIME"]);
          updateRegDevId.innerHTML = `ID: <strong>${d.Id}</strong>`;
          updateRegDevTime.innerHTML = `Last Modified Time: <strong>${start.substring(
            0,
            start.length - 3
          )}</strong>`;
          updateRegDevSubmitBtn.setAttribute("Id", d.Id);
          if (regAttr == "delete") {
            updateRegDevSubmitBtn.classList.remove("btn-primary");
            updateRegDevSubmitBtn.classList.add("btn-danger");
            updateRegDevSubmitBtn.innerHTML = "Delete";
            updateRegDevForm.style.display = "none";
            updateRegDevSubmitBtn.removeAttribute("onclick");
            updateRegDevMac.innerHTML = `MAC Address: <strong>${d.MAC}</strong>`;
            updateRegDevName.innerHTML = `Device Name: <strong>${d.NAME}</strong>`;
            updateRegDevSubmitBtn.setAttribute(
              "onclick",
              "deleteDeviceDetail()"
            );
            updateRegDevModalTitle.innerHTML = "Delete Register Device Detail";
          } else {
            regDevUpdateMac.value = d.MAC;
            regDevUpdateName.value = d.NAME;
            regDevUpdateDesc.value = d.DESCRIPTION;
            updateRegDevSubmitBtn.classList.remove("btn-danger");
            updateRegDevSubmitBtn.classList.add("btn-primary");
            updateRegDevSubmitBtn.innerHTML = "Update";
            updateRegDevForm.style.display = "";
            updateRegDevSubmitBtn.removeAttribute("onclick");
            updateRegDevMac.innerText = "";
            updateRegDevName.innerText = "";
            updateRegDevSubmitBtn.setAttribute(
              "onclick",
              "updateDeviceDetail()"
            );
            updateRegDevModalTitle.innerHTML = "Update Register Device Detail";
          }
        });
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
});

saveDeviceUpdateButton.addEventListener("show.bs.modal", async (event) => {
  // Button that triggered the modal
  const button = event.relatedTarget;
  // Extract info from data-bs-* attributes
  const deviceId = button.getAttribute("data-bs-whatever");
  const updateDeviceIdInModal = document.getElementById(
    "update-save-device-id"
  );
  const updateDeviceStartInModal = document.getElementById(
    "update-save-device-start"
  );
  const updateDeviceEndInModal = document.getElementById(
    "update-save-device-end"
  );
  const checkAttr = button.getAttribute("attr");
  const updateSaveDeviceForm = document.getElementById(
    "update-save-device-form"
  );
  const updateSaveDeviceModalTile = document.getElementById(
    "save-device-update-modalLabel"
  );
  // If necessary, you could initiate an AJAX request here
  Rdata = {
    Id: deviceId,
  };
  Object.assign(Rdata, RequestData())
  await fetch(`${host}/getSaveDevice`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(Rdata),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      // if(data["CODE"] == 0)
      // response = data["DATA"];
      response = data;
      if (data.DATA) {
        data.DATA.forEach((d) => {
          start = String(d.Start);
          end = String(d.Expired);
          updateDeviceIdInModal.innerHTML = `ID: <strong>${d.Id}</strong>`;
          updateDeviceStartInModal.innerHTML = `Start Date: <strong>${start.substring(
            0,
            start.length - 3
          )}</strong>`;
          updateDeviceEndInModal.innerHTML = `Expired Date: <strong>${end.substring(
            0,
            end.length - 3
          )}</strong>`;
          document.querySelector("#update-save-device-mac").value = d.MAC;
          updateSaveDeviceSubmitBtn.setAttribute("Id", d.Id);
          if (checkAttr == "delete") {
            updateSaveDeviceSubmitBtn.classList.remove("btn-primary");
            updateSaveDeviceSubmitBtn.classList.add("btn-danger");
            updateSaveDeviceSubmitBtn.innerHTML = "Delete";
            updateSaveDeviceForm.style.display = "none";
            updateSaveDeviceSubmitBtn.removeAttribute("onclick");
            updateSaveDeviceSubmitBtn.setAttribute(
              "onclick",
              "deleteDeviceSaveData()"
            );
            updateSaveDeviceModalTile.innerHTML = "Delete Save Device List";
          } else {
            updateSaveDeviceSubmitBtn.classList.remove("btn-danger");
            updateSaveDeviceSubmitBtn.classList.add("btn-primary");
            updateSaveDeviceSubmitBtn.innerHTML = "Update";
            updateSaveDeviceForm.style.display = "";
            updateSaveDeviceSubmitBtn.removeAttribute("onclick");
            updateSaveDeviceSubmitBtn.setAttribute(
              "onclick",
              "updateDeviceSaveData()"
            );
            updateSaveDeviceModalTile.innerHTML =
              "Update Save Device Data List Time";
          }
        });
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
});

regDevTab.addEventListener("click", async (e) => {
  // console.log('register tab clicked')
  if (!table) {
    await fetch(`${host}/getRegDevices`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(RequestData())
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        if (data.DATA) {
          data.DATA.forEach((d) => {
            time = String(d["LAST MODIFIED TIME"]);
            newRow = $(
              "<tr><td>" +
                d.Id +
                "</td><td>" +
                d.MAC +
                "</td><td>" +
                d.NAME +
                "</td><td>" +
                time.substring(0, time.length - 3) +
                "</td><td>" +
                d.DESCRIPTION +
                "</td><td><button type='button' class='btn btn-info' data-bs-toggle='modal' data-bs-target='#register-device-update-modal' attr='update' data-bs-whatever=" +
                d.Id +
                ">Update</button>&nbsp;&nbsp;<button type='button' class='btn btn-danger' data-bs-toggle='modal' data-bs-target='#register-device-update-modal' attr='delete' data-bs-whatever=" +
                d.Id +
                ">Delete</button></td></tr>"
            );
            $("#register-device-table tbody").append(newRow);
          });
          table = $("#register-device-table").dataTable({
            order: [[0, "desc"]],
          });
        } else {
          $("#register-device-table").dataTable({
            order: [[0, "desc"]],
          });
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }
});

async function updateDeviceDetail() {
  updateRegDevSubmitBtn.disabled = true;
  regDevUpdateMacErr.innerText = "";
  regDevUpdateMac.style.border = borderOri;
  regDevUpdateNameErr.innerText = "";
  regDevUpdateName.style.border = borderOri;
  RData = {
    Id: updateRegDevSubmitBtn.getAttribute("Id"),
    MAC: regDevUpdateMac.value,
    NAME: regDevUpdateName.value,
    DESCRIPTION: regDevUpdateDesc.value,
  };
  Object.assign(RData, RequestData())
  if (regDevUpdateMac.value != "" || regDevUpdateName.value != "") {
    console.log(RData);
    await fetch(`${host}/updateDevice`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(RData),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        response = data;
        if (data.DATA) {
          updateRegDevSubmitBtn.disabled = false;
          document.querySelector(".btn-close").click();
          location.reload();
        } else if (data.ERROR) {
          updateRegDevSubmitBtn.disabled = false;
          console.log(data.ERROR);
          if ("NAME" in data.ERROR[0]) {
            regDevUpdateNameErr.innerText = data.ERROR[0].NAME;
            regDevUpdateName.style.border = borderRed;
          } else {
            regDevUpdateMac.style.border = borderRed;
            regDevUpdateMacErr.innerText = data.ERROR[0].MAC;
          }
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        updateRegDevSubmitBtn.disabled = false;
      });
  } else {
    regDevUpdateMacErr.innerText = "MAC is Empty!";
    regDevUpdateMac.style.border = borderRed;
    regDevUpdateNameErr.innerText = "NAME is Empty!";
    regDevUpdateName.style.border = borderRed;
    updateRegDevSubmitBtn.disabled = false;
  }
}

async function deleteDeviceDetail() {
  updateRegDevSubmitBtn.disabled = true;
  RData = {
    Id: updateRegDevSubmitBtn.getAttribute("Id"),
  };
  console.log(RData);
  Object.assign(RData, RequestData())
  await fetch(`${host}/deleteDevice`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(RData),
  })
    .then((response) => response.json())
    .then((data) => {
      // console.log(data);
      if (data["CODE"] == 0) {
        updateRegDevSubmitBtn.disabled = false;
        document.querySelector(".btn-close").click();
        location.reload();
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      updateRegDevSubmitBtn.disabled = false;
    });
}

async function deleteDeviceSaveData() {
  updateSaveDeviceSubmitBtn.disabled = true;
  RData = {
    Id: updateSaveDeviceSubmitBtn.getAttribute("Id"),
  };
  Object.assign(RData, RequestData())
  console.log(RData);
  await fetch(`${host}/deleteSaveDeviceTime`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(RData),
  })
    .then((response) => response.json())
    .then((data) => {
      // console.log(data);
      if (data["CODE"] == 0) {
        updateSaveDeviceSubmitBtn.disabled = false;
        document.querySelector(".btn-close").click();
        location.reload();
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      updateSaveDeviceSubmitBtn.disabled = false;
    });
}

async function updateDeviceSaveData() {
  updateSaveDeviceSubmitBtn.disabled = true;
  RData = {
    Id: updateSaveDeviceSubmitBtn.getAttribute("Id"),
    MAC: document.querySelector("#update-save-device-mac").value,
    TIME: document.querySelector("#update-device-save-date-time").value,
  };
  Object.assign(RData, RequestData())
  console.log(RData);
  await fetch(`${host}/updateSaveDeviceTime`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(RData),
  })
    .then((response) => response.json())
    .then((data) => {
      // console.log(data);
      if (data["CODE"] == 0) {
        updateSaveDeviceSubmitBtn.disabled = false;
        document.querySelector(".btn-close").click();
        location.reload();
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      updateSaveDeviceSubmitBtn.disabled = false;
    });
}

async function getSelectedData() {
  addSaveDeviceSubmitBtn.disabled = true;
  timeSelect.style.border = borderOri;
  macAddress.style.border = borderOri;
  macAddressAddError.innerText = "";
  timeSelectAddError.innerText = "";
  let response = [];
  let Rdata = {};
  if (timeSelect.value == "Custom")
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
  Object.assign(Rdata, RequestData())
  if (macAddress.value != "" || timeSelect.value != "please select") {
    // console.log(Rdata);
    await fetch(`${host}/saveDevice`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(Rdata),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        response = data;
        if (data.DATA) {
          addSaveDeviceSubmitBtn.disabled = false;
          document.querySelector(".btn-close").click();
          location.reload();
        } else if (data.ERROR) {
          addSaveDeviceSubmitBtn.disabled = false;
          console.log(data.ERROR);
          if ("TIME" in data.ERROR[0]) {
            timeSelectAddError.innerText = "Please select Time!";
            timeSelect.style.border = borderRed;
          } else {
            macAddress.style.border = borderRed;
            macAddressAddError.innerText = data.ERROR[0].MAC;
          }
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        addSaveDeviceSubmitBtn.disabled = false;
      });
  } else {
    timeSelect.style.border = borderRed;
    macAddress.style.border = borderRed;
    macAddressAddError.innerText = "MAC address is Empty!";
    timeSelectAddError.innerText = "Please select Time!";
    addSaveDeviceSubmitBtn.disabled = false;
  }
}

async function addNewDevice() {
  registerDevAddSubmitBtn.disabled = true;
  registerDevAddMac.style.border = borderOri;
  registerDevAddName.style.border = borderOri;
  registerDevAddMacErr.innerText = "";
  registerDevAddNameErr.innerText = "";
  let Rdata = {};
  Rdata = {
    MAC: registerDevAddMac.value,
    NAME: registerDevAddName.value,
    DESCRIPTION: registerDevAddDesc.value,
  };
  Object.assign(Rdata, RequestData())
  if (registerDevAddMac.value != "" || registerDevAddName.value != "") {
    console.log(Rdata);
    await fetch(`${host}/addNewDevice`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(Rdata),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        response = data;
        if (data.DATA) {
          registerDevAddSubmitBtn.disabled = false;
          document.querySelector(".btn-close").click();
          location.reload();
        } else if (data.ERROR) {
          registerDevAddSubmitBtn.disabled = false;
          console.log(data.ERROR);
          if ("NAME" in data.ERROR[0]) {
            registerDevAddNameErr.innerText = data.ERROR[0].NAME;
            registerDevAddName.style.border = borderRed;
          } else {
            registerDevAddMac.style.border = borderRed;
            registerDevAddMacErr.innerText = data.ERROR[0].MAC;
          }
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        registerDevAddSubmitBtn.disabled = false;
      });
  } else {
    registerDevAddMac.style.border = borderRed;
    registerDevAddName.style.border = borderRed;
    registerDevAddMacErr.innerText = "MAC address is Empty!";
    registerDevAddNameErr.innerText = "Name is Empty!";
    registerDevAddSubmitBtn.disabled = false;
  }
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

$(function () {
  $('input[name="upateDevicedatetimes"]').daterangepicker({
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

timeSelect.addEventListener("change", (e) => {
  if (e.target.value == "Custom") {
    dateTimeRow.style.display = "";
  } else {
    dateTimeRow.style.display = "none";
  }
});
