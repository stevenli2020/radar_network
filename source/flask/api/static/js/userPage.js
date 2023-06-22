// add new user var
// const addUsername = document.getElementById("user-data-add-username");
// const addUsernameError = document.getElementById("add-username-error");
// const addFullname = document.getElementById("user-data-add-fullname");
// const addFullnameError = document.getElementById("add-fullname-error");
// const addUserEmail = document.getElementById("user-data-add-email");
// const addUserEmailError = document.getElementById("add-email-error");
// const addUserPhone = document.getElementById("user-data-add-phone");
// const addUserPhoneError = document.getElementById("add-phone-error");
// const addUserType = document.getElementById("user-data-add-type");
// const addUserTypeError = document.getElementById("add-user-type-error");
// const addUserSubmitBtn = document.getElementById("user-data-submit-btn");
// update user
const UserManagementIcon = document.getElementById('user-data-update-modal')
const submitFormBtn = document.getElementById('update-device-register-submit-btn')
const updateUsernameInput = document.getElementById('user-data-update-username')
const updateUsernameInputError = document.getElementById('update-user-data-username-error')
const updateFullnameInput = document.getElementById('user-data-update-fullname')
const updateFullnameInputError = document.getElementById('update-user-data-fullname-error')
const updateEmailInput = document.getElementById('user-data-update-email')
const updateEmailInputError = document.getElementById('update-user-data-email-error')
const updatePhoneInput = document.getElementById('user-data-update-phone')
const updateTypeInput = document.getElementById('user-data-update-type')
const updateTypeInputError = document.getElementById('update-user-data-type-error')
const updateMulSel = document.getElementById('mul-sel')
const para = document.getElementById('parent-mul')
// delete user
// reset password
// admin table
const adminUsersTable = document.getElementById("admin-user-table")
// users table
const usersTable = document.getElementById("user-data-table")



if(!checkLogin()){
  window.location.href = loginPage
}

if(!checkAdmin()){
  window.location.href = host
}

let Rdata = RequestData();
var screenWidth = screen.width;
fetch(`${host}/getAllUsers`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(Rdata),
})
  .then((response) => response.json())
  .then((data) => {
    console.log(data); 
     
    if(data.DATA){
      let tHeadA = document.createElement('thead')
      let tBodyA = document.createElement('tbody')
      let tHeadU = document.createElement('thead')
      let tBodyU = document.createElement('tbody')
      // console.log(screenWidth)
      if(screenWidth <= 415){
        removeChildEl("admin-user-table")        
        removeChildEl("user-data-table")        
        tHeadA.innerHTML = `<tr><th>Id</th><th>Login Name</th><th>Email</th><th>Status</th><th>Option</th></tr>`
        tHeadU.innerHTML = `<tr><th>Id</th><th>Login Name</th><th>Email</th><th>Status</th><th>Option</th></tr>`
        adminUsersTable.appendChild(tHeadA)
        adminUsersTable.appendChild(tBodyA)
        adminUsersTable.style.fontSize = "small";
        usersTable.appendChild(tHeadU)
        usersTable.appendChild(tBodyU)
        usersTable.style.fontSize = "small";
      } else if(screenWidth <= 821){
        removeChildEl("admin-user-table")        
        removeChildEl("user-data-table")        
        tHeadA.innerHTML = `<tr><th>Id</th><th>Login Name</th><th>Fullname</th><th>Email</th><th>Phone</th><th>Status</th><th>Option</th></tr>`
        tHeadU.innerHTML = `<tr><th>Id</th><th>Login Name</th><th>Fullname</th><th>Email</th><th>Phone</th><th>Status</th><th>Option</th></tr>`
        adminUsersTable.appendChild(tHeadA)
        adminUsersTable.appendChild(tBodyA)
        adminUsersTable.style.fontSize = "small";
        usersTable.appendChild(tHeadU)
        usersTable.appendChild(tBodyU)
        usersTable.style.fontSize = "small";
      }
      data.DATA.forEach(d => {
        created = String(d.CREATED)
        lastModified = String(d.LAST_UPDATE)
        userStatus = checkStatus(d.STATUS)
        newRow = ''
        if(d.TYPE == 0){   
          let macArr = []  
          if(d.ROOM_NAME != null){
            let macA = []
            if(d.ROOM_NAME.includes(',')){
              macA = d.ROOM_NAME.split(",")              
            } else {
              macA.push(d.ROOM_NAME)
            }            
            for(var i=0; i<macA.length; i++){
              macArr.push(macA[i])
            }
          }
          
          if(screenWidth <= 415){
            newRow = $(
              "<tr><td>"+d.ID+"</td><td>"+d.LOGIN_NAME+"</td><td style='word-break: break-word;'>"+d.EMAIL+"</td><td>"+userStatus+"</td><td><i style='color: green;' class='tooltipcss bi bi-pencil-square' data-bs-toggle='modal'  data-bs-target='#user-data-update-modal' attr='update' data-bs-whatever=" +
              d.ID +
              "><span class='tooltiptextcss'>Update User</span></i>&nbsp;&nbsp;<i style='color: red;' class='bi bi-trash3 tooltipcss' data-bs-toggle='modal'  data-bs-target='#user-data-update-modal' attr='delete' data-bs-whatever=" +
              d.ID +
              "><span class='tooltiptextcss'>Delete User</span></i>&nbsp;&nbsp;<i class='bi bi-envelope tooltipcss' data-bs-toggle='modal'  data-bs-target='#user-data-update-modal' attr='reset' data-bs-whatever=" +
              d.ID +
              "><span class='tooltiptextcss'>Reset Password</span></i></td></tr>"
            )
          } else if (screenWidth <= 821) {
            newRow = $(
              "<tr><td>"+d.ID+"</td><td>"+d.LOGIN_NAME+"</td><td>"+d.FULL_NAME+"</td><td style='word-break: break-word;'>"+d.EMAIL+"</td><td>"+d.PHONE+"</td><td>"+userStatus+"</td><td><i style='color: green;' class='tooltipcss bi bi-pencil-square' data-bs-toggle='modal'  data-bs-target='#user-data-update-modal' attr='update' data-bs-whatever=" +
              d.ID +
              "><span class='tooltiptextcss'>Update User</span></i>&nbsp;&nbsp;<i style='color: red;' class='bi bi-trash3 tooltipcss' data-bs-toggle='modal'  data-bs-target='#user-data-update-modal' attr='delete' data-bs-whatever=" +
              d.ID +
              "><span class='tooltiptextcss'>Delete User</span></i>&nbsp;&nbsp;<i class='bi bi-envelope tooltipcss' data-bs-toggle='modal'  data-bs-target='#user-data-update-modal' attr='reset' data-bs-whatever=" +
              d.ID +
              "><span class='tooltiptextcss'>Reset Password</span></i></td></tr>"
            )
          } else {
            // macArr.map(m => `<strong style="color: #67a9c9;"> ${m}</strong>`)
            newRow = $(
              "<tr><td>"+d.ID+"</td><td>"+d.LOGIN_NAME+"</td><td>"+d.FULL_NAME+"</td><td style='word-break: break-word;'>"+d.EMAIL+"</td><td>"+d.PHONE+"</td><td>"+userStatus+"</td><td style='word-break: break-word;'>"+d.CODE+"</td><td style='word-break: break-word;'>"+created.substring(0, created.length - 3)+"</td><td style='word-break: break-word;color: #67a9c9;font-weight: bold;'>"+d.ROOM_NAME+"</td><td><i style='color: green;' class='tooltipcss bi bi-pencil-square' data-bs-toggle='modal'  data-bs-target='#user-data-update-modal' attr='update' data-bs-whatever=" +
              d.ID +
              "><span class='tooltiptextcss'>Update User</span></i>&nbsp;&nbsp;<i style='color: red;' class='bi bi-trash3 tooltipcss' data-bs-toggle='modal'  data-bs-target='#user-data-update-modal' attr='delete' data-bs-whatever=" +
              d.ID +
              "><span class='tooltiptextcss'>Delete User</span></i>&nbsp;&nbsp;<i class='bi bi-envelope tooltipcss' data-bs-toggle='modal'  data-bs-target='#user-data-update-modal' attr='reset' data-bs-whatever=" +
              d.ID +
              "><span class='tooltiptextcss'>Reset Password</span></i></td></tr>"
            )
          }               
          $("#user-data-table tbody").append(newRow);
        } else {
          if(screenWidth <= 415){
            newRow = $(
              "<tr><td>"+d.ID+"</td><td>"+d.LOGIN_NAME+"</td><td style='word-break: break-word;'>"+d.EMAIL+"</td><td>"+userStatus+"</td><td><i style='color: green;' class='tooltipcss bi bi-pencil-square' data-bs-toggle='modal'  data-bs-target='#user-data-update-modal' attr='update' data-bs-whatever=" +
              d.ID +
              "><span class='tooltiptextcss'>Update User</span></i>&nbsp;&nbsp;<i style='color: red;' class='bi bi-trash3 tooltipcss' data-bs-toggle='modal'  data-bs-target='#user-data-update-modal' attr='delete' data-bs-whatever=" +
              d.ID +
              "><span class='tooltiptextcss'>Delete User</span></i>&nbsp;&nbsp;<i class='bi bi-envelope tooltipcss' data-bs-toggle='modal'  data-bs-target='#user-data-update-modal' attr='reset' data-bs-whatever=" +
              d.ID +
              "><span class='tooltiptextcss'>Reset Password</span></i></td></tr>"
            )
          } else if (screenWidth <= 821) {
            newRow = $(
              "<tr><td>"+d.ID+"</td><td>"+d.LOGIN_NAME+"</td><td>"+d.FULL_NAME+"</td><td style='word-break: break-word;'>"+d.EMAIL+"</td><td>"+d.PHONE+"</td><td>"+userStatus+"</td><td><i style='color: green;' class='tooltipcss bi bi-pencil-square' data-bs-toggle='modal'  data-bs-target='#user-data-update-modal' attr='update' data-bs-whatever=" +
              d.ID +
              "><span class='tooltiptextcss'>Update User</span></i>&nbsp;&nbsp;<i style='color: red;' class='bi bi-trash3 tooltipcss' data-bs-toggle='modal'  data-bs-target='#user-data-update-modal' attr='delete' data-bs-whatever=" +
              d.ID +
              "><span class='tooltiptextcss'>Delete User</span></i>&nbsp;&nbsp;<i class='bi bi-envelope tooltipcss' data-bs-toggle='modal'  data-bs-target='#user-data-update-modal' attr='reset' data-bs-whatever=" +
              d.ID +
              "><span class='tooltiptextcss'>Reset Password</span></i></td></tr>"
            )
          } else {
            newRow = $(
              "<tr><td>"+d.ID+"</td><td>"+d.LOGIN_NAME+"</td><td>"+d.FULL_NAME+"</td><td style='word-break: break-word;'>"+d.EMAIL+"</td><td>"+d.PHONE+"</td><td>"+userStatus+"</td><td style='word-break: break-word;'>"+d.CODE+"</td><td style='word-break: break-word;'>"+created.substring(0, created.length - 3)+"</td><td style='word-break: break-word;'>"+lastModified.substring(0, lastModified.length - 3)+"</td><td><i style='color: green;' class='tooltipcss bi bi-pencil-square' data-bs-toggle='modal'  data-bs-target='#user-data-update-modal' attr='update' data-bs-whatever=" +
              d.ID +
              "><span class='tooltiptextcss'>Update User</span></i>&nbsp;&nbsp;<i style='color: red;' class='bi bi-trash3 tooltipcss' data-bs-toggle='modal'  data-bs-target='#user-data-update-modal' attr='delete' data-bs-whatever=" +
              d.ID +
              "><span class='tooltiptextcss'>Delete User</span></i>&nbsp;&nbsp;<i class='bi bi-envelope tooltipcss' data-bs-toggle='modal'  data-bs-target='#user-data-update-modal' attr='reset' data-bs-whatever=" +
              d.ID +
              "><span class='tooltiptextcss'>Reset Password</span></i></td></tr>"
            )
          }
          $("#admin-user-table tbody").append(newRow);
        }
      })
      $("#admin-user-table").dataTable({
        order: [[0, "desc"]],
      });
      $("#user-data-table").dataTable({
        order: [[0, "desc"]],
      });
    } else {
      $("#admin-user-table").dataTable({
        order: [[0, "desc"]],
      });
      $("#user-data-table").dataTable({
        order: [[0, "desc"]],
      });
    }
  })
  .catch((error) => {
    submitFormBtn.disabled = false
    console.error("Error:", error);
  });

UserManagementIcon.addEventListener('show.bs.modal', async (event) => {
  const button = event.relatedTarget;
  const userId = button.getAttribute('data-bs-whatever')
  const modalAttr = button.getAttribute('attr')
  const modalTitle = document.getElementById('user-data-update-modalLabel')
  const userID = document.getElementById('update-user-data-id')
  // const userCode = document.getElementById('update-user-data-code')
  const userCreated = document.getElementById('update-user-data-created')
  const userLastModifiedTime = document.getElementById('update-user-data-last-modified-time')
  const updateUserForm = document.getElementById('update-user-data-form')    
  const deleteUsername = document.getElementById('delete-user-data-username')
  const deleteFullname = document.getElementById('delete-user-data-fullname')
  const deleteEmail = document.getElementById('delete-user-data-email')
  const deletePhone = document.getElementById('delete-user-data-phone')
  // const deleteType = document.getElementById('delete-user-data-type')
  updateUsernameInput.style.border = borderOri;
  updateUsernameInputError.innerText = "";
  updateFullnameInput.style.border = borderOri;
  updateFullnameInputError.innerText = "";
  updateEmailInput.style.border = borderOri;
  updateEmailInputError.innerText = "";
  updateTypeInput.style.border = borderOri;
  updateTypeInputError.innerText = "";
  if(modalAttr != "add"){
    Rdata = {
      USER_ID: userId
    }
    console.log(userId)
    Object.assign(Rdata, RequestData())
    await fetch(`${host}/getSpecificUser`, {
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
            if(modalAttr != "reset"){
              lastUpdate = String(d["LAST_UPDATE"]);
              createdT = String(d["CREATED"]);
              userID.innerHTML = `ID: <strong>${d.ID}</strong>`;
              // userCode.innerHTML = `Code: <strong>${d.CODE}</strong>`;
              userCreated.innerHTML = `Created Time: <strong>${createdT.substring(
                0,
                createdT.length - 3
              )}</strong>`;
              userLastModifiedTime.innerHTML = `Last Modified Time: <strong>${lastUpdate.substring(
                0,
                lastUpdate.length - 3
              )}</strong>`;
              submitFormBtn.setAttribute("user-id", d.ID);
              submitFormBtn.setAttribute("user-name", d.LOGIN_NAME);
              if (modalAttr == "delete") {
                submitFormBtn.classList.remove("btn-primary");
                submitFormBtn.classList.add("btn-danger");
                submitFormBtn.innerHTML = "Delete";
                updateUserForm.style.display = "none";
                submitFormBtn.removeAttribute("onclick");
                deleteUsername.innerHTML = `Username: <strong>${d.LOGIN_NAME}</strong>`;
                deleteFullname.innerHTML = `Full Name: <strong>${d.FULL_NAME}</strong>`;
                deleteEmail.innerHTML = `Email: <strong>${d.EMAIL}</strong>`;
                deletePhone.innerHTML = `Phone: <strong>${d.PHONE}</strong>`;
                // deleteType.innerHTML = `Type: <strong>${d.TYPE}</strong>`;
                submitFormBtn.setAttribute(
                  "onclick",
                  "deleteUser()"
                );
                modalTitle.innerHTML = "Delete User";
              } else if(modalAttr == "update") {
                if("ROOM_NAME" in d){
                  maC = d.ROOM_NAME?d.ROOM_NAME.split(","):null
                  macA = []
                  if(maC){
                    maC.forEach(m => {
                      macA.push(m)
                      // if(m.length == 12){
                      //   macA.push(m)
                      // }
                    })
                  }
                  
                  removeChildEl('parent-mul')
                  // updateMulSel.remove()
                  const mulLabel = document.createElement('label')
                  const mul = document.createElement('select')
                  mulLabel.setAttribute('for', 'mul-sel')
                  mulLabel.setAttribute('class', 'col-form-label')
                  mulLabel.innerText = 'Assign Room:'
                  mul.setAttribute('id', 'mul-sel')
                  mul.setAttribute('multiple', 'true')
                  mul.setAttribute('data-multi-select-plugin', 'true')
                  para.appendChild(mulLabel)
                  para.appendChild(mul)
                  mulSel(macA)             
                }
                updateUsernameInput.value = d.LOGIN_NAME;
                updateFullnameInput.value = d.FULL_NAME;
                updateEmailInput.value = d.EMAIL;
                updatePhoneInput.value = d.PHONE;
                updateTypeInput.value = d.TYPE;
                submitFormBtn.classList.remove("btn-danger");
                submitFormBtn.classList.add("btn-primary");
                submitFormBtn.innerHTML = "Update";
                updateUserForm.style.display = "";
                submitFormBtn.removeAttribute("onclick");
                deleteUsername.innerText = "";
                deleteFullname.innerText = "";
                deleteEmail.innerText = "";
                deletePhone.innerText = "";
                // deleteType.innerText = "";
                submitFormBtn.setAttribute(
                  "onclick",
                  "updateUserDetail()"
                );
                modalTitle.innerHTML = "Update User Detail";
              }
            } else {
              // userID.style.textAlign = 'center'
              userID.innerHTML = 'Sent reset password link to user email?'
              userCreated.innerHTML = ''
              userLastModifiedTime.innerHTML = ''
              deleteEmail.innerHTML = ''
              deleteFullname.innerHTML = ''
              deletePhone.innerHTML = ''
              deleteUsername.innerHTML = ''
              updateUserForm.style.display = 'none'
              modalTitle.innerHTML = 'Reset User Password'              
              submitFormBtn.setAttribute('user-id', d.ID)
              submitFormBtn.setAttribute('user-name', d.LOGIN_NAME)
              submitFormBtn.setAttribute(
                "onclick",
                "resetUserPassword()"
              );
            }
          });
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  } else {
    userID.innerHTML = ''
    userCreated.innerHTML = ''
    userLastModifiedTime.innerHTML = ''
    deleteEmail.innerHTML = ''
    deleteFullname.innerHTML = ''
    deletePhone.innerHTML = ''
    deleteUsername.innerHTML = ''
    updateUserForm.style.display = ''
    modalTitle.innerHTML = 'Add New User'
    submitFormBtn.innerHTML = "Submit"
    submitFormBtn.setAttribute(
      "onclick",
      "addNewUser()"
    );
  }  
})

async function deleteUser(){
  submitFormBtn.disabled = true
  let Rdata = {
    USER_ID: submitFormBtn.getAttribute('user-id')
  }
  Object.assign(Rdata, RequestData())
  await fetch(`${host}/deleteUser`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(Rdata),
  })
    .then((response) => response.json())
    .then((data) => {
      submitFormBtn.disabled = false
      // console.log(data);
      document.querySelector("#update-user-close-btn").click();
      if(data.DATA){
        popupMessageTitle.innerHTML = "Delete User"
        popupMessageBody.innerHTML = `<p><strong>${submitFormBtn.getAttribute('user-name')}</strong> has been deleted successfully</p>`
        document.querySelector("#popupMessageOpenBtn").click()
        setTimeout(()=>{
          location.reload()
        }, 3000)
        
      } else {
        submitFormBtn.disabled = false
      }
    })
    .catch((error) => {
      submitFormBtn.disabled = false
      console.error("Error:", error);
    });
}

async function updateUserDetail(){
  let roomArr = getMacArr()
  clearFormData()
  if(updateUsernameInputError.innerText != "" || updateFullnameInputError.innerText != "" || updateEmailInputError.innerText != "" || updateTypeInputError.innerText != "") {
    submitFormBtn.disabled = false
    return;
  }
  let Rdata = {
    USER_ID: submitFormBtn.getAttribute('user-id'),
    LOGIN_NAME: updateUsernameInput.value,
    FULL_NAME: updateFullnameInput.value,
    EMAIL: updateEmailInput.value,
    PHONE: updatePhoneInput.value,
    USER_TYPE: updateTypeInput.value,
    ROOM: roomArr
  }
  Object.assign(Rdata, RequestData())
  console.log(Rdata)
  await fetch(`${host}/updateUser`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(Rdata),
  })
    .then((response) => response.json())
    .then((data) => {
      submitFormBtn.disabled = false
      // console.log(data);
      document.querySelector("#update-user-close-btn").click();
      if(data.DATA){
        popupMessageTitle.innerHTML = "Update User"
        popupMessageBody.innerHTML = `<p><strong>${submitFormBtn.getAttribute('user-name')}</strong> has been updated successfully</p>`
        document.querySelector("#popupMessageOpenBtn").click()
        setTimeout(()=>{
          location.reload()
        }, 3000)
      } else {
        submitFormBtn.disabled = false
        if ("Username" in data.ERROR[0]) {
          updateUsernameInput.style.border = borderRed;
          updateUsernameInputError.innerText = data.ERROR[0].Username;
          return;
        }
        if ("Fullname" in data.ERROR[0]) {
          updateFullnameInput.style.border = borderRed;
          updateFullnameInputError.innerText = data.ERROR[0].Fullname;
          return;
        }
        if ("Email" in data.ERROR[0]) {
          updateEmailInput.style.border = borderRed;
          updateEmailInputError.innerText = data.ERROR[0].Email;
          return;
        }
        if ("Type" in data.ERROR[0]) {
          updateTypeInput.style.border = borderRed;
          updateTypeInputError.innerText = data.ERROR[0].Type;
          return;
        }
      }
    })
    .catch((error) => {
      submitFormBtn.disabled = false
      console.error("Error:", error);
    });
}

async function resetUserPassword(){
  submitFormBtn.disabled = true
  let Rdata = {
    USER_ID: submitFormBtn.getAttribute('user-id')
  }
  Object.assign(Rdata, RequestData())
  await fetch(`${host}/api/sentEmail`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(Rdata),
  })
    .then((response) => response.json())
    .then((data) => {
      submitFormBtn.disabled = false
      // console.log(data);
      document.querySelector("#update-user-close-btn").click();
      if(data.DATA){
        popupMessageTitle.innerHTML = "Reset Password"
        popupMessageBody.innerHTML = `<p>Reset password link has been sent to <strong>${submitFormBtn.getAttribute('user-name')}</strong>'s email</p>`
        document.querySelector("#popupMessageOpenBtn").click()
        setTimeout(()=>{
          location.reload()
        }, 3000)
      } else {
        submitFormBtn.disabled = false
      }
    })
    .catch((error) => {
      submitFormBtn.disabled = false
      console.error("Error:", error);
    });
}

function getMacArr(){
  const mulInput = document.getElementById('mul-sel')
  // console.log(mulInput)
  var children = mulInput.children;
  var macArr = []
  for(var i=0; i < children.length; i++){
    if(children[i].hasAttribute('selected')){
      macArr.push(children[i].getAttribute('value'))
    }
  }
  console.log(macArr)
  return macArr
}

async function addNewUser() {
  // console.log(addUsername.value, addFullname.value, addUserEmail.value, addUserPhone.value, addUserType.value, 'condition true')
  let roomArr = getMacArr()
  clearFormData()
  // submitFormBtn.disabled = true
  // updateUsernameInput.style.border = borderOri;
  // updateUsernameInputError.innerText = "";
  // updateFullnameInput.style.border = borderOri;
  // updateFullnameInputError.innerText = "";
  // updateEmailInput.style.border = borderOri;
  // updateEmailInputError.innerText = "";
  // updateTypeInput.style.border = borderOri;
  // updateTypeInputError.innerText = "";
  // if (addUsername.value == "") {
  //   addUsername.style.border = borderRed;
  //   addUsernameError.innerText = "Username is Empty!";
  // }
  // if (addFullname.value == "") {
  //   addFullname.style.border = borderRed;
  //   addFullnameError.innerText = "Full name is Empty!";
  // }
  // if (addUserEmail.value == "") {
  //   addUserEmail.style.border = borderRed;
  //   addUserEmailError.innerText = "Email is Empty!";
  // } else {
  //   if (!validateEmail(addUserEmail.value)) {
  //     addUserEmail.style.border = borderRed;
  //     addUserEmailError.innerText = "Email address is incorrect!";
  //   }
  // }
  // if (addUserType.value == "-1") {
  //   addUserType.style.border = borderRed;
  //   addUserTypeError.innerText = "Please Select!";
  // }
  // if(addUsernameError.innerText != "" || addFullnameError.innerText != "" || addUserEmailError.innerText != "" || addUserTypeError.innerText != "") {
  //   addUserSubmitBtn.disabled = false
  //   return;
  // }
  if(updateUsernameInputError.innerText != "" || updateFullnameInputError.innerText != "" || updateEmailInputError.innerText != "" || updateTypeInputError.innerText != "") {
    submitFormBtn.disabled = false
    return;
  }
  let FData = {
    LOGIN_NAME: updateUsernameInput.value,
    FULL_NAME: updateFullnameInput.value,
    EMAIL: updateEmailInput.value,
    PHONE: updatePhoneInput.value,
    USER_TYPE: updateTypeInput.value,
    ROOM: roomArr,
  };
  Object.assign(FData, RequestData());
  await fetch(`${host}/usersManagement`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(FData),
  })
    .then((response) => response.json())
    .then((data) => {
      // console.log(data);
      document.querySelector("#update-user-close-btn").click();
      if(data.DATA){
        popupMessageTitle.innerHTML = "Add User"
        popupMessageBody.innerHTML = `<p>New user <strong>${updateUsernameInput.value}</strong> has been added successfully</p>`
        document.querySelector("#popupMessageOpenBtn").click()
        setTimeout(()=>{
          location.reload()
        }, 3000)
      } else {
        submitFormBtn.disabled = false
        if ("Username" in data.ERROR[0]) {
          updateUsernameInput.style.border = borderRed;
          updateUsernameInputError.innerText = data.ERROR[0].Username;
          // return;
        }
        if ("Fullname" in data.ERROR[0]) {
          updateFullnameInput.style.border = borderRed;
          updateFullnameInputError.innerText = data.ERROR[0].Fullname;
          // return;
        }
        if ("Email" in data.ERROR[0]) {
          updateEmailInput.style.border = borderRed;
          updateEmailInputError.innerText = data.ERROR[0].Email;
          // return;
        }
        if ("Type" in data.ERROR[0]) {
          updateTypeInput.style.border = borderRed;
          updateTypeInputError.innerText = data.ERROR[0].Type;
          // return;
        }
      }
    })
    .catch((error) => {
      submitFormBtn.disabled = false
      console.error("Error:", error);
    });
}

function clearFormData(){
  submitFormBtn.disabled = true
  updateUsernameInput.style.border = borderOri;
  updateUsernameInputError.innerText = "";
  updateFullnameInput.style.border = borderOri;
  updateFullnameInputError.innerText = "";
  updateEmailInput.style.border = borderOri;
  updateEmailInputError.innerText = "";
  updateTypeInput.style.border = borderOri;
  updateTypeInputError.innerText = "";
  if (updateUsernameInput.value == "") {
    updateUsernameInput.style.border = borderRed;
    updateUsernameInputError.innerText = "Username is Empty!";
  }
  if (updateFullnameInput.value == "") {
    updateFullnameInput.style.border = borderRed;
    updateFullnameInputError.innerText = "Full name is Empty!";
  }
  if (updateEmailInput.value == "") {
    updateEmailInput.style.border = borderRed;
    updateEmailInputError.innerText = "Email is Empty!";
  } else {
    if (!validateEmail(updateEmailInput.value)) {
      updateEmailInput.style.border = borderRed;
      updateEmailInputError.innerText = "Email address is incorrect!";
    }
  }
  if (updateTypeInput.value == "-1") {
    updateTypeInput.style.border = borderRed;
    updateTypeInputError.innerText = "Please Select!";
  }
}
