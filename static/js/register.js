// Function to generate a random password based on provided options
function generateRandomPassword(length, useUppercase, useLowercase, useDigits, useSpecial) {
    const uppercaseChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const lowercaseChars = 'abcdefghijklmnopqrstuvwxyz';
    const digitChars = '0123456789';
    const specialChars = '!@#$%^&*()-_=+[]{}|;:,.<>?';

    let charset = '';
    if (useUppercase) charset += uppercaseChars;
    if (useLowercase) charset += lowercaseChars;
    if (useDigits) charset += digitChars;
    if (useSpecial) charset += specialChars;

    // If charset is empty, use a default value to avoid errors
    if (charset.length === 0) charset = lowercaseChars;

    let password = '';
    for (let i = 0; i < length; i++) {
        const randomIndex = Math.floor(Math.random() * charset.length);
        password += charset[randomIndex];
    }

    return password;
}

// Handle button click for password generation
document.getElementById('generatePasswordBtn').addEventListener('click', function () {
    // Retrieve the options for password generation
    const length = parseInt(document.getElementById('password_length').value) || 16;
    const useUppercase = document.getElementById('useUppercase').checked;
    const useLowercase = document.getElementById('useLowercase').checked;
    const useDigits = document.getElementById('useDigits').checked;
    const useSpecial = document.getElementById('useSpecial').checked;

    // Generate the password based on user preferences
    const generatedPassword = generateRandomPassword(length, useUppercase, useLowercase, useDigits, useSpecial);

    // Fill the generated password into the password input fields
    document.getElementById('password1Input').value = generatedPassword;
    document.getElementById('password2Input').value = generatedPassword;

    // Show an alert or flash message
    alert('Random password generated and filled in the input fields!');
});

// Toggle password visibility
function togglePasswordVisibility(inputId, iconId) {
    const passwordInput = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    // Show the password
    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        icon.src = "/static/images/show.png";
    } else {
        passwordInput.type = "password";
        icon.src = "/static/images/hide.png";
    }
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
