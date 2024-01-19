const loginForm = document.getElementById("loginForm");
const loginUsernameInput = document.getElementById("loginUsernameInput");
const loginPasswordInput = document.getElementById("loginPasswordInput");
const loginSubmitBtn = document.getElementById("loginSubmitBtn");


loginForm.addEventListener("submit", logInSubmit);

if(checkLogin()){
  window.location.href = host
}

async function logInSubmit(e) {
  e.preventDefault();
  loginSubmitBtn.disabled = true;
  if (loginUsernameInput.value == "") {
    loginUsernameInput.parentElement.classList.add("alert-validate");
  }
  if (loginPasswordInput.value == "") {
    loginPasswordInput.parentElement.classList.add("alert-validate");
  }
  if (
    loginUsernameInput.value != "" &&
    loginPasswordInput.value != ""
  ) {
    loginUsernameInput.parentElement.classList.remove("alert-validate");
    loginPasswordInput.parentElement.classList.remove("alert-validate");
    
    
    let RData = {
      LOGIN_NAME: loginUsernameInput.value,
      PWD: SHA256(loginPasswordInput.value)
    };
    showLoading()
    await fetch(`${host}/api/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(RData),
    })
      .then((response) => response.json())
      .then((data) => {
        loginSubmitBtn.disabled = false;
        // console.log(data)
        if(data.DATA){
          data.DATA.forEach(d => {
            // console.log(d)
            const key = Object.keys(d)
            const value = Object.values(d)
            console.log(key, value)
            setCookie(key, value, 1)
          })
          loginUsernameInput.value = ''
          loginPasswordInput.value = ''
          window.location.href = host
        } else {
            if ('Username' in data['ERROR'][0]){
                loginUsernameInput.parentElement.setAttribute('data-validate', data["ERROR"][0]["Username"])
                loginUsernameInput.parentElement.classList.add("alert-validate");
            }
            if ('PWD' in data['ERROR'][0]){
                loginPasswordInput.parentElement.setAttribute('data-validate', data["ERROR"][0]["PWD"])
                loginPasswordInput.parentElement.classList.add("alert-validate");
            }
        }
        hideLoading()
      })
      .catch((error) => {
        hideLoading()
        console.error("Error:", error);
        loginSubmitBtn.disabled = false;
      });
  } else {
    loginSubmitBtn.disabled = false;
    return;
  }
}
