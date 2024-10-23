const roomName = document.getElementById("room-name");

const imageContainer = document.getElementById('image-container');
const image = document.getElementById('image');
const confirmButton = document.getElementById('confirm-selection');
const clearButton = document.getElementById('clear-all');
let isSelecting = false;
let startX, startY;
let selectedAreas = []; // Store selected areas
let x_range = 5; // Define your x_range
let y_range = 5; // Define your y_range

imageContainer.addEventListener('mousedown', (e) => {
    isSelecting = true;
    startX = Math.max(0, e.clientX - imageContainer.offsetLeft);
    startY = Math.max(0, e.clientY - imageContainer.offsetTop);
    const selectionRectangle = createSelectionRectangle(startX, startY, 0, 0);
    selectionRectangle.style.backgroundColor = 'rgba(0, 0, 255, 0.3)'; // Blue
    selectionRectangle.classList.add('selection-rectangle');
    e.preventDefault();
});

document.addEventListener('mousemove', (e) => {
    if (!isSelecting) return;

    const currentX = Math.min(imageContainer.clientWidth, e.clientX - imageContainer.offsetLeft);
    const currentY = Math.max(0, Math.min(imageContainer.clientHeight, e.clientY - imageContainer.offsetTop)); // Ensure yStart is not negative
    const width = Math.abs(currentX - startX);
    const height = Math.abs(currentY - startY);
    const left = Math.min(startX, currentX);
    const top = Math.min(startY, currentY);

    const selectionRectangles = document.querySelectorAll('.selection-rectangle');
    const selectionRectangle = selectionRectangles[selectionRectangles.length - 1];

    selectionRectangle.style.width = width + 'px';
    selectionRectangle.style.height = height + 'px';
    selectionRectangle.style.left = left + 'px';
    selectionRectangle.style.top = top + 'px';
});

document.addEventListener('mouseup', () => {
    if (isSelecting) {
        isSelecting = false;
    }
});

confirmButton.addEventListener('click', () => {
    // Change the class of selected areas to 'confirmed-rectangle' (blue)
    const selectionRectangles = document.querySelectorAll('.selection-rectangle');
    selectionRectangles.forEach((rectangle) => {
        rectangle.classList.remove('selection-rectangle');
        rectangle.classList.add('confirmed-rectangle');

        // Calculate and save the coordinates based on x_range and y_range
        const X_START = parseFloat(((parseInt(rectangle.style.left) / imageContainer.clientWidth) * x_range).toFixed(2));
        const X_END = parseFloat((((parseInt(rectangle.style.left) + parseInt(rectangle.style.width)) / imageContainer.clientWidth) * x_range).toFixed(2));
        const Y_START = parseFloat((y_range - ((parseInt(rectangle.style.top) + parseInt(rectangle.style.height)) / imageContainer.clientHeight) * y_range).toFixed(2));
        const Y_END = parseFloat((y_range - ((parseInt(rectangle.style.top) / imageContainer.clientHeight) * y_range)).toFixed(2));
        selectedAreas.push({ X_START, X_END, Y_START, Y_END });
    });

    console.log(selectedAreas);
    let body = Object.assign({
        room_id:roomData.ID,
        data:selectedAreas
    }, RequestData());
    fetch(`${host}/api/updateFilterLocationHistory`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      }).then((response) => response.json()).then((data) => {

        // Initialize by drawing preselected areas
        console.log(data)
        showToast("Filtering updated!", true);
        hideLoading()
      })
});

// Function to create a selection rectangle
function createSelectionRectangle(left, top, width, height) {
    const selectionRectangle = document.createElement('div');
    selectionRectangle.style.position = 'absolute';
    selectionRectangle.style.left = left + 'px';
    selectionRectangle.style.top = top + 'px';
    selectionRectangle.style.width = width + 'px';
    selectionRectangle.style.height = height + 'px';
    imageContainer.appendChild(selectionRectangle);
    return selectionRectangle;
}

function drawPreselectedAreas(preselectedAreas) {
    preselectedAreas.forEach(area => {
        const left = (area.X_START / x_range) * imageContainer.clientWidth;
        const top = imageContainer.clientHeight - ((area.Y_END / y_range) * imageContainer.clientHeight);
        const width = ((area.X_END - area.X_START) / x_range) * imageContainer.clientWidth;
        const height = ((area.Y_END - area.Y_START) / y_range) * imageContainer.clientHeight;
        const selectionRectangle = createSelectionRectangle(left, top, width, height);
        selectionRectangle.classList.add('confirmed-rectangle');
        selectedAreas.push(area)
    });
}

clearButton.addEventListener('click', () => {
    const confirmedRectangles = document.querySelectorAll('.confirmed-rectangle');
    confirmedRectangles.forEach(rectangle => {
        rectangle.remove();
    });
    selectedAreas = [];
});

roomI = window.location.href.split("=")[1];

roomD = {
    ROOM_UUID: roomI,
};

let roomData = {}

Object.assign(roomD, RequestData());
getFilterLocationHistoryData()

image.onload = () => {
    let body2 = Object.assign({
        room_id:roomData.ID
    }, RequestData());
    fetch(`${host}/api/getFilterLocationHistory`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body2),
      }).then((response2) => response2.json()).then((data2) => {

        // Initialize by drawing preselected areas
        drawPreselectedAreas(data2.DATA);

        hideLoading()
      })
};

function getFilterLocationHistoryData(){

    let body1 = Object.assign({}, roomD);
    showLoading()
    fetch(`${host}/api/getRoomDetail`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body1),
      }).then((response) => response.json()).then((data) => {

        roomData = data.DATA[0]
        console.log(roomData)
        image.src = `${host}/static/uploads/` + roomData.IMAGE_NAME;
        roomName.innerText = `${roomData.ROOM_NAME}@${roomData.ROOM_LOC}`
        x_range = roomData.ROOM_X
        y_range = roomData.ROOM_Y

        
      })
}