// Register Device
const registerDevAddMac = document.getElementById("register-device-add-mac");
const registerDevAddMacErr = document.getElementById(
  "register-mac-address-error"
);
const registerDevAddPassword = document.getElementById("register-device-password");
const registerDevAddPasswordErr = document.getElementById(
  "register-device-password-error"
);
const registerDevAddName = document.getElementById("register-device-add-name");
const registerDevAddNameErr = document.getElementById(
  "register-device-add-name-error"
);
const registerDevAddPosX = document.getElementById("register-device-add-pos-x");
const registerDevAddPosXErr = document.getElementById("register-device-add-pos-x-error");
const registerDevAddPosY = document.getElementById("register-device-add-pos-y");
const registerDevAddPosYErr = document.getElementById(
  "register-device-add-pos-y-error"
);
const registerDevAddPosZ = document.getElementById("register-device-add-pos-z");
const registerDevAddPosZErr = document.getElementById(
  "register-device-add-pos-z-error"
);
const registerDevAddRotX = document.getElementById("register-device-add-rot-x");
const registerDevAddRotXErr = document.getElementById("register-device-add-rot-x-error");
const registerDevAddRotY = document.getElementById("register-device-add-rot-y");
const registerDevAddRotYErr = document.getElementById(
  "register-device-add-rot-y-error"
);
const registerDevAddRotZ = document.getElementById("register-device-add-rot-z");
const registerDevAddRotZErr = document.getElementById(
  "register-device-add-rot-z-error"
);
const registerDevAddLoc = document.getElementById(
  "register-device-add-location"
);
const registerDevAddLocSugg = document.getElementById(
  "register-device-add-location-sugg"
);
const registerDevAddLocErr = document.getElementById(
  "register-device-add-location-error"
);
const registerDevAddType = document.getElementById(
  "register-device-add-type"
);
const registerDevAddTypeErr = document.getElementById(
  "register-device-add-type-error"
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
const regDevUpdatePosX = document.getElementById("register-device-update-pos-x");
const regDevUpdatePosXErr = document.getElementById(
  "register-device-update-pos-x-error"
);
const regDevUpdatePosY = document.getElementById("register-device-update-pos-y");
const regDevUpdatePosYErr = document.getElementById(
  "register-device-update-pos-y-error"
);
const regDevUpdatePosZ = document.getElementById("register-device-update-pos-z");
const regDevUpdatePosZErr = document.getElementById(
  "register-device-update-pos-z-error"
);
const regDevUpdateRotX = document.getElementById("register-device-update-rot-x");
const regDevUpdateRotXErr = document.getElementById(
  "register-device-update-rot-x-error"
);
const regDevUpdateRotY = document.getElementById("register-device-update-rot-y");
const regDevUpdateRotYErr = document.getElementById(
  "register-device-update-rot-y-error"
);
const regDevUpdateRotZ = document.getElementById("register-device-update-rot-z");
const regDevUpdateRotZErr = document.getElementById(
  "register-device-update-rot-z-error"
);
const regDevUpdateLoc = document.getElementById(
  "register-device-update-location"
);
const regDevUpdateLocSugg = document.getElementById(
  "register-device-update-location-sugg"
);
const regDevUpdateType = document.getElementById(
  "register-device-update-type"
);
const regDevUpdateTypeErr = document.getElementById(
  "register-device-update-type-error"
);
const regDevUpdateLocErr = document.getElementById(
  "register-device-update-location-error"
);
const regDevUpdateDesc = document.getElementById(
  "register-device-update-description"
);
const regDevUpdateDescLabel = document.getElementById(
  "register-device-description-label"
);
const updateRegDevSubmitBtn = document.getElementById(
  "update-device-register-submit-btn"
);
// form-row
const devPosRow = document.getElementById('register-device-position-row')
const devRotRow = document.getElementById('register-device-rotation-row')
const devLocTypeRow = document.getElementById('register-device-loc-type-row')
// register tab
const regDevTab = document.getElementById("register-device-tab");
let option1 = document.createElement("option");
let option2 = document.createElement("option");
let option3 = document.createElement("option");
let option4 = document.createElement("option");
let option5 = document.createElement("option");
// table
const devicesTalbeId = document.getElementById("register-device-table")
var screenWidth = screen.width;
var client;
var reconnectTimeout = 2000;
var Mhost = "143.198.199.16";
var port = 8888;
var prevLe = 0;
var msgInterval = 0;
let userData = RequestData()
client = new Paho.MQTT.Client(Mhost, port, userData.ID);
var options = {
  timeout: 3,
  onSuccess: onConnect,
  onFailure: doFail,
  userName: userData.Username,
  password: "c764eb2b5fa2d259dc667e2b9e195218",
  // useSSL: true
};
client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;
client.connect(options);



function onConnect() {
  // Once a connection has been made, make a subscription and send a message.
  console.log("onConnect");
  client.subscribe("/GMT/#");  
};
function onConnectionLost(responseObject) {
  if (responseObject.errorCode !== 0)
	console.log("onConnectionLost:"+responseObject.errorMessage);
};
function onMessageArrived(message) {
  // console.log("topic: "+message.destinationName+"\nMessage: "+message.payloadString);
  // client.disconnect();
  if(message.destinationName.includes("DECODE_PUBLISH/R")){
    if(!message.payloadString.includes("CONNECTED")){
      document.querySelector("#popupMessageCloseBtn").click()
      popupMessageTitle.innerHTML = "Process Status"
      popupMessageBody.innerHTML = `<p><strong>${message.payloadString}</strong></p>`
      document.querySelector("#popupMessageOpenBtn").click()
      setTimeout(()=>{
        document.querySelector("#popupMessageCloseBtn").click()
      }, 2000)
    }    
  }
  if(getCookie('deviceConfMac')){
    console.log(getCookie('deviceConfMac'))
    if(message.destinationName.includes(`GMT/DEV/${getCookie('deviceConfMac')}/R`)){
      document.querySelector("#popupMessageCloseBtn").click()
      popupMessageTitle.innerHTML = "Process Status"
      popupMessageBody.innerHTML = `<p><strong>${message.payloadString}</strong></p>`
      document.querySelector("#popupMessageOpenBtn").click()
      setTimeout(()=>{
        document.querySelector("#popupMessageCloseBtn").click()
      }, 2000)
    }
  }
  
};
function doFail(e) {
  console.log(e);
}

if (!checkLogin()) {
  window.location.href = loginPage;
}

// table
var table;

function fetchRegDevices() {
  showLoading();

  fetch(`${host}/getRegDevices`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(RequestData()),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      if (data.DATA) {
        if ($.fn.DataTable.isDataTable('#register-device-table')) {
          $('#register-device-table').DataTable().destroy();
        }

        $('#register-device-table thead').remove();
        $('#register-device-table tbody').remove();

        let tHead = document.createElement('thead');
        let tBody = document.createElement('tbody');

        // Determine the table headers based on screen width
        let tableHeaders = getTableHeaders(); // Define this function

        // Add the table headers to the thead element
        tHead.innerHTML = `<tr>${tableHeaders.join('')}</tr>`;
        devicesTalbeId.appendChild(tHead);
        devicesTalbeId.appendChild(tBody);
        devicesTalbeId.style.fontSize = "small";

        // Clear the existing data in the table body
        $("#register-device-table tbody").empty();

        data.DATA.forEach((d) => {
          // Populate table rows based on screen width
          let tableRow = getTableRow(d); // Define this function
          $("#register-device-table tbody").append(tableRow);
        });

        // Reinitialize the DataTable
        table = $("#register-device-table").dataTable({
          order: [[0, "desc"]],
        });
      } else {
        if ($.fn.DataTable.isDataTable('#register-device-table')) {
          $('#register-device-table').DataTable().destroy();
        }
        // Reinitialize the DataTable without data
        $("#register-device-table").dataTable({
          order: [[0, "desc"]],
        });
      }
      hideLoading();
    })
    .catch((error) => {
      hideLoading();
      showToast("Error: " + String(error), false);
      console.error("Error:", error);
    });
}

// Function to determine table headers based on screen width
function getTableHeaders() {
  if (screenWidth <= 415) {
    return [
      "<th>Id</th>",
      "<th>Name</th>",
      "<th>Type</th>",
      "<th>Status</th>",
      "<th>Option</th>",
    ];
  } else if (screenWidth <= 821) {
    return [
      "<th>Id</th>",
      "<th>Name</th>",
      "<th>Location</th>",
      "<th>Type</th>",
      "<th>Status</th>",
      "<th>Position(X,Y,Z)</th>",
      "<th>Rotation(X,Y,Z)</th>",
      "<th>Option</th>",
    ];
  } else {
    return [
      "<th>Id</th>",
      "<th>MAC</th>",
      "<th>Name</th>",
      "<th>Location</th>",
      "<th>Type</th>",
      "<th>Status</th>",
      "<th>Position(X,Y,Z)</th>",
      "<th>Rotation(X,Y,Z)</th>",
      "<th>Last Modified</th>",
      "<th>Description</th>",
      "<th>Option</th>",
    ];
  }
}

// Function to create a table row based on screen width
function getTableRow(data) {
  // Customize table row content based on screen width
  if (screenWidth <= 415) {
    return $(
      "<tr><td id='wrap-text-table-phone'>" +
      data.Id +
      "</td><td id='wrap-text-table-10'>" +
      data.NAME +
      "</td><td id='wrap-text-table-phone'>" +
      getDeviceType(data.TYPE) +
      "</td><td id='wrap-text-table-phone'>" +
      getStatusIcon(data.STATUS) +
      "</td><td id='wrap-text-table-10'><i style='color: green;' class='tooltipcss bi bi-pencil-square' data-bs-toggle='modal' data-bs-target='#register-device-update-modal' attr='update' data-bs-whatever=" +
      data.Id +
      "><span class='tooltiptextcss'>Update</span></i>&nbsp;&nbsp;<i style='color: red;' class='bi bi-trash3 tooltipcss' class='btn btn-danger' data-bs-toggle='modal' data-bs-target='#register-device-update-modal' attr='delete' data-bs-whatever=" +
      data.Id +
      "><span class='tooltiptextcss'>Delete</span></i>&nbsp;&nbsp;<i style='color: blue;' class='bi bi-send tooltipcss' data-bs-toggle='modal' data-bs-target='#register-device-update-modal' attr='configuration' data-bs-whatever=" +
      data.Id +
      "><span class='tooltiptextcss'>Configuration</span></i></td></tr>"
    );
  } else if (screenWidth <= 821) {
    return $(
      "<tr><td>" +
      data.Id +
      "</td><td style='word-break: break-word;'>" +
      data.NAME +
      "</td><td style='word-break: break-word;'>" +
      data.ROOM_NAME +
      "</td><td style='word-break: break-word;'>" +
      getDeviceType(data.TYPE) +
      "</td><td style='word-break: break-word;'>" +
      getStatusIcon(data.STATUS) +
      "</td style='word-break: break-word;'>><td>" +
      data.DEPLOY_X +
      ", " +
      data.DEPLOY_Y +
      ", " +
      data.DEPLOY_Z +
      "</td style='word-break: break-word;'>><td>" +
      data.ROT_X +
      ", " +
      data.ROT_Y +
      ", " +
      data.ROT_Z +
      "</td><td><i style='color: green;' class='tooltipcss bi bi-pencil-square' data-bs-toggle='modal' data-bs-target='#register-device-update-modal' attr='update' data-bs-whatever=" +
      data.Id +
      "><span class='tooltiptextcss'>Update</span></i>&nbsp;&nbsp;<i style='color: red;' class='bi bi-trash3 tooltipcss' class='btn btn-danger' data-bs-toggle='modal' data-bs-target='#register-device-update-modal' attr='delete' data-bs-whatever=" +
      data.Id +
      "><span class='tooltiptextcss'>Delete</span></i>&nbsp;&nbsp;<i style='color: blue;' class='bi bi-send tooltipcss' data-bs-toggle='modal' data-bs-target='#register-device-update-modal' attr='configuration' data-bs-whatever=" +
      data.Id +
      "><span class'tooltiptextcss'>Configuration</span></i></td></tr>"
    );
  } else {
    return $(
      "<tr><td>" +
      data.Id +
      "</td><td>" +
      data.MAC +
      "</td><td>" +
      data.NAME +
      "</td><td>" +
      data.ROOM_NAME +
      "</td><td>" +
      getDeviceType(data.TYPE) +
      "</td><td>" +
      getStatusIcon(data.STATUS) +
      "</td><td>" +
      data.DEPLOY_X +
      ", " +
      data.DEPLOY_Y +
      ", " +
      data.DEPLOY_Z +
      "</td><td>" +
      data.ROT_X +
      ", " +
      data.ROT_Y +
      ", " +
      data.ROT_Z +
      "</td><td>" +
      getLocalTime(data["LAST DATA"]) +
      "</td><td>" +
      data.DESCRIPTION +
      "</td><td><i style='color: green;' class='tooltipcss bi bi-pencil-square' data-bs-toggle='modal' data-bs-target='#register-device-update-modal' attr='update' data-bs-whatever=" +
      data.Id +
      "><span class='tooltiptextcss'>Update</span></i>&nbsp;&nbsp;<i style='color: red;' class='bi bi-trash3 tooltipcss' class='btn btn-danger' data-bs-toggle='modal' data-bs-target='#register-device-update-modal' attr='delete' data-bs-whatever=" +
      data.Id +
      "><span class='tooltiptextcss'>Delete</span></i>&nbsp;&nbsp;<i style='color: blue;' class='bi bi-send tooltipcss' data-bs-toggle='modal' data-bs-target='#register-device-update-modal' attr='configuration' data-bs-whatever=" +
      data.Id +
      "><span class='tooltiptextcss'>Configuration</span></i></td></tr>"
    );
  }
}

// Function to get device type based on a provided code
function getDeviceType(code) {
  if (code === wallType) {
    return "Wall";
  } else if (code === ceilType) {
    return "Ceil";
  } else if (code === vitalType) {
    return "Vital";
  } else {
    return null;
  }
}

// Function to get status icon based on status
function getStatusIcon(status) {
  if (status === "DISCONNECTED") {
    return "<i style='color: red;' class='tooltipcss bi bi-cloud-slash-fill'><span class='tooltiptextcss'>Disconnected</span></i>";
  } else {
    return "<i style='color: green;' class='tooltipcss bi bi-cloud-fill'><span class='tooltiptextcss'>Connected</span></i>";
  }
}

// Function to get local time from a UTC time string
function getLocalTime(utcTime) {
  if (utcTime !== null) {
    let localTime = new Date(utcTime);
    let localTimeString = getTimezoneOffset(utcTime);
    localTimeString = moment(localTimeString).fromNow();
    return localTimeString;
  } else {
    return '-';
  }
}

fetchRegDevices()

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
  Object.assign(Rdata, RequestData());
  showLoading()
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
          updateRegDevSubmitBtn.setAttribute("mac", d.MAC);
          updateRegDevSubmitBtn.setAttribute("dev-name", d.NAME);
          console.log(regAttr);
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
          } else if (regAttr == 'update') {
            devPosRow.style.display = '';
            devRotRow.style.display = '';
            devLocTypeRow.style.display = '';
            regDevUpdateMac.value = d.MAC;
            regDevUpdateName.value = d.NAME;
            regDevUpdateDesc.value = d.DESCRIPTION;
            regDevUpdatePosX.value = d.DEPLOY_X;
            regDevUpdatePosY.value = d.DEPLOY_Y;
            regDevUpdatePosZ.value = d.DEPLOY_Z;
            regDevUpdateRotX.value = d.ROT_X;
            regDevUpdateRotY.value = d.ROT_Y;
            regDevUpdateRotZ.value = d.ROT_Z;
            regDevUpdateType.value = d.TYPE;
            regDevUpdateLoc.value = d.ROOM_NAME;
            regDevUpdateDescLabel.innerHTML = `Device Descriptiong:`;
            regDevUpdateLoc.setAttribute("ouuid", d.ROOM_UUID);
            regDevUpdateLoc.setAttribute("uuid", d.ROOM_UUID);
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
          } else {
            regDevUpdateMac.value = d.MAC;
            regDevUpdateName.value = d.NAME;
            devPosRow.style.display = 'none';
            devRotRow.style.display = 'none';
            devLocTypeRow.style.display = 'none';
            regDevUpdateDescLabel.innerHTML = `Device Configuration(<i>Put <strong>;</strong> in end of line</i>)`;
            regDevUpdateDesc.value = "";
            updateRegDevSubmitBtn.classList.remove("btn-danger");
            updateRegDevSubmitBtn.classList.add("btn-primary");
            updateRegDevSubmitBtn.innerHTML = "Send";
            updateRegDevForm.style.display = "";
            updateRegDevSubmitBtn.removeAttribute("onclick");
            updateRegDevMac.innerText = "";
            updateRegDevName.innerText = "";
            updateRegDevSubmitBtn.setAttribute(
              "onclick",
              "sendDeviceConfiguration()"
            );
            updateRegDevModalTitle.innerHTML = "Send Device Configuration";
          }
        });
      }
      hideLoading()
    })
    .catch((error) => {
      hideLoading()
      showToast("Error"+String(error), false);
      console.error("Error:", error);
    });
});

registerDevAddLoc.addEventListener("input", e => {
  if (e.target.value != "") {    
    // posDetDev.setAttribute("uid", "");
    RData = {
      VALUE: e.target.value,
    };
    Object.assign(RData, RequestData());
    showLoading()
    fetch(`${host}/api/getRoomSuggestion`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(RData),
    })
      .then((response) => response.json())
      .then((data) => {
        removeChildEl("register-device-add-location-sugg");
        // console.log(data);
        if (data["DATA"].length > 0) {
          // console.log(data)
          data["DATA"].forEach((node) => {
            b = document.createElement("DIV");
            b.innerHTML = node.ROOM_NAME;
            b.setAttribute("uuid", node.ROOM_UUID)
            b.addEventListener("click", function (e) {
              if (e.target.nodeName == "DIV") {
                removeChildEl("register-device-add-location-sugg");
                // addSensorName.value = node.NAME;
                registerDevAddLoc.value = e.target.innerHTML;
                registerDevAddLoc.setAttribute("uuid", e.target.getAttribute('uuid'));
                // addSensorType.value = node.SENSOR_TYPE;
                registerDevAddLoc.style.border = borderOri;
                registerDevAddLocErr.innerHTML = "";
              }
            });
            registerDevAddLocSugg.appendChild(b);
          });
        }
        hideLoading()
      })
      .catch((error) => {
        hideLoading()
        showToast("Error"+String(error), false);
        console.error("Error:", error);
      });
  } else {
    removeChildEl("register-device-add-location-sugg");
    registerDevAddLoc.style.border = borderOri;
    registerDevAddLocErr.innerHTML = "";
  }
})

regDevUpdateLoc.addEventListener("input", e => {
  if (e.target.value != "") {    
    // posDetDev.setAttribute("uid", "");
    RData = {
      VALUE: e.target.value,
    };
    Object.assign(RData, RequestData());
    showLoading()
    fetch(`${host}/api/getRoomSuggestion`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(RData),
    })
      .then((response) => response.json())
      .then((data) => {
        removeChildEl("register-device-update-location-sugg");
        // console.log(data);
        if (data["DATA"].length > 0) {
          // console.log(data)
          data["DATA"].forEach((node) => {
            b = document.createElement("DIV");
            b.innerHTML = node.ROOM_NAME;
            b.setAttribute("uuid", node.ROOM_UUID)
            b.addEventListener("click", function (e) {
              if (e.target.nodeName == "DIV") {
                removeChildEl("register-device-update-location-sugg");
                // addSensorName.value = node.NAME;
                regDevUpdateLoc.value = e.target.innerHTML;
                regDevUpdateLoc.setAttribute("uuid", e.target.getAttribute('uuid'));
                // addSensorType.value = node.SENSOR_TYPE;
                regDevUpdateLoc.style.border = borderOri;
                regDevUpdateLocErr.innerHTML = "";
              }
            });
            regDevUpdateLocSugg.appendChild(b);
          });
        }

        hideLoading()
      })
      .catch((error) => {
        showToast("Error"+String(error), false);
        console.error("Error:", error);
      });
  } else {
    removeChildEl("register-device-update-location-sugg");
    regDevUpdateLoc.style.border = borderOri;
    regDevUpdateLocErr.innerHTML = "";
  }
})

async function sendDeviceConfiguration(){
  if(regDevUpdateDesc.value != "" && regDevUpdateMac.value != ""){
    publishToMQTT(regDevUpdateDesc.value, `/GMT/DEV/${regDevUpdateMac.value}/C/SAVECFG`);
    document.querySelector("#registed-modal-close").click();
    setCookie("deviceConfMac", regDevUpdateMac.value, .0005);
    
  }  
}

async function updateDeviceDetail() {
  updateRegDevSubmitBtn.disabled = true;
  regDevUpdateMacErr.innerText = "";
  regDevUpdateMac.style.border = borderOri;
  regDevUpdateNameErr.innerText = "";
  regDevUpdateName.style.border = borderOri;
  regDevUpdatePosXErr.innerText = "";
  regDevUpdatePosX.style.border = borderOri;
  regDevUpdatePosYErr.innerText = "";
  regDevUpdatePosY.style.border = borderOri;
  regDevUpdatePosZErr.innerText = "";
  regDevUpdatePosZ.style.border = borderOri;
  regDevUpdateRotXErr.innerText = "";
  regDevUpdateRotX.style.border = borderOri;
  regDevUpdateRotYErr.innerText = "";
  regDevUpdateRotY.style.border = borderOri;
  regDevUpdateRotZErr.innerText = "";
  regDevUpdateRotZ.style.border = borderOri;
  regDevUpdateTypeErr.innerText = "";
  regDevUpdateType.style.border = borderOri;
  regDevUpdateLocErr.innerText = "";
  regDevUpdateLoc.style.border = borderOri;
  if (regDevUpdateMac.value == "") {
    regDevUpdateMac.style.border = borderRed;
    regDevUpdateMacErr.innerText = "Please add mac address";
  }
  if (regDevUpdateName.value == "") {
    regDevUpdateName.style.border = borderRed;
    regDevUpdateNameErr.innerText = "Please add device name";
  }
  if (regDevUpdatePosX.value == "") {
    regDevUpdatePosX.style.border = borderRed;
    regDevUpdatePosXErr.innerText = "Please add device position(X)";
  }
  if (regDevUpdatePosY.value == "") {
    regDevUpdatePosY.style.border = borderRed;
    regDevUpdatePosYErr.innerText = "Please add device position(Y)";
  }
  if (regDevUpdatePosZ.value == "") {
    regDevUpdatePosZ.style.border = borderRed;
    regDevUpdatePosZErr.innerText = "Please add device position(Z)";
  }
  if (regDevUpdateRotX.value == "") {
    regDevUpdateRotX.style.border = borderRed;
    regDevUpdateRotXErr.innerText = "Please add device rotation(X)";
  }
  if (regDevUpdateRotY.value == "") {
    regDevUpdateRotY.style.border = borderRed;
    regDevUpdateRotYErr.innerText = "Please add device rotation(Y)";
  }
  if (regDevUpdateRotZ.value == "") {
    regDevUpdateRotZ.style.border = borderRed;
    regDevUpdateRotZErr.innerText = "Please add device rotation(Z)";
  }
  if (regDevUpdateType.value == "") {
    regDevUpdateType.style.border = borderRed;
    regDevUpdateTypeErr.innerText = "Please select device type";
  }
  if (regDevUpdateLoc.value == "0") {
    regDevUpdateLoc.style.border = borderRed;
    regDevUpdateLocErr.innerText = "Please add device location";
  }
  if (
    regDevUpdateMacErr.innerText != "" ||
    regDevUpdateNameErr.innerText != "" ||
    regDevUpdatePosXErr.innerText != "" ||
    regDevUpdatePosYErr.innerText != "" ||
    regDevUpdatePosZErr.innerText != "" ||
    regDevUpdateRotXErr.innerText != "" ||
    regDevUpdateRotYErr.innerText != "" ||
    regDevUpdateRotZErr.innerText != "" ||
    regDevUpdateLocErr.innerText != "" ||
    regDevUpdateTypeErr.innerText != ""
  ) {
    updateRegDevSubmitBtn.disabled = false;
    return;
  }
  RData = {
    Id: updateRegDevSubmitBtn.getAttribute("Id"),
    MAC: regDevUpdateMac.value,
    NAME: regDevUpdateName.value,
    DEPLOY_X: regDevUpdatePosX.value,
    DEPLOY_Y: regDevUpdatePosY.value,
    DEPLOY_Z: regDevUpdatePosZ.value,
    ROT_X: regDevUpdateRotX.value,
    ROT_Y: regDevUpdateRotY.value,
    ROT_Z: regDevUpdateRotZ.value,
    DEPLOY_LOC: regDevUpdateLoc.getAttribute("uuid"),
    DEPLOY_O_LOC: regDevUpdateLoc.getAttribute("ouuid"),
    DEVICE_TYPE: regDevUpdateType.value,
    DESCRIPTION: regDevUpdateDesc.value,
  };
  Object.assign(RData, RequestData());
  console.log(RData);
  showLoading()
  await fetch(`${host}/updateDevice`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(RData),
  })
    .then((response) => response.json())
    .then((data) => {
      // console.log(data);
      response = data;
      
      if (data.DATA) {
        document.querySelector('#registed-modal-close').click();
        showToast(`<p>Device name <strong>${regDevUpdateName.value}</strong> has been updated successfully</p>`, true);
        fetchRegDevices()
        // popupMessageTitle.innerHTML = "Update Device"
        // popupMessageBody.innerHTML = `<p>Device name <strong>${regDevUpdateName.value}</strong> has been updated successfully</p>`
        // document.querySelector("#popupMessageOpenBtn").click()
        setTimeout(() => {
          publishToMQTT(regDevUpdateMac.value, '/GMT/USVC/DECODE_PUBLISH/C/UPDATE_DEV_CONF');
          updateRegDevSubmitBtn.disabled = false;
          // document.querySelector(".btn-close").click();
          // location.reload();
        }, 5000);        
      } else if (data.ERROR) {
        updateRegDevSubmitBtn.disabled = false;
        console.log(data.ERROR);
        if ("NAME" in data.ERROR[0]) {
          regDevUpdateNameErr.innerText = data.ERROR[0].NAME;
          regDevUpdateName.style.border = borderRed;
        }
        if ("MAC" in data.ERROR[0]) {
          regDevUpdateMac.style.border = borderRed;
          regDevUpdateMacErr.innerText = data.ERROR[0].MAC;
        }
        if ("DEPLOY_X" in data.ERROR[0]) {
          regDevUpdatePosX.style.border = borderRed;
          regDevUpdatePosXErr.innerText = data.ERROR[0].DEPLOY_X;
        }
        if ("DEPLOY_Y" in data.ERROR[0]) {
          regDevUpdatePosY.style.border = borderRed;
          regDevUpdatePosYErr.innerText = data.ERROR[0].DEPLOY_Y;
        }
        if ("DEPLOY_Z" in data.ERROR[0]) {
          regDevUpdatePosZ.style.border = borderRed;
          regDevUpdatePosZErr.innerText = data.ERROR[0].DEPLOY_Z;
        }
        if ("ROT_X" in data.ERROR[0]) {
          regDevUpdateRotX.style.border = borderRed;
          regDevUpdateRotXErr.innerText = data.ERROR[0].ROT_X;
        }
        if ("ROT_Y" in data.ERROR[0]) {
          regDevUpdateRotY.style.border = borderRed;
          regDevUpdateRotYErr.innerText = data.ERROR[0].ROT_Y;
        }
        if ("ROT_Z" in data.ERROR[0]) {
          regDevUpdateRotZ.style.border = borderRed;
          regDevUpdateRotZErr.innerText = data.ERROR[0].ROT_Z;
        }
        if ("DEVICE_TYPE" in data.ERROR[0]) {
          regDevUpdateType.style.border = borderRed;
          regDevUpdateTypeErr.innerText = data.ERROR[0].DEVICE_TYPE;
        }
        if ("DEPLOY_LOC" in data.ERROR[0]) {
          regDevUpdateLoc.style.border = borderRed;
          regDevUpdateLocErr.innerText = data.ERROR[0].DEPLOY_LOC;
        }
      }
      hideLoading()
    })
    .catch((error) => {
      hideLoading()
      console.error("Error:", error);
      showToast("Error"+String(error), false);
      updateRegDevSubmitBtn.disabled = false;
    });
}

async function deleteDeviceDetail() {
  updateRegDevSubmitBtn.disabled = true;
  RData = {
    Id: updateRegDevSubmitBtn.getAttribute("Id"),
    MAC: updateRegDevSubmitBtn.getAttribute("mac"),
  };
  console.log(RData);
  Object.assign(RData, RequestData());
  showLoading()
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
        document.querySelector('#registed-modal-close').click();
        showToast(`<p>Device name <strong>${updateRegDevSubmitBtn.getAttribute('dev-name')}</strong> has been deleted successfully</p>`, true);
        fetchRegDevices()
        // popupMessageTitle.innerHTML = "Delete Device"
        // popupMessageBody.innerHTML = `<p>Device name <strong>${updateRegDevSubmitBtn.getAttribute('dev-name')}</strong> has been deleted successfully</p>`
        // document.querySelector("#popupMessageOpenBtn").click()
        // setTimeout(()=>{
        //   location.reload()
        // }, 3000)
      }
      hideLoading()
    })
    .catch((error) => {
      hideLoading()
      console.error("Error:", error);
      showToast("Error"+String(error), false);
      updateRegDevSubmitBtn.disabled = false;
    });
}

async function addNewDevice() {
  registerDevAddSubmitBtn.disabled = true;
  registerDevAddMac.style.border = borderOri;
  registerDevAddPassword.style.border = borderOri;
  registerDevAddName.style.border = borderOri;
  registerDevAddPosX.style.border = borderOri;
  registerDevAddPosY.style.border = borderOri;
  registerDevAddPosZ.style.border = borderOri;
  registerDevAddRotX.style.border = borderOri;
  registerDevAddRotY.style.border = borderOri;
  registerDevAddRotZ.style.border = borderOri;
  registerDevAddType.style.border = borderOri;
  registerDevAddLoc.style.border = borderOri;
  registerDevAddMacErr.innerText = "";
  registerDevAddPasswordErr.innerText = "";
  registerDevAddNameErr.innerText = "";
  registerDevAddPosXErr.innerText = "";
  registerDevAddPosYErr.innerText = "";
  registerDevAddPosZErr.innerText = "";
  registerDevAddRotXErr.innerText = "";
  registerDevAddRotYErr.innerText = "";
  registerDevAddRotZErr.innerText = "";
  registerDevAddLocErr.innerText = "";
  registerDevAddTypeErr.innerText = "";

  if (registerDevAddMac.value == "") {
    registerDevAddMac.style.border = borderRed;
    registerDevAddMacErr.innerText = "Please add mac address";
  }
  if (registerDevAddPassword.value == "") {
    registerDevAddPassword.style.border = borderRed;
    registerDevAddPasswordErr.innerText = "Please add device password";
  }
  if (registerDevAddName.value == "") {
    registerDevAddName.style.border = borderRed;
    registerDevAddNameErr.innerText = "Please add device name";
  }
  if (registerDevAddPosX.value == "") {
    registerDevAddPosX.style.border = borderRed;
    registerDevAddPosXErr.innerText = "Please add device position(X)";
  }
  if (registerDevAddPosY.value == "") {
    registerDevAddPosY.style.border = borderRed;
    registerDevAddPosYErr.innerText = "Please add device position(Y)";
  }
  if (registerDevAddPosZ.value == "") {
    registerDevAddPosZ.style.border = borderRed;
    registerDevAddPosZErr.innerText = "Please add device position(Z)";
  }
  if (registerDevAddRotX.value == "") {
    registerDevAddRotX.style.border = borderRed;
    registerDevAddRotXErr.innerText = "Please add device rotation(X)";
  }
  if (registerDevAddRotY.value == "") {
    registerDevAddRotY.style.border = borderRed;
    registerDevAddRotYErr.innerText = "Please add device rotation(Y)";
  }
  if (registerDevAddRotZ.value == "") {
    registerDevAddRotZ.style.border = borderRed;
    registerDevAddRotZErr.innerText = "Please add device rotation(Z)";
  }
  if (registerDevAddLoc.value == "") {
    registerDevAddLoc.style.border = borderRed;
    registerDevAddLocErr.innerText = "Please add device location";
  }
  if (registerDevAddType.value == "0") {
    registerDevAddType.style.border = borderRed;
    registerDevAddTypeErr.innerText = "Please select device type";
  }
  if (
    registerDevAddMacErr.innerText != "" ||
    registerDevAddPasswordErr.innerText != "" ||
    registerDevAddNameErr.innerText != "" ||
    registerDevAddPosXErr.innerText != "" ||
    registerDevAddPosYErr.innerText != "" ||
    registerDevAddPosZErr.innerText != "" ||
    registerDevAddRotXErr.innerText != "" ||
    registerDevAddRotYErr.innerText != "" ||
    registerDevAddRotZErr.innerText != "" ||
    registerDevAddLocErr.innerText != "" ||
    registerDevAddTypeErr.innerText != ""
  ) {
    registerDevAddSubmitBtn.disabled = false;
    return;
  }
  let Rdata = {};
  Rdata = {
    MAC: registerDevAddMac.value,
    NAME: registerDevAddName.value,
    DEPLOY_X: registerDevAddPosX.value,
    DEPLOY_Y: registerDevAddPosY.value,
    DEPLOY_Z: registerDevAddPosZ.value,
    ROT_X: registerDevAddRotX.value,
    ROT_Y: registerDevAddRotY.value,
    ROT_Z: registerDevAddRotZ.value,
    DEVICE_TYPE: registerDevAddType.value,
    DEPLOY_LOC: registerDevAddLoc.getAttribute("uuid"),
    DESCRIPTION: registerDevAddDesc.value,
  };
  Object.assign(Rdata, RequestData());
  showLoading()
  await fetch(`${host}/addNewDevice`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(Rdata),
  })
    .then((response) => response.json())
    .then(async (data) => {
      // console.log(data);
      response = data;
      if ("DATA" in data) {
        registerDevAddSubmitBtn.disabled = false;
        document.querySelector('#register-device-add-close-btn').click();
        showToast(`<p>New device <strong>${registerDevAddName.value}</strong> has been added successfully</p>`, true);
        let Cdata = {};
        Cdata = {
          username: registerDevAddMac.value,
          password: registerDevAddPassword.value
        };
        Object.assign(Cdata, RequestData());
        showLoading()
        await fetch(`${host}/addDeviceCredential`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(Cdata),
        })
          .then((response2) => response2.json())
          .then((data2) => {
            console.log(data2);
          })
        fetchRegDevices()
        // getRoomData()
        // popupMessageTitle.innerHTML = "Add Device"
        // popupMessageBody.innerHTML = `<p>New device <strong>${registerDevAddName.value}</strong> has been added successfully</p>`
        // document.querySelector("#popupMessageOpenBtn").click()
        // setTimeout(()=>{
        //   location.reload()
        // }, 3000)
      } else {
        registerDevAddSubmitBtn.disabled = false;
        // console.log(data.ERROR);
        if ("NAME" in data.ERROR[0]) {
          registerDevAddNameErr.innerText = data.ERROR[0].NAME;
          registerDevAddName.style.border = borderRed;
        }
        if ("MAC" in data.ERROR[0]) {
          registerDevAddMac.style.border = borderRed;
          registerDevAddMacErr.innerText = data.ERROR[0].MAC;
        }
        if ("DEPLOY_X" in data.ERROR[0]) {
          registerDevAddPosX.style.border = borderRed;
          registerDevAddPosXErr.innerText = data.ERROR[0].DEPLOY_X;
        }
        if ("DEPLOY_Y" in data.ERROR[0]) {
          registerDevAddPosY.style.border = borderRed;
          registerDevAddPosYErr.innerText = data.ERROR[0].DEPLOY_Y;
        }
        if ("DEPLOY_Z" in data.ERROR[0]) {
          registerDevAddPosZ.style.border = borderRed;
          registerDevAddPosZErr.innerText = data.ERROR[0].DEPLOY_Z;
        }
        if ("ROT_X" in data.ERROR[0]) {
          registerDevAddRotX.style.border = borderRed;
          registerDevAddRotXErr.innerText = data.ERROR[0].ROT_X;
        }
        if ("ROT_Y" in data.ERROR[0]) {
          registerDevAddRotY.style.border = borderRed;
          registerDevAddRotYErr.innerText = data.ERROR[0].ROT_Y;
        }
        if ("ROT_Z" in data.ERROR[0]) {
          registerDevAddRotZ.style.border = borderRed;
          registerDevAddRotZErr.innerText = data.ERROR[0].ROT_Z;
        }
        if ("DEPLOY_LOC" in data.ERROR[0]) {
          registerDevAddLoc.style.border = borderRed;
          registerDevAddLocErr.innerText = data.ERROR[0].DEPLOY_LOC;
        }
        if ("DEVICE_TYPE" in data.ERROR[0]) {
          registerDevAddType.style.border = borderRed;
          registerDevAddTypeErr.innerText = data.ERROR[0].DEVICE_TYPE;
        }
      }
      hideLoading()
    })
    .catch((error) => {
      hideLoading()
      console.error("Error:", error);
      showToast("Error"+String(error), false);
      registerDevAddSubmitBtn.disabled = false;
    });
}

function publishToMQTT(msg, topic){
  message = new Paho.MQTT.Message(msg);
  message.destinationName = topic;
  client.send(message);
}
