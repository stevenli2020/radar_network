const indiCard = document.getElementById("ag-courses_box");

// add room details form
const addRoomRow = document.getElementById("add-room-button")
const addRoomName = document.getElementById("room-add-name")
const addRoomNameError = document.getElementById("room-add-name-error")
const addRoomNameX = document.getElementById("room-x-add")
const addRoomNameXError = document.getElementById("room-x-add-error")
const addRoomNameY = document.getElementById("room-y-add")
const addRoomNameYError = document.getElementById("room-y-add-error")
const posDetDev = document.getElementById("pos-detect-dev")
const posDetDevSugg = document.getElementById("pos-detect-dev-suggest")
const posDetDevError = document.getElementById("pos-detect-dev-error")
const posDetDevX = document.getElementById("pos-detect-dev-x")
const posDetDevXError = document.getElementById("pos-detect-dev-x-error")
const posDetDevY = document.getElementById("pos-detect-dev-y")
const posDetDevYError = document.getElementById("pos-detect-dev-y-error")
const vitalDetDev = document.getElementById("vital-detect-dev")
const vitalDetDevSugg = document.getElementById("vital-detect-dev-suggest")
const vitalDetDevError = document.getElementById("vital-detect-dev-error")
const vitalDetDevX = document.getElementById("vital-detect-dev-x")
const vitalDetDevXError = document.getElementById("vital-detect-dev-x-error")
const vitalDetDevY = document.getElementById("vital-detect-dev-y")
const vitalDetDevYError = document.getElementById("vital-detect-dev-y-error")
const imgUpload = document.getElementById("add-room-img-upload")
const imgUploadError = document.getElementById("addRoomImgUploadError")
const addRoomSubmitBtn = document.getElementById("room-submit-btn")

if(!checkAdmin()){
  addRoomRow.style.display = 'none'
}

getDeviceStatus()
setInterval(getDeviceStatus, 5000, 5)

function getDeviceStatus(t=1){
  fetch(`${host}/getRegDevices`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(RequestData()),
  })
    .then((response) => response.json())
    .then((data) => {
      // console.log(data);
      if (data.DATA) {
        data.DATA.forEach((d) => {
          if ("NAME" in d) {
            if(t == 1)
              addCard(d)
            else{
              updateCard(d)
            }
          } else if ("USER_ID" in d) {
            mac = getMAC(d)
            mac.forEach(m => {
              if(t == 1)
                getSpecificDevice(m)
              else
                getSpecificDevice(m, 5)
            })          
          }
        });
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}



async function getSpecificDevice(mac, t=1){
  rData = {
    MAC: mac
  }
  Object.assign(rData, RequestData())
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
        data.DATA.forEach(d => {
          if(t == 1)
            addCard(d)
          else{
            updateCard(d)
          }
            
        })
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

function updateCard(d){
  let updateStatus = document.getElementById(d.Id+"-status")
  let updateTime = document.getElementById(d.Id+"-timestamp")
  updateStatus.innerHTML = `Status: <span class='ag-courses-item_date'>${d.STATUS}</span>`;
  updateTime.innerHTML = `Time: <span class='ag-courses-item_date'>${d.TIMESTAMP.substring(
    0,
    d.TIMESTAMP.length - 3
  )}</span>`;
  // highlightFor(d.Id+"-status", 'yellow', 1);
  // highlightFor(d.Id+"-timestamp", 'yellow', 1);
}

function addCard(d) {
  let firDiv = document.createElement("div");
  let aTag = document.createElement("a");
  let secDiv = document.createElement("div");
  let thirdDiv = document.createElement("div");
  let fourthDiv = document.createElement("div");
  let fifthDiv = document.createElement("div");
  let sixthDiv = document.createElement("div");
  firDiv.setAttribute("class", "ag-courses_item");
  aTag.setAttribute("href", `/Detail?mac=${d.MAC}`);
  aTag.setAttribute("class", "ag-courses-item_link");
  secDiv.setAttribute("class", "ag-courses-item_bg");
  thirdDiv.setAttribute("class", "ag-courses-item_title");
  thirdDiv.innerText = d.NAME;
  fourthDiv.setAttribute("class", "ag-courses-item_date-box");
  fourthDiv.setAttribute("id", d.Id+"-status");
  fourthDiv.innerHTML = `Status: <span class='ag-courses-item_date'>${d.STATUS}</span>`;
  fifthDiv.setAttribute("class", "ag-courses-item_date-box");
  fifthDiv.setAttribute("id", d.Id+"-timestamp");
  fifthDiv.innerHTML = `Time: <span class='ag-courses-item_date'>${d.TIMESTAMP.substring(
    0,
    d.TIMESTAMP.length - 3
  )}</span>`;
  sixthDiv.setAttribute("class", "ag-courses-item_date-box");
  sixthDiv.innerHTML = `Mac: <span class='ag-courses-item_date'>${d.MAC}</span>`;
  aTag.appendChild(secDiv);
  aTag.appendChild(thirdDiv);
  aTag.appendChild(fourthDiv);
  aTag.appendChild(fifthDiv);
  aTag.appendChild(sixthDiv);
  firDiv.appendChild(aTag);
  indiCard.appendChild(firDiv);
}

async function addNewRoom(){
  addRoomSubmitBtn.disabled = true
  addRoomNameError.innerHTML = "";
  addRoomName.style.border = borderOri;
  addRoomNameXError.innerHTML = "";
  addRoomNameX.style.border = borderOri;
  addRoomNameYError.innerHTML = "";
  addRoomNameY.style.border = borderOri;
  posDetDevError.innerHTML = "";
  posDetDev.style.border = borderOri;
  posDetDevXError.innerHTML = "";
  posDetDevX.style.border = borderOri;
  posDetDevYError.innerHTML = "";
  posDetDevY.style.border = borderOri;
  vitalDetDevError.innerHTML = "";
  vitalDetDev.style.border = borderOri;
  vitalDetDevXError.innerHTML = "";
  vitalDetDevX.style.border = borderOri;
  vitalDetDevYError.innerHTML = "";
  vitalDetDevY.style.border = borderOri;
  // imgUploadError.innerHTML = "";
  // imgUpload.style.border = borderOri;

  if(addRoomName.value == ""){
    addRoomNameError.innerText = "Room name is empty!"
    addRoomName.style.border = borderRed
  } else {
    if(addRoomNameX.value == ""){
      addRoomNameXError.innerText = "Please add value!"
      addRoomNameX.style.border = borderRed
    }
    if(addRoomNameY.value == ""){
      addRoomNameYError.innerText = "Please add value!"
      addRoomNameY.style.border = borderRed
    }
  }

  if(addRoomNameX.value != "" || addRoomNameY.value != ""){
    if(addRoomName.value == ""){
      addRoomNameError.innerText = "Room name is empty!"
      addRoomName.style.border = borderRed
    }
  }

  // if(imgUpload.value == ""){
  //   imgUploadError.innerText = "Please upload room image!"
  //   imgUpload.style.border = borderRed
  // }

  if(vitalDetDev.value == "" && posDetDev.value == ""){
    vitalDetDevError.innerText = "Please add at least one device!"
    posDetDevError.innerText = "Please add at least one device!"
    vitalDetDev.style.border = borderRed
    posDetDev.style.border = borderRed
  }

  if(posDetDevX.value != "" || posDetDevY.value != ""){
    if(posDetDev.value == ""){
      posDetDevError.innerText = "Please add device name!"
      posDetDev.style.border = borderRed
    }
  }

  if(vitalDetDevX.value != "" || vitalDetDevY.value != ""){
    if(vitalDetDev.value == ""){
      vitalDetDevError.innerText = "Please add device name!"
      vitalDetDev.style.border = borderRed
    }
  }

  if(posDetDev.value != ""){
    if(posDetDevX.value == ""){
      posDetDevXError.innerText = "Please add value!"
      posDetDevX.style.border = borderRed
    }
    if(posDetDevY.value == ""){
      posDetDevYError.innerText = "Please add value!"
      posDetDevY.style.border = borderRed
    }
  }

  if(vitalDetDev.value != ""){
    if(vitalDetDevX.value == ""){
      vitalDetDevXError.innerText = "Please add value!"
      vitalDetDevX.style.border = borderRed
    }
    if(vitalDetDevY.value == ""){
      vitalDetDevYError.innerText = "Please add value!"
      vitalDetDevY.style.border = borderRed
    }
  }

  if(addRoomNameError.innerText != "" || addRoomNameXError.innerText != "" || addRoomNameYError.innerText != "" || posDetDevError.innerText != "" || posDetDevXError.innerText != "" || posDetDevYError.innerText != "" || vitalDetDevError.innerText != "" || vitalDetDevXError.innerText != "" || vitalDetDevYError.innerText != ""){
    addRoomSubmitBtn.disabled = false
    return
  }
  
  let RData = {
    ROOM_NAME: addRoomName.value,
    ROOM_X: parseFloat(addRoomNameX.value),
    ROOM_Y: parseFloat(addRoomNameY.value),
    POS_MAC: posDetDev.getAttribute('mac'),
    POS_X: parseFloat(posDetDevX.value),
    POS_Y: parseFloat(posDetDevY.value),
    VITAL_MAC: vitalDetDev.getAttribute("mac"),
    VITAL_X: parseFloat(vitalDetDevX.value),
    VITAL_Y: parseFloat(vitalDetDevY.value),
    IMAGE_NAME: document.querySelector("#uploaded-img").getAttribute('img-name')
  }
  Object.assign(RData, RequestData());
  console.log(RData)
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
      addRoomSubmitBtn.disabled = false
      console.log(data);
      if ("DATA" in data) {
        // console.log(data)
        location.reload()        
      } else {
        if("RoomName" in data.ERROR[0]){
          addRoomNameError.innerText = data.ERROR[0].RoomName
          addRoomName.style.border = borderRed
        }
        if("ROOM_X" in data.ERROR[0]){
          addRoomNameXError.innerText = data.ERROR[0].RoomName
          addRoomNameX.style.border = borderRed
        }
        if("ROOM_Y" in data.ERROR[0]){
          addRoomNameYError.innerText = data.ERROR[0].RoomName
          addRoomNameY.style.border = borderRed
        }
        if("POS_MAC" in data.ERROR[0]){
          posDetDevError.innerText = data.ERROR[0].RoomName
          posDetDev.style.border = borderRed
        }
        if("POS_X" in data.ERROR[0]){
          posDetDevXError.innerText = data.ERROR[0].RoomName
          posDetDevX.style.border = borderRed
        }
        if("POS_Y" in data.ERROR[0]){
          posDetDevYError.innerText = data.ERROR[0].RoomName
          posDetDevY.style.border = borderRed
        }
        if("VITAL_MAC" in data.ERROR[0]){
          vitalDetDevError.innerText = data.ERROR[0].RoomName
          vitalDetDev.style.border = borderRed
        }
        if("VITAL_X" in data.ERROR[0]){
          vitalDetDevXError.innerText = data.ERROR[0].RoomName
          vitalDetDevX.style.border = borderRed
        }
        if("VITAL_Y" in data.ERROR[0]){
          vitalDetDevYError.innerText = data.ERROR[0].RoomName
          vitalDetDevY.style.border = borderRed
        }
        // if("IMAGE_NAME" in data.ERROR[0]){
        //   imgUploadError.innerText = data.ERROR[0].RoomName
        //   imgUpload.style.border = borderRed
        // }
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      addRoomSubmitBtn.disabled = false
    });
}

posDetDev.addEventListener("input", e => {
  if (e.target.value != "") {    
    // posDetDev.setAttribute("uid", "");
    RData = {
      VALUE: e.target.value,
    };
    Object.assign(RData, RequestData());
    fetch(`${host}/api/getDevSuggestion`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(RData),
    })
      .then((response) => response.json())
      .then((data) => {
        removeChildEl("pos-detect-dev-suggest");
        // console.log(data);
        if (data["DATA"].length > 0) {
          // console.log(data)
          data["DATA"].forEach((node) => {
            b = document.createElement("DIV");
            b.innerHTML = node.NAME;
            b.setAttribute("mac", node.MAC)
            b.addEventListener("click", function (e) {
              if (e.target.nodeName == "DIV") {
                removeChildEl("pos-detect-dev-suggest");
                // addSensorName.value = node.NAME;
                posDetDev.value = e.target.innerHTML;
                posDetDev.setAttribute("mac", e.target.getAttribute('mac'));
                // addSensorType.value = node.SENSOR_TYPE;
                posDetDev.style.border = borderOri;
                posDetDevError.innerHTML = "";
              }
            });
            posDetDevSugg.appendChild(b);
          });
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  } else {
    removeChildEl("add-sensor-mac-suggest");
    posDetDev.style.border = borderOri;
    posDetDevError.innerHTML = "";
  }
})

vitalDetDev.addEventListener("input", e => {
  if (e.target.value != "") {    
    RData = {
      VALUE: e.target.value,
    };
    Object.assign(RData, RequestData());
    fetch(`${host}/api/getDevSuggestion`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(RData),
    })
      .then((response) => response.json())
      .then((data) => {
        removeChildEl("vital-detect-dev-suggest");
        // console.log(data);
        if (data["DATA"].length > 0) {
          // console.log(data)
          data["DATA"].forEach((node) => {
            b = document.createElement("DIV");
            b.innerHTML = node.NAME;
            b.setAttribute("mac", node.MAC)
            b.addEventListener("click", function (e) {
              if (e.target.nodeName == "DIV") {
                removeChildEl("vital-detect-dev-suggest");
                vitalDetDev.value = e.target.innerHTML;
                vitalDetDev.setAttribute("mac", e.target.getAttribute('mac'));
                vitalDetDev.style.border = borderOri;
                vitalDetDevError.innerHTML = "";
              }
            });
            vitalDetDevSugg.appendChild(b);
          });
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  } else {
    removeChildEl("add-sensor-mac-suggest");
    vitalDetDev.style.border = borderOri;
    vitalDetDevError.innerHTML = "";
  }
})
