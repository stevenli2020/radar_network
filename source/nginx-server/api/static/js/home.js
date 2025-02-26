const indiCard = document.getElementById("ag-courses_box");
// add room details form
const addRoomRow = document.getElementById("add-room-button");
const addRoomName = document.getElementById("room-add-name");
const addRoomNameError = document.getElementById("room-add-name-error");
const addRoomLoc = document.getElementById("room-add-loc");
const addRoomLocError = document.getElementById("room-add-loc-error");
const addRoomX = document.getElementById("room-x-add");
const addRoomXError = document.getElementById("room-x-add-error");
const addRoomY = document.getElementById("room-y-add");
const addRoomYError = document.getElementById("room-y-add-error");
const addRoomDesc = document.getElementById("room-info");
const imgUpload = document.getElementById("add-room-img-upload");
const imgUploadError = document.getElementById("addRoomImgUploadError");
const addRoomSubmitBtn = document.getElementById("room-submit-btn");
// update room details form
const updateRoomForm = document.getElementById("update-room-form");
const updateRoomBtn = document.getElementById("room-update-modal");
const updateRoomFormTitle = document.getElementById("room-update-modalLabel");
const updateRoomName = document.getElementById("room-update-name");
const updateRoomNameError = document.getElementById("room-add-name-error");
const updateRoomLoc = document.getElementById("room-update-loc");
const updateRoomLocError = document.getElementById("room-update-loc-error");
const updateRoomX = document.getElementById("room-x-update");
const updateRoomXError = document.getElementById("room-x-update-error");
const updateRoomY = document.getElementById("room-y-update");
const updateRoomYError = document.getElementById("room-y-update-error");
const updateRoomDesc = document.getElementById("update-room-info");
const updateImgUpload = document.getElementById("update-room-img-upload");
const updateImgUploadError = document.getElementById(
  "updateRoomImgUploadError"
);
const updateRoomSubmitBtn = document.getElementById("update-room-submit-btn");
// delete room modal
const deleteRoomP = document.getElementById("delete-room-name-p");

const moreDetailsDiv = document.getElementById("more-details-box");
const loadingDiv = document.getElementById("loading");
const detailsContentDiv = document.getElementById("details-content");

// Sleeping Hour
const sleepingWeeklyAverage = document.getElementById("sleeping-hour-average");

// Bed Time
const bedWeeklyAverage = document.getElementById("bed-time-average");

// Morning Wake Up Time
const wakeWeeklyAverage = document.getElementById("wake-time-average");

// Time In Bed
const inbedWeeklyAverage = document.getElementById("inbed-time-average");

// In Room
const inroomWeeklyAverage = document.getElementById("inroom-time-average");

// Sleep disruption
const disruptionWeeklyAverage = document.getElementById("disruption-average");

// breath Rate
const breathWeeklyAverage = document.getElementById("breath-rate-average");

// Heart Rate
const heartWeeklyAverage = document.getElementById("heart-rate-average");

var currentDetailsID = null

if (checkAdmin()) {
  addRoomRow.style.display = "block";
}

getRoomData();
// setInterval(getRoomData, 5000, 5)

async function getRoomData(t = 1) {
  showLoading()
  await fetch(`${host}/api/getRoomDetails`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(RequestData()),
  })
    .then((response) => response.json())
    .then((data) => {

      if (data.DATA) {
        while (indiCard.firstChild) {
          indiCard.removeChild(indiCard.firstChild);
        }
        data.DATA.forEach((d) => {
          if (t == 1) addCard(d);
          else updateCard(d);
        });
      }

      hideLoading()
    })
    .catch((error) => {
      console.error("Error:", error);
      showToast("Error"+String(error), false);
      hideLoading()
    });
}

async function getSpecificDevice(mac, t = 1) {
  rData = {
    MAC: mac,
  };
  let result = null;
  Object.assign(rData, RequestData());
  showLoading()
  await fetch(`${host}/getRegDevice`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(rData),
  })
    .then((response) => response.json())
    .then((data) => {
      // console.log(data);
      if (data.DATA) {
        result = data.DATA;
      }

      hideLoading()
    })
    .catch((error) => {
      hideLoading()
      console.error("Error:", error);
      showToast("Error"+String(error), false);
    });
  return result;
}

function roomStatus(st) {
  let roomStat = "";
  switch (st) {
    case 0:
      roomStat = "Room is empty";
      break;
    case 1:
      roomStat = "Room is occupied";
      break;
    case 2:
      roomStat = "Sleeping";
      break;
    case 255:
      roomStat = "Alert";
      break;
    default:
      roomStat = "Room is empty";
  }
  return roomStat;
}

function updateCard(posMac) {
  let posUpdateStatus = document.getElementById(posMac.ID + "-status");
  let posUpdateTime = document.getElementById(posMac.ID + "-timestamp");
  let posOccuTime = document.getElementById(posMac.ID + "-occupancy");
  // let vitalUpdateStatus = document.getElementById(vitalMac[0].Id+"-status")
  // let vitalUpdateTime = document.getElementById(vitalMac[0].Id+"-timestamp")
  posUpdateStatus.innerHTML = `Status: <span class='ag-courses-item_date'>${roomStatus(
    posMac.STATUS
  )}</span>`;
  posUpdateTime.innerHTML = `Time: <span class='ag-courses-item_date'>${posMac.LAST_DATA_TS.substring(
    0,
    posMac.LAST_DATA_TS.length - 3
  )}</span>`;
  try{
    posOccuTime.innerHTML = `<span class='ag-courses-item_date'>${posMac.OCCUPANCY} people in room</span>`;
  } catch(ex){

  }
}

function fetchDetailsbyID(data){
  loadingDiv.style.display = "none"
  detailsContentDiv.style.display = "block"
  const tableBody = document.getElementById('tableBody');

  while (tableBody.firstChild) {
      tableBody.removeChild(tableBody.firstChild);
  }

  // Iterate through the data and create table rows
  data.forEach(item => {
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
}

function addCard(d) {
  let firDiv = document.createElement("div");
  let aTag = document.createElement("div");
  let secDiv = document.createElement("div");
  let thirdDiv = document.createElement("div");
  let rowS = document.createElement("div");
  firDiv.setAttribute("class", "ag-courses_item");
  secDiv.style.position = "absolute";
  secDiv.style.bottom = "5%";
  secDiv.style.right = "5%";

  firDiv.addEventListener("mouseover", function (event) {
    if (true){
      currentDetailsID = d.ROOM_UUID
      if (d["ALERTS"].length > 0){
        loadingDiv.style.display = "block"
        detailsContentDiv.style.display = "none"
        var rect = firDiv.getBoundingClientRect();

        // Calculate the position relative to firDiv
        var left, top;

        // Calculate left position relative to firDiv
        if (rect.right < window.innerWidth / 2) {
            left = rect.right + 10;
        } else {
            left = rect.left - moreDetailsDiv.offsetWidth + 10;
        }

        // Calculate top position relative to firDiv
        if (rect.top < window.innerHeight / 2) {
            top = rect.bottom + 10; 
        } else {
            top = rect.top - moreDetailsDiv.offsetHeight + 10;
        }

        // Set the position of moreDetailsDiv relative to firDiv
        moreDetailsDiv.style.left = left + 'px';
        moreDetailsDiv.style.top = top + 'px';

        moreDetailsDiv.style.display = 'flex'; // Show moreDetailsDiv
        fetchDetailsbyID(d["ALERTS"])
      }
    }

  });
  firDiv.addEventListener("mouseout", function () {
    moreDetailsDiv.style.display = 'none';
    loadingDiv.style.display = "none"
    detailsContentDiv.style.display = "none"
  });
  // secDiv.style.padding = "5px";
  // secDiv.style.display = "flex";
  // secDiv.style.flexDirection = "row-reverse";
  aTag.setAttribute(
    "onclick",
    `window.location.href='${host}/Detail/Layman?room=${d.ROOM_UUID}'`
  );
  aTag.style.cursor = "pointer";
  aTag.setAttribute("class", "ag-courses-item_link");
  thirdDiv.setAttribute("class", "ag-courses-item_title");
  thirdDiv.innerText = d.ROOM_NAME;
  if (d.ALERTS.length > 0){
    thirdDiv.innerHTML += '  <i id="popper-alerts" style="cursor: pointer;" class="bi bi-exclamation-triangle-fill"  aria-describedby="tooltip-popper"></i>';
  }
  if (checkAdmin()) {
    // secDiv.innerHTML = `
    //   <i style='color: red; margin-right: 20px;' class='bi bi-trash3 tooltipcss' class='btn btn-danger' data-bs-toggle='modal' data-bs-target='#room-update-modal' attr='delete' data-bs-whatever="${d.ROOM_UUID}"><span class='tooltiptextcss'>Delete</span></i>&nbsp;&nbsp;&nbsp;<i style='color: green;' class='tooltipcss bi bi-pencil-square' data-bs-toggle='modal' data-bs-target='#room-update-modal' attr='update' data-bs-whatever="${d.ROOM_UUID}"><span class='tooltiptextcss'>Update</span></i>
    //   `;
    secDiv.innerHTML = `<i id="popper-firstDiv" style="cursor: pointer;" class="bi bi-three-dots-vertical icon-popper-${d.ROOM_UUID}"  aria-describedby="tooltip-popper"></i>
    <div id="tooltip-popper" class="tooltip-popper-${d.ROOM_UUID}" role="tooltip-popper">
      <i style='color: green; cursor: pointer;float: left; width: 50%; margin-top: 4px;' class='bi bi-pencil-square' data-bs-toggle='modal' data-bs-target='#room-update-modal' attr='update' data-bs-whatever="${d.ROOM_UUID}"></i>&nbsp;&nbsp;&nbsp;<i style='color: red; cursor: pointer;float: left; width: 50%; margin-top: 4px;' class='bi bi-trash3' class='btn btn-danger' data-bs-toggle='modal' data-bs-target='#room-update-modal' attr='delete' data-bs-whatever="${d.ROOM_UUID}"></i>
    <div id="arrow-popper" data-popper-arrow></div>
    </div>`;
  }

  let localSg = "-";
  if (d.LAST_DATA_TS) {
    localSg = getTimezoneOffset(d.LAST_DATA_TS);
    localSg = moment(localSg).fromNow();
  }

  rowS.innerHTML = `   
      <div class="ag-courses-item_date-box">
        <span class='ag-courses-item_date'><strong>${
          d.INFO ? d.INFO : "-"
        }</strong></span>
      </div>   
      <div class="ag-courses-item_date-box" id="${d.ID}-status">
        Status: <span class='ag-courses-item_date'>${roomStatus(
          d.STATUS
        )}</span>
      </div>
      <div class="ag-courses-item_date-box">
        Location: <span class='ag-courses-item_date'>${d.ROOM_LOC}</span>
      </div>
      <div  class="ag-courses-item_date-box" id="${d.ID}-timestamp">
        Last data: <span class='ag-courses-item_date'>${localSg}</span>
      </div>
    `;
  aTag.appendChild(thirdDiv);
  aTag.appendChild(rowS);
  firDiv.appendChild(aTag);
  firDiv.appendChild(secDiv);

  indiCard.appendChild(firDiv);
  try{
    const popcornPopper = document.querySelector(`.icon-popper-${d.ROOM_UUID}`);
    const tooltipPopper = document.querySelector(`.tooltip-popper-${d.ROOM_UUID}`);

    const popperInstance = Popper.createPopper(popcornPopper, tooltipPopper, {
      modifiers: [
        {
          name: 'offset',
          options: {
            offset: [0, 8],
          },
        },
      ],
    });
    function show() {
      // Make the tooltip visible
      tooltipPopper.setAttribute("data-show", "");
  
      // Enable the event listeners
      popperInstance.setOptions((options) => ({
        ...options,
        modifiers: [
          ...options.modifiers,
          { name: "eventListeners", enabled: true },
        ],
      }));
  
      // Update its position
      popperInstance.update();
    }
  
    function hide() {
      // Hide the tooltip
      tooltipPopper.removeAttribute("data-show");
  
      // Disable the event listeners
      popperInstance.setOptions((options) => ({
        ...options,
        modifiers: [
          ...options.modifiers,
          { name: "eventListeners", enabled: false },
        ],
      }));
    }
  
    const showEvents = ["mouseenter", "focus"];
    // const hideEvents = ["mouseleave", "blur"];
    const hideEvents = ["click"];
    // const toggleEvents = ["click"];
  
    showEvents.forEach((event) => {
      popcornPopper.addEventListener(event, show);
    });
  
    hideEvents.forEach((event) => {
      popcornPopper.addEventListener(event, hide);
    });
  
    // toggleEvents.forEach((event) => {
    //   console.log(tooltipPopper.hasAttribute('data-show'))
    //   if(tooltipPopper.hasAttribute('data-show'))
    //     popcornPopper.addEventListener(event, hide);
    //   else
    //     popcornPopper.addEventListener(event, show);
    // });
  
  }catch(ex){

  }
}



async function addNewRoom() {
  addRoomSubmitBtn.disabled = true;
  addRoomNameError.innerHTML = "";
  addRoomName.style.border = borderOri;
  addRoomXError.innerHTML = "";
  addRoomX.style.border = borderOri;
  addRoomYError.innerHTML = "";
  addRoomY.style.border = borderOri;
  // imgUploadError.innerHTML = "";
  // imgUpload.style.border = borderOri;

  if (addRoomName.value == "") {
    addRoomNameError.innerText = "Room name is empty!";
    addRoomName.style.border = borderRed;
  } else {
    if (addRoomX.value == "") {
      addRoomXError.innerText = "Please add value!";
      addRoomX.style.border = borderRed;
    }
    if (addRoomY.value == "") {
      addRoomYError.innerText = "Please add value!";
      addRoomY.style.border = borderRed;
    }
  }

  if (addRoomX.value != "" || addRoomY.value != "") {
    if (addRoomName.value == "") {
      addRoomNameError.innerText = "Room name is empty!";
      addRoomName.style.border = borderRed;
    }
  }

  if (addRoomLoc.value == "") {
    addRoomLocError.innerText = "Room location is empty!";
    addRoomLoc.style.border = borderRed;
  }

  if (
    addRoomNameError.innerText != "" ||
    addRoomXError.innerText != "" ||
    addRoomYError.innerText != "" ||
    addRoomLocError.innerText != ""
  ) {
    addRoomSubmitBtn.disabled = false;
    return;
  }

  let RData = {
    ROOM_NAME: addRoomName.value,
    ROOM_X: parseFloat(addRoomX.value),
    ROOM_Y: parseFloat(addRoomY.value),
    ROOM_LOC: addRoomLoc.value,
    INFO: addRoomDesc.value,
    IMAGE_NAME: document
      .querySelector("#uploaded-img")
      .getAttribute("img-name"),
  };
  Object.assign(RData, RequestData());
  console.log(RData);
  showLoading()
  await fetch(`${host}/api/addNewRoom`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(RData),
  })
    .then((response) => response.json())
    .then((data) => {
      // removeChildEl("pos-detect-dev-suggest");
      addRoomSubmitBtn.disabled = false;
      console.log(data);
      if ("DATA" in data) {
        // console.log(data)
        // location.reload();
        showToast("New room added!", true);
        getRoomData()
        document.getElementById("close-add-modal").click()
      } else {
        if ("ROOM_NAME" in data.ERROR[0]) {
          addRoomNameError.innerText = data.ERROR[0].ROOM_NAME;
          addRoomName.style.border = borderRed;
        }
        if ("ROOM_X" in data.ERROR[0]) {
          addRoomXError.innerText = data.ERROR[0].ROOM_X;
          addRoomX.style.border = borderRed;
        }
        if ("ROOM_Y" in data.ERROR[0]) {
          addRoomYError.innerText = data.ERROR[0].ROOM_Y;
          addRoomY.style.border = borderRed;
        }
        if ("ROOM_LOC" in data.ERROR[0]) {
          addRoomLocError.innerText = data.ERROR[0].ROOM_LOC;
          addRoomLoc.style.border = borderRed;
        }
        // if("IMAGE_NAME" in data.ERROR[0]){
        //   imgUploadError.innerText = data.ERROR[0].RoomName
        //   imgUpload.style.border = borderRed
        // }
      }
      hideLoading()
    })
    .catch((error) => {
      hideLoading()
      console.error("Error:", error);
      showToast("Error"+String(error), false);
      addRoomSubmitBtn.disabled = false;
    });
}

async function updateRoom() {
  updateRoomSubmitBtn.disabled = true;
  updateRoomNameError.innerHTML = "";
  updateRoomName.style.border = borderOri;
  updateRoomXError.innerHTML = "";
  updateRoomX.style.border = borderOri;
  updateRoomYError.innerHTML = "";
  updateRoomY.style.border = borderOri;
  if (updateRoomName.value == "") {
    updateRoomNameError.innerText = "Room name is empty!";
    updateRoomName.style.border = borderRed;
  } else {
    if (updateRoomX.value == "") {
      updateRoomXError.innerText = "Please add value!";
      updateRoomX.style.border = borderRed;
    }
    if (updateRoomY.value == "") {
      updateRoomYError.innerText = "Please add value!";
      updateRoomY.style.border = borderRed;
    }
  }

  if (updateRoomX.value != "" || updateRoomY.value != "") {
    if (updateRoomName.value == "") {
      updateRoomNameError.innerText = "Room name is empty!";
      updateRoomName.style.border = borderRed;
    }
  }

  if (updateRoomLoc.value == "") {
    updateRoomLocError.innerText = "Room location is empty!";
    updateRoomLoc.style.border = borderRed;
  }

  // if(imgUpload.value == ""){
  //   imgUploadError.innerText = "Please upload room image!"
  //   imgUpload.style.border = borderRed
  // }

  if (
    updateRoomNameError.innerText != "" ||
    updateRoomXError.innerText != "" ||
    updateRoomYError.innerText != "" ||
    updateRoomLocError.innerText != ""
  ) {
    updateRoomSubmitBtn.disabled = false;
    return;
  }

  let RData = {
    ROOM_NAME: updateRoomName.value,
    ROOM_X: parseFloat(updateRoomX.value),
    ROOM_Y: parseFloat(updateRoomY.value),
    ROOM_LOC: updateRoomLoc.value,
    INFO: updateRoomDesc.value,
    IMAGE_NAME: document
      .querySelector("#uploaded-img")
      .getAttribute("img-name"),
    O_IMAGE_NAME: updateRoomSubmitBtn.getAttribute("o-img-name"),
    ROOM_UUID: updateRoomSubmitBtn.getAttribute("uuid"),
  };
  Object.assign(RData, RequestData());
  console.log(RData);
  showLoading()
  await fetch(`${host}/api/updateRoom`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(RData),
  })
    .then((response) => response.json())
    .then((data) => {
      // removeChildEl("pos-detect-dev-suggest");
      updateRoomSubmitBtn.disabled = false;
      console.log(data);
      if ("DATA" in data) {
        // console.log(data)
        // location.reload();
        showToast("Room information updated!", true);
        getRoomData()
        document.getElementById("close-update-modal").click()
      } else {
        if ("ROOM_NAME" in data.ERROR[0]) {
          updateRoomNameError.innerText = data.ERROR[0].ROOM_NAME;
          updateRoomName.style.border = borderRed;
        }
        if ("ROOM_X" in data.ERROR[0]) {
          updateRoomXError.innerText = data.ERROR[0].ROOM_X;
          updateRoomX.style.border = borderRed;
        }
        if ("ROOM_Y" in data.ERROR[0]) {
          updateRoomYError.innerText = data.ERROR[0].ROOM_Y;
          updateRoomY.style.border = borderRed;
        }
        if ("ROOM_LOC" in data.ERROR[0]) {
          updateRoomLocError.innerText = data.ERROR[0].ROOM_LOC;
          updateRoomLoc.style.border = borderRed;
        }
        // if("IMAGE_NAME" in data.ERROR[0]){
        //   imgUploadError.innerText = data.ERROR[0].RoomName
        //   imgUpload.style.border = borderRed
        // }
      }
      hideLoading()
    })
    .catch((error) => {
      hideLoading()
      console.error("Error:", error);
      showToast("Error"+String(error), false);
      updateRoomSubmitBtn.disabled = false;
    });
}

async function deletRoom() {
  Rdata = {
    ROOM_UUID: updateRoomSubmitBtn.getAttribute("uuid"),
    IMAGE_NAME: updateRoomSubmitBtn.getAttribute("img"),
  };
  Object.assign(Rdata, RequestData());
  showLoading()
  await fetch(`${host}/api/deleteRoom`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(Rdata),
  })
    .then((response) => response.json())
    .then((data) => {
      if ("DATA" in data) {
        // location.reload();
        showToast("Room deleted!", true);
        getRoomData()
        document.getElementById("close-update-modal").click()
      }
      hideLoading()
    })
    .catch((error) => {
      hideLoading()
      showToast("Error"+String(error), false);
      console.error("Error:", error);
    });
}

updateRoomBtn.addEventListener("show.bs.modal", async (event) => {
  // Button that triggered the modal
  const button = event.relatedTarget;
  // Extract info from data-bs-* attributes
  const roomId = button.getAttribute("data-bs-whatever");
  const regAttr = button.getAttribute("attr");
  Rdata = {
    ROOM_UUID: roomId,
  };
  Object.assign(Rdata, RequestData());
  showLoading()
  await fetch(`${host}/api/getRoomDetail`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(Rdata),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      data.DATA.forEach((d) => {
        if (regAttr == "update") {
          deleteRoomP.style.display = "none";
          updateRoomForm.style.display = "";
          updateRoomSubmitBtn.classList.remove("btn-danger");
          updateRoomSubmitBtn.classList.add("btn-primary");
          updateRoomSubmitBtn.setAttribute("uuid", d.ROOM_UUID);
          updateRoomSubmitBtn.setAttribute("o-img-name", d.IMAGE_NAME);
          updateRoomSubmitBtn.removeAttribute("onclick");
          updateRoomSubmitBtn.setAttribute("onclick", "updateRoom()");
          updateRoomSubmitBtn.innerText = "Update";
          updateRoomFormTitle.innerText = "Update Room";
          updateRoomName.value = d.ROOM_NAME;
          updateRoomLoc.value = d.ROOM_LOC;
          updateRoomX.value = d.ROOM_X;
          updateRoomY.value = d.ROOM_Y;
          updateRoomDesc.value = d.INFO;
          updateImgUploadError.innerHTML =
            '<div class="alert alert-success">Current Background Image</div> <img src="' +
            host +
            "/static/uploads/" +
            d.IMAGE_NAME +
            '" id="uploaded-img" img-name=' +
            d.IMAGE_NAME +
            " o-img-name=" +
            d.IMAGE_NAME +
            ' class="img-thumbnail centerImg" />';
        } else {
          deleteRoomP.style.display = "";
          updateRoomForm.style.display = "none";
          updateRoomSubmitBtn.classList.remove("btn-primary");
          updateRoomSubmitBtn.classList.add("btn-danger");
          updateRoomSubmitBtn.innerText = "Delete";
          updateRoomSubmitBtn.removeAttribute("onclick");
          updateRoomSubmitBtn.setAttribute("uuid", d.ROOM_UUID);
          updateRoomSubmitBtn.setAttribute("img", d.IMAGE_NAME);
          updateRoomSubmitBtn.setAttribute("onclick", "deletRoom()");
          updateRoomFormTitle.innerText = "Delete Room";
          deleteRoomP.innerHTML = `Are you sure you want to delete, <strong>${d.ROOM_NAME}</strong>?`;
        }
      });
      hideLoading()
    })
    .catch((error) => {
      hideLoading()
      showToast("Error"+String(error), false);
      console.error("Error:", error);
    });
});
