const inputs = document.querySelectorAll(".otp-input-box input");
console.log(inputs);
const button = document.querySelector("#verify-btn");
console.log(button);


inputs.forEach((input, index1) => {
    input.addEventListener("keyup", (e) => {
        const currentInput = input;
        const nextInput = input.nextElementSibling;
        const prevInput = input.previousElementSibling;

        if (currentInput.value.length > 1) {
            currentInput.value = ""
            return
        }

        if (nextInput && nextInput.hasAttribute("disabled") && currentInput.value !== "") {
            nextInput.removeAttribute("disabled")
            nextInput.focus();
        }

        // to delete the otp with backspace
        if (e.key === "Backspace") {
            inputs.forEach((input, index2) => {
                if (index1 <= index2 && prevInput) {
                    input.setAttribute("disabled", true);
                    currentInput.value = "";
                    prevInput.focus();
                }
            })
        }
        // to activate the verify button

        if (!inputs[5].disabled && inputs[5].value !== "") {
            button.classList.add("active")
        }

        else {
            button.classList.remove("active")
        }

    })
})


window.addEventListener("load", () => { inputs[0].focus() });