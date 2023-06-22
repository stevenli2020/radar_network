const pageTitle = document.getElementById("passTitle");
const userForm = document.getElementById("userForm");
const authTitle = document.getElementById("authTitle");
const usernameInput = document.getElementById("usernameInput");
const passwordInput = document.getElementById("passwordInput");
const confirmPasswordInput = document.getElementById("confirmPasswordInput");
const submitBtn = document.getElementById("authSubmitBtn");

let crtPage = window.location.href.split("?");
crtPage = crtPage[1].split("&");
console.log(crtPage);
if (crtPage[crtPage.length - 1] == "add") {
  pageTitle.innerText = "Add Password";
  authTitle.innerText = "Add New Password";
  usernameInput.value = crtPage[0];
} else if (crtPage[crtPage.length - 1] == "update") {
  pageTitle.innerText = "Update Password";
  authTitle.innerText = "Update Password";
  usernameInput.value = crtPage[0];
}

userForm.addEventListener("submit", passSubmit);

async function passSubmit(e) {
  e.preventDefault();
  submitBtn.disabled = true;
  if (usernameInput.value == "") {
    usernameInput.parentElement.classList.add("alert-validate");
  }
  if (confirmPasswordInput.value == "") {
    confirmPasswordInput.parentElement.classList.add("alert-validate");
  }
  if (passwordInput.value == "") {
    passwordInput.parentElement.classList.add("alert-validate");
  }
  if (
    usernameInput.value != "" &&
    passwordInput.value != "" &&
    confirmPasswordInput.value != ""
  ) {
    usernameInput.parentElement.classList.remove("alert-validate");
    passwordInput.parentElement.classList.remove("alert-validate");
    confirmPasswordInput.parentElement.classList.remove("alert-validate");
    if (passwordInput.value != confirmPasswordInput.value) {
      confirmPasswordInput.parentElement.setAttribute(
        "data-validate",
        "password must be same!"
      );
      confirmPasswordInput.parentElement.classList.add("alert-validate");
      submitBtn.disabled = false;
      return;
    }
    let RData = {
      LOGIN_NAME: usernameInput.value,
      PWD: SHA256(passwordInput.value),
      CPWD: SHA256(confirmPasswordInput.value),
      CODE: crtPage[1],
      AUTH: crtPage[2],
    };
    await fetch(`${host}/api/updatePassword`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(RData),
    })
      .then((response) => response.json())
      .then((data) => {
        submitBtn.disabled = false;
        console.log(data)
        if(data.CODE == 0){
            usernameInput.value = ''
            passwordInput.value = ''
            confirmPasswordInput.value = ''
            window.location.href = `${host}/api/login`
        } else {
            if ('Username' in data['ERROR'][0]){
                usernameInput.parentElement.setAttribute('data-validate', data["ERROR"][0]["Username"])
                usernameInput.parentElement.classList.add("alert-validate");
            }
            if ('PWD' in data['ERROR'][0]){
                passwordInput.parentElement.setAttribute('data-validate', data["ERROR"][0]["PWD"])
                passwordInput.parentElement.classList.add("alert-validate");
            }
            if ('CPWD' in data['ERROR'][0]){
                confirmPasswordInput.parentElement.setAttribute('data-validate', data["ERROR"][0]["CPWD"])
                confirmPasswordInput.parentElement.classList.add("alert-validate");
            }
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        submitBtn.disabled = false;
      });
  } else {
    submitBtn.disabled = false;
    return;
  }
}
