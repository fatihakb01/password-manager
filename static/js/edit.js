// JavaScript function to generate a random password
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
    const length = document.getElementById('password_length').value || 16;
    const useUppercase = document.getElementById('use_uppercase').checked;
    const useLowercase = document.getElementById('use_lowercase').checked;
    const useDigits = document.getElementById('use_digits').checked;
    const useSpecial = document.getElementById('use_special').checked;

    // Generate the password based on user preferences
    const generatedPassword = generateRandomPassword(length, useUppercase, useLowercase, useDigits, useSpecial);

    // Fill the generated password into the password input field
    document.getElementById('passwordInput').value = generatedPassword;

    // Show an alert or flash message
    alert('Random password generated and filled in the input field!');
});

// Handle password visibility toggle
document.getElementById("togglePassword").addEventListener("click", function () {
    var passwordInput = document.getElementById("passwordInput");
    var icon = document.getElementById("toggleIcon");

    if (passwordInput.type === "password") {
        passwordInput.type = "text";  // Show the password as plain text
        icon.src = "/static/images/show.png";  // Change to show icon
    } else {
        passwordInput.type = "password";  // Mask the password again
        icon.src = "/static/images/hide.png";  // Change back to hide icon
    }
});

// Function to copy text to clipboard using modern clipboard API
function copyToClipboard(targetId) {
    var input = document.getElementById(targetId);
    var valueToCopy = input.value;  // Get the value to copy

    // Use the clipboard API to copy text
    navigator.clipboard.writeText(valueToCopy).then(function() {
        alert("Copied");
    }).catch(function(error) {
        console.error("Failed to copy text: ", error);  // Handle any errors
    });
}

// Add click event listeners to all copy buttons
document.querySelectorAll('.copy-btn').forEach(function(copyBtn) {
    copyBtn.addEventListener('click', function () {
        var targetId = copyBtn.getAttribute('data-copy-target');
        copyToClipboard(targetId);
    });
});
