const eyeIcon = document.querySelector("#eye-icon");
const passwordField = document.querySelector("#user-password");

eyeIcon.addEventListener("click", () => {
    passwordField.type = "text"
    setTimeout(() => {
        passwordField.type = "password"
    }, 2000)

})
