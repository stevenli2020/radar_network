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

if (!checkAdmin()) {
  addRoomRow.style.display = "none";
}

getRoomData();
// setInterval(getRoomData, 5000, 5)

async function getRoomData(t = 1) {
  await fetch(`${host}/api/getRoomDetails`, {
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
        data.DATA.forEach((d) => {
          if (t == 1) addCard(d);
          else updateCard(d);
          // let posMac = []
          // let vitalMac = []
          // let roomName = d.ROOM_NAME
          // let uuid = d.ROOM_UUID
          // if(d.POS_MAC != null || d.VITAL_MAC != null){
          //   if(d.POS_MAC){
          //     getSpecificDevice(d.POS_MAC)
          //       .then(data => {
          //         posMac = data
          //         getSpecificDevice(d.VITAL_MAC)
          //           .then(data => {
          //             vitalMac = data
          //             // console.log(posMac, vitalMac)
          //             if(t==1){
          //               addCard(roomName, posMac, vitalMac, uuid)
          //             } else{
          //               // console.log(vitalMac.length)
          //               if(vitalMac.length > 0){
          //                 updateCard(vitalMac)
          //                 updateCard(posMac)
          //               }
          //               else
          //                 updateCard(posMac)
          //             }
          //           })
          //       })
          //   } else {
          //     getSpecificDevice(d.VITAL_MAC).then(data => {
          //       vitalMac = data
          //       // console.log(posMac, vitalMac)
          //       if(t==1){
          //         addCard(roomName, posMac, vitalMac, uuid)
          //       } else{
          //         updateCard(vitalMac)
          //       }
          //     })
          //   }
          // }
        });
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

async function getSpecificDevice(mac, t = 1) {
  rData = {
    MAC: mac,
  };
  let result = null;
  Object.assign(rData, RequestData());
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
    })
    .catch((error) => {
      console.error("Error:", error);
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
  posOccuTime.innerHTML = `<span class='ag-courses-item_date'>${posMac.OCCUPANCY} people in room</span>`;
  // vitalUpdateStatus.innerHTML = `Status: <span class='ag-courses-item_date'>${vitalMac[0].STATUS}</span>`;
  // vitalUpdateTime.innerHTML = `Time: <span class='ag-courses-item_date'>${vitalMac[0].TIMESTAMP.substring(
  //   0,
  //   vitalMac[0].TIMESTAMP.length - 3
  // )}</span>`;
  // highlightFor(d.Id+"-status", 'yellow', 1);
  // highlightFor(d.Id+"-timestamp", 'yellow', 1);
}

function addCard(d) {
  let firDiv = document.createElement("div");
  let aTag = document.createElement("div");
  let secDiv = document.createElement("div");
  let thirdDiv = document.createElement("div");
  // let fourthDiv = document.createElement("div");
  // let fifthDiv = document.createElement("div");
  // let sixthDiv = document.createElement("div");
  let rowS = document.createElement("div");
  firDiv.setAttribute("class", "ag-courses_item");
  secDiv.style.position = "absolute";
  secDiv.style.bottom = "1%";
  secDiv.style.left = "80%";
  secDiv.style.padding = "5px";
  secDiv.style.display = "flex";
  secDiv.style.flexDirection = "row-reverse";
  // aTag.setAttribute("href", `/Detail?room=${d.UUID}`);
  aTag.setAttribute(
    "onclick",
    `window.location.href='${host}/Detail?room=${d.ROOM_UUID}'`
  );
  aTag.style.cursor = "pointer";
  aTag.setAttribute("class", "ag-courses-item_link");
  // secDiv.setAttribute("class", "ag-courses-item_bg");
  thirdDiv.setAttribute("class", "ag-courses-item_title");
  thirdDiv.innerText = d.ROOM_NAME;
  // date = new Date( Date.parse(d.LAST_DATA_TS)-28800000 )
  // dateFormat = date.getFullYear()+""+((date.getMonth()+1)<10?"0"+(date.getMonth()+1):(date.getMonth()+1))+""+date.getDate()+""+date.getHours()+""+date.getMinutes()+""+date.getSeconds()
  // console.log(d.LAST_DATA_TS, dateFormat)
  secDiv.innerHTML = `
  <i style='color: red; margin-right: 20px;' class='bi bi-trash3 tooltipcss' class='btn btn-danger' data-bs-toggle='modal' data-bs-target='#room-update-modal' attr='delete' data-bs-whatever="${d.ROOM_UUID}"><span class='tooltiptextcss'>Delete</span></i>&nbsp;&nbsp;&nbsp;<i style='color: green;' class='tooltipcss bi bi-pencil-square' data-bs-toggle='modal' data-bs-target='#room-update-modal' attr='update' data-bs-whatever="${d.ROOM_UUID}"><span class='tooltiptextcss'>Update</span></i>
  `;
  let localSg = "-"
  if(d.LAST_DATA_TS){
    localSg = getTimezoneOffset(d.LAST_DATA_TS)
    localSg = moment(localSg).fromNow()
  }
    
  
  rowS.innerHTML = `   
      <div class="ag-courses-item_date-box">
        <span class='ag-courses-item_date'><strong>${d.INFO}</strong></span>
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
        Last data received: <span class='ag-courses-item_date'>${localSg}</span>
      </div>
    `;

  // aTag.appendChild(secDiv);
  aTag.appendChild(thirdDiv);
  aTag.appendChild(rowS);
  // aTag.appendChild(fifthDiv);
  // aTag.appendChild(sixthDiv);

  firDiv.appendChild(aTag);
  firDiv.appendChild(secDiv);
  // firDiv.appendChild(`<button type='button'>edit</button><button type='button'>delete</button>`)
  indiCard.appendChild(firDiv);
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

  // if(imgUpload.value == ""){
  //   imgUploadError.innerText = "Please upload room image!"
  //   imgUpload.style.border = borderRed
  // }

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
        location.reload();
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
    })
    .catch((error) => {
      console.error("Error:", error);
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
  // imgUploadError.innerHTML = "";
  // imgUpload.style.border = borderOri;

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
        location.reload();
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
    })
    .catch((error) => {
      console.error("Error:", error);
      updateRoomSubmitBtn.disabled = false;
    });
}

async function deletRoom() {
  Rdata = {
    ROOM_UUID: updateRoomSubmitBtn.getAttribute("uuid"),
    IMAGE_NAME: updateRoomSubmitBtn.getAttribute("img"),
  };
  Object.assign(Rdata, RequestData());
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
        location.reload();
      }
    })
    .catch((error) => {
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
          updateRoomSubmitBtn.innerText = "update";
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
          updateRoomSubmitBtn.innerText = "delete";
          updateRoomSubmitBtn.removeAttribute("onclick");
          updateRoomSubmitBtn.setAttribute("uuid", d.ROOM_UUID);
          updateRoomSubmitBtn.setAttribute("img", d.IMAGE_NAME);
          updateRoomSubmitBtn.setAttribute("onclick", "deletRoom()");
          updateRoomFormTitle.innerText = "Delete Room";
          deleteRoomP.innerHTML = `Are you sure you want to delete, <strong>${d.ROOM_NAME}</strong>?`;
        }
      });
    })
    .catch((error) => {
      console.error("Error:", error);
    });
});