// Function to generate a random password
function generateRandomPassword() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()';
    let password = '';
    for (let i = 0; i < 12; i++) {
        password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return password;
}

// Toggle password visibility
function togglePasswordVisibility(inputId, iconId) {
    const passwordInput = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    if (passwordInput.type === "password") {
        passwordInput.type = "text";  // Show password
        icon.src = "/static/images/show.png";  // Show icon
    } else {
        passwordInput.type = "password";  // Hide password
        icon.src = "/static/images/hide.png";  // Hide icon
    }
}

// Function to copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function () {
        alert("Password copied to clipboard!");
    }).catch(function (error) {
        console.error("Failed to copy text: ", error);
    });
}

// Add event listeners after the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function () {
    // Toggle password visibility for password1
    document.getElementById("togglePassword1View").addEventListener("click", function () {
        togglePasswordVisibility("password1Input", "toggleIcon1");
    });

    // Toggle password visibility for password2
    document.getElementById("togglePassword2View").addEventListener("click", function () {
        togglePasswordVisibility("password2Input", "toggleIcon2");
    });

    // Generate random password and populate both password fields
    document.getElementById("generatePasswordBtn").addEventListener("click", function () {
        const newPassword = generateRandomPassword();
        document.getElementById("password1Input").value = newPassword;
        document.getElementById("password2Input").value = newPassword;
    });

    // Copy the password1 value to the clipboard
    document.getElementById("copyPasswordBtn").addEventListener("click", function () {
        const password1 = document.getElementById("password1Input").value;
        if (password1) {
            copyToClipboard(password1);
        } else {
            alert("Generate a password first!");
        }
    });
});
