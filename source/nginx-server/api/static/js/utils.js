const host = "http://143.198.199.16:5000";
const loginPage = `${host}/api/login`;
const borderOri = "1px solid #ced4da";
const borderRed = "1px solid red";
const saveDevicesId = document.getElementById('save-devices-id')
const usersManagementId = document.getElementById('users-management-id')
const loginId = document.getElementById('login-id')
const logoutId = document.getElementById('logout-id')
const wallType = 1
const ceilType = 2
const vitalType = 3
const brightGreen = "#32d616"
const brightRed = "#eb0a0a"
const skyBlue = "#0360f2"
const brightOrange = "#fa9302"
// popup message modal
const popupMessageTitle = document.getElementById("popupMessageTitle")
const popupMessageBody = document.getElementById("popupMessageBody")
const localDate = new Date()
const localGMTVal = Math.abs(localDate.getTimezoneOffset() * 60 * 1000)
// console.log(localGMTVal)

const loadingOverlay = document.getElementById('loading-overlay')

if(checkLogin()){
  loginId.style.display = 'none'
} else {
  logoutId.style.display = 'none'
  window.location = loginPage
}

const currentURL = window.location.href;
if (currentURL == `${host}/`){
  document.getElementById('home-id').classList.add("active")
}else if (currentURL == `${host}/usersManagement`){
  document.getElementById('users-management-id').classList.add("active")
}else if (currentURL == `${host}/saveDevice`){
  document.getElementById('save-devices-id').classList.add("active")
}

if(checkAdmin()){
  usersManagementId.style.display = 'block'
  saveDevicesId.style.display = 'block'
}

setInterval(() => {
  if(checkLogin()){
    loginId.style.display = 'none'
  } else {
    logoutId.style.display = 'none'
    window.location = loginPage
  }
}, 15000)

function getTimezoneOffset(dt) {
  function z(n){return (n<10? '0' : '') + n}
  var offset = new Date().getTimezoneOffset();
  var sign = offset < 0? '+' : '-';
  offset = Math.abs(offset);
  // return sign + z(offset/60 | 0) + z(offset%60);
  da = new Date(dt)
  let result
  if(sign == "+"){
    result = da.setHours(da.getHours() - parseInt(z(offset/60 | 0)))
    result = da.setMinutes(da.getMinutes() - parseInt(z(offset%60)))
  } else {
    result = da.setHours(da.getHours() + parseInt(z(offset/60 | 0)))
    result = da.setMinutes(da.getMinutes() + parseInt(z(offset%60)))
  }
  return result
}


function gcd(a, b){
  return (b == 0) ? a : gcd (b, a%b);
}

function highlightFor(id,color,seconds){
  var element = document.getElementById(id)
  var origcolor = element.style.backgroundColor
  element.style.backgroundColor = color;
  var t = setTimeout(function(){
     element.style.backgroundColor = origcolor;
  },(seconds*1000));
}

function getMAC(d){
  let macArr = []  
  if(d.MAC != null){
    let macA = d.MAC.split("'")
    for(var i=0; i<macA.length; i++){
      if(macA[i].length == 12){
        macArr.push(macA[i])
      }
    }
  }
  return macArr
}

function getCutTimeWithMilli(d){
  var today = new Date();
  var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
  var timeMili = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds() + "." + today.getMilliseconds();
  var timeMin = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
  var dateTime = date+' '+timeMin;
  if(d == "Miliseconds"){
    return timeMili
  }
  if(d == "Minute"){
    return timeMin
  }
  if(d == "date"){
    return date
  }
  if(d == "dateTime"){
    return dateTime
  }
  // return time
}



function checkStatus(num){
  if(num == 0){
    return "Register"
  } else if(num == 1){
    return "Add Password"
  } else if(num == 2){
    return "Login"
  } else if(num == 3){
    return "Logout"
  } else {
    return ""
  }
}

async function logout(){
  let response = [];
  let Rdata = RequestData();
  showLoading()
  await fetch(`${host}/api/logout`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(Rdata),
  })
    .then((response) => response.json())
    .then((data) => {
      // console.log(data)
      if(data.DATA){
        eraseCookie('Username')
        eraseCookie('TYPE')
        eraseCookie('CODE')
        eraseCookie('ID')
        window.location.href = loginPage
      }
      hideLoading()
    })
    .catch((error) => {
      hideLoading()
      console.error("Error:", error);
    });
  return response;
}

async function API_Call(time, deviceId, location) {
  let response = [];
  let Rdata = {};
  action = "events";
  Rdata = {
    TIME: time,
    DEVICEID: deviceId,
    // LOCATION: location,
  };
  showLoading()
  await fetch(`${host}/getData`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(Rdata),
  })
    .then((response) => response.json())
    .then((data) => {
      // console.log(data)
      // if(data["CODE"] == 0)
      // response = data["DATA"];
      response = data;
      hideLoading()
    })
    .catch((error) => {
      hideLoading()
      showToast("Error"+String(error), false);
      console.error("Error:", error);
    });
  // console.log(response);
  return response;
}

function isWhatPercentOf(x, y) {
  return (x / y) * 100;
}

const validateEmail = (email) => {
  return email.match(
    /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
  );
};

function hash(string) {
  const utf8 = new TextEncoder().encode(string);
  return crypto.subtle.digest("SHA-256", utf8).then((hashBuffer) => {
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray
      .map((bytes) => bytes.toString(16).padStart(2, "0"))
      .join("");
    return hashHex;
  });
}

/**
 * Secure Hash Algorithm (SHA256)
 * http://www.webtoolkit.info/
 * Original code by Angel Marin, Paul Johnston
 **/

function SHA256(s) {
  var chrsz = 8;
  var hexcase = 0;

  function safe_add(x, y) {
    var lsw = (x & 0xffff) + (y & 0xffff);
    var msw = (x >> 16) + (y >> 16) + (lsw >> 16);
    return (msw << 16) | (lsw & 0xffff);
  }

  function S(X, n) {
    return (X >>> n) | (X << (32 - n));
  }
  function R(X, n) {
    return X >>> n;
  }
  function Ch(x, y, z) {
    return (x & y) ^ (~x & z);
  }
  function Maj(x, y, z) {
    return (x & y) ^ (x & z) ^ (y & z);
  }
  function Sigma0256(x) {
    return S(x, 2) ^ S(x, 13) ^ S(x, 22);
  }
  function Sigma1256(x) {
    return S(x, 6) ^ S(x, 11) ^ S(x, 25);
  }
  function Gamma0256(x) {
    return S(x, 7) ^ S(x, 18) ^ R(x, 3);
  }
  function Gamma1256(x) {
    return S(x, 17) ^ S(x, 19) ^ R(x, 10);
  }

  function core_sha256(m, l) {
    var K = new Array(
      0x428a2f98,
      0x71374491,
      0xb5c0fbcf,
      0xe9b5dba5,
      0x3956c25b,
      0x59f111f1,
      0x923f82a4,
      0xab1c5ed5,
      0xd807aa98,
      0x12835b01,
      0x243185be,
      0x550c7dc3,
      0x72be5d74,
      0x80deb1fe,
      0x9bdc06a7,
      0xc19bf174,
      0xe49b69c1,
      0xefbe4786,
      0xfc19dc6,
      0x240ca1cc,
      0x2de92c6f,
      0x4a7484aa,
      0x5cb0a9dc,
      0x76f988da,
      0x983e5152,
      0xa831c66d,
      0xb00327c8,
      0xbf597fc7,
      0xc6e00bf3,
      0xd5a79147,
      0x6ca6351,
      0x14292967,
      0x27b70a85,
      0x2e1b2138,
      0x4d2c6dfc,
      0x53380d13,
      0x650a7354,
      0x766a0abb,
      0x81c2c92e,
      0x92722c85,
      0xa2bfe8a1,
      0xa81a664b,
      0xc24b8b70,
      0xc76c51a3,
      0xd192e819,
      0xd6990624,
      0xf40e3585,
      0x106aa070,
      0x19a4c116,
      0x1e376c08,
      0x2748774c,
      0x34b0bcb5,
      0x391c0cb3,
      0x4ed8aa4a,
      0x5b9cca4f,
      0x682e6ff3,
      0x748f82ee,
      0x78a5636f,
      0x84c87814,
      0x8cc70208,
      0x90befffa,
      0xa4506ceb,
      0xbef9a3f7,
      0xc67178f2
    );
    var HASH = new Array(
      0x6a09e667,
      0xbb67ae85,
      0x3c6ef372,
      0xa54ff53a,
      0x510e527f,
      0x9b05688c,
      0x1f83d9ab,
      0x5be0cd19
    );
    var W = new Array(64);
    var a, b, c, d, e, f, g, h, i, j;
    var T1, T2;

    m[l >> 5] |= 0x80 << (24 - (l % 32));
    m[(((l + 64) >> 9) << 4) + 15] = l;

    for (var i = 0; i < m.length; i += 16) {
      a = HASH[0];
      b = HASH[1];
      c = HASH[2];
      d = HASH[3];
      e = HASH[4];
      f = HASH[5];
      g = HASH[6];
      h = HASH[7];

      for (var j = 0; j < 64; j++) {
        if (j < 16) W[j] = m[j + i];
        else
          W[j] = safe_add(
            safe_add(
              safe_add(Gamma1256(W[j - 2]), W[j - 7]),
              Gamma0256(W[j - 15])
            ),
            W[j - 16]
          );

        T1 = safe_add(
          safe_add(safe_add(safe_add(h, Sigma1256(e)), Ch(e, f, g)), K[j]),
          W[j]
        );
        T2 = safe_add(Sigma0256(a), Maj(a, b, c));

        h = g;
        g = f;
        f = e;
        e = safe_add(d, T1);
        d = c;
        c = b;
        b = a;
        a = safe_add(T1, T2);
      }

      HASH[0] = safe_add(a, HASH[0]);
      HASH[1] = safe_add(b, HASH[1]);
      HASH[2] = safe_add(c, HASH[2]);
      HASH[3] = safe_add(d, HASH[3]);
      HASH[4] = safe_add(e, HASH[4]);
      HASH[5] = safe_add(f, HASH[5]);
      HASH[6] = safe_add(g, HASH[6]);
      HASH[7] = safe_add(h, HASH[7]);
    }
    return HASH;
  }

  function str2binb(str) {
    var bin = Array();
    var mask = (1 << chrsz) - 1;
    for (var i = 0; i < str.length * chrsz; i += chrsz) {
      bin[i >> 5] |= (str.charCodeAt(i / chrsz) & mask) << (24 - (i % 32));
    }
    return bin;
  }

  function Utf8Encode(string) {
    string = string.replace(/\r\n/g, "\n");
    var utftext = "";

    for (var n = 0; n < string.length; n++) {
      var c = string.charCodeAt(n);

      if (c < 128) {
        utftext += String.fromCharCode(c);
      } else if (c > 127 && c < 2048) {
        utftext += String.fromCharCode((c >> 6) | 192);
        utftext += String.fromCharCode((c & 63) | 128);
      } else {
        utftext += String.fromCharCode((c >> 12) | 224);
        utftext += String.fromCharCode(((c >> 6) & 63) | 128);
        utftext += String.fromCharCode((c & 63) | 128);
      }
    }

    return utftext;
  }

  function binb2hex(binarray) {
    var hex_tab = hexcase ? "0123456789ABCDEF" : "0123456789abcdef";
    var str = "";
    for (var i = 0; i < binarray.length * 4; i++) {
      str +=
        hex_tab.charAt((binarray[i >> 2] >> ((3 - (i % 4)) * 8 + 4)) & 0xf) +
        hex_tab.charAt((binarray[i >> 2] >> ((3 - (i % 4)) * 8)) & 0xf);
    }
    return str;
  }

  s = Utf8Encode(s);
  return binb2hex(core_sha256(str2binb(s), s.length * chrsz));
}

// set cookie in browser
function setCookie(name,value,days) {
  var expires = "";
  console.log(name, value, days)
  if (days) {
      var date = new Date();
      date.setTime(date.getTime() + (days*24*60*60*1000));
      expires = "; expires=" + date.toUTCString();
  }
  console.log(expires)
  document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}

// get cookie from browser
function getCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(';');
  for(var i=0;i < ca.length;i++) {
      var c = ca[i];
      while (c.charAt(0)==' ') c = c.substring(1,c.length);
      if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
  }
  return null;
}

function RequestData(){
  return {
      Username: getCookie("Username"),
      CODE: getCookie("CODE"),
      TYPE: getCookie("TYPE"),
      ID: getCookie('ID')
  }
}

// erase cookie from browser
function eraseCookie(name) {   
  document.cookie = name +'=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
}

// check login or not
function checkLogin() {
  let user = getCookie("Username");
  let token = getCookie("CODE");
  let type = getCookie("TYPE");
  let id = getCookie("ID");
  // console.log("user " + user)
  if (user == null || token == null || type == null || id == null) {
  //   alert("Welcome again " + user);
      // console.log("checked")
      // window.location.href = loginPage
      return false
  } else {
      return true
  }
}

// check Admin
function checkAdmin(){
  let type = getCookie("TYPE");
  if (type == 1) {
        return true
    } else {
        return false
    }
}

// remove child Element
function removeChildEl(parentId){
  let parent = document.getElementById(parentId)
  while(parent.hasChildNodes()){
    parent.removeChild(parent.firstChild)
  }
}


// Image Upload
// var imgByteArray = []
var fileData = new FormData()
var fileLink;
function load_file(id, name, fileError, link){
  // console.log(id, name, fileError)
  // var reader= new FileReader();
  var sample_image = document.getElementById(id);
  fileName = sample_image.files[0].name;
  // // var file=files[0];
  // fileData.append('fac-add-image', files[0])

  upload_image(sample_image.files[0], name, fileError, link);
}

// const sample_image = document.getElementsByName('fac-add-image')[0];

// sample_image.addEventListener('change', () => {

//   upload_image(sample_image.files[0]);

// });

const upload_image = (file, Elname, fileError, imgLink) => {
  document.getElementById(fileError).innerHTML = "";
	if(!['image/jpeg', 'image/png'].includes(file.type))
	{
		document.getElementById(fileError).innerHTML = '<div class="alert alert-danger mt-1">Only .jpg and .png image are allowed</div>';

		document.getElementsByName(Elname)[0].value = '';

		return;
	}

	if(file.size > 2 * 1024 * 1024)
	{
		document.getElementById(fileError).innerHTML = '<div class="alert alert-danger">File must be less than 2 MB</div>';

		document.getElementsByName(Elname)[0].value = '';

		return;
	}

	const form_data = new FormData();

	form_data.append(Elname, file);

  showLoading()
	fetch(`${host}/api/uploadImg`, {

		method:"POST",

    	body:form_data

	}).then(function(response){
    hideLoading()
		return response.json();

	}).then(function(responseData){
		document.getElementById(fileError).innerHTML = '<div class="alert alert-success">Image Uploaded Successfully</div> <img src="'+host+'/static/uploads/'+responseData.image_source+'" id="uploaded-img" img-name='+responseData.image_source+' class="img-thumbnail centerImg" />';
    
    fileLink = `${host}/static/uploads/${responseData.image_source}`
    
		document.getElementsByName(Elname)[0].value = '';
    hideLoading()
	});

}

function secondsToHours(seconds){
  var seconds = Number(seconds);
  var h = Math.round(seconds / (3600)) 
  // var hDisplay = h > 0 ? h + (h == 1 ? " hr" : " hrs") : "0 hr";
  return h
}

function secondsToMin(seconds){
  var seconds = Number(seconds);
  var m = Math.round(seconds / (60)) 
  // var hDisplay = h > 0 ? h + (h == 1 ? " hr" : " hrs") : "0 hr";
  return m
}

function secondsToDhms(seconds) {
  seconds = Number(seconds);
  var d = Math.floor(seconds / (3600*24));
  var h = Math.floor(seconds % (3600*24) / 3600);
  var m = Math.floor(seconds % 3600 / 60);
  var s = Math.floor(seconds % 60);
  
  // var dDisplay = d > 0 ? d + (d == 1 ? " day, " : " days, ") : "";
  // var hDisplay = h > 0 ? h + (h == 1 ? " hour, " : " hours, ") : "";
  // var mDisplay = m > 0 ? m + (m == 1 ? " minute, " : " minutes, ") : "";
  // var sDisplay = s > 0 ? s + (s == 1 ? " second" : " seconds") : "";
  var dDisplay = d > 0 ? d + (" D, ") : "";
  var hDisplay = h > 0 ? h + (" H, ") : "";
  var mDisplay = m > 0 ? m + (" M, ") : "";
  var sDisplay = s > 0 ? s + (" S") : "";
  return dDisplay + hDisplay + mDisplay + sDisplay;
}

function showLoading(){
  loadingOverlay.style.display = 'block'
}

function hideLoading(){
  loadingOverlay.style.display = 'none'
}



function showToast(message, success) {
  var toastContainer = document.getElementById('toastContainer');

  // Create a new Toast element
  var newToast = document.createElement('div');
  newToast.className = 'toast mb-2'; // Remove "hide" class to make it appear with animation
  var iconClass = success ? 'bi bi-check-circle' : 'bi bi-x-circle'; // Icon based on success
  var backgroundColor = success ? 'bg-success' : 'bg-danger'; // Background color based on success
  newToast.innerHTML = `
    <div class="toast-header ${backgroundColor}">
      <i class="${iconClass} text-light me-2"></i>
      <strong class="me-auto text-light">${success ? 'Success' : 'Failure'}</strong>
      <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
    <div class="toast-body">
      ${message}
    </div>
  `;
  
  // Append the new Toast to the container
  toastContainer.appendChild(newToast);

  // Create a new Toast instance
  var dynamicToast = new bootstrap.Toast(newToast);

  // Show the Toast
  dynamicToast.show();

  // Automatically remove the Toast element after it has been hidden
  dynamicToast._element.addEventListener('hidden.bs.toast', function () {
    newToast.remove();
  });
}