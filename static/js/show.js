// Get the password input element and its actual password from the data attribute
var passwordInput = document.getElementById("passwordInput");
var actualPassword = passwordInput.getAttribute('data-password');  // Decrypted password from data attribute

// Flag to track password visibility
var isPasswordVisible = false;

// Handle password visibility toggle
document.getElementById("togglePasswordView").addEventListener("click", function () {
    var icon = document.getElementById("toggleIcon");

    if (!isPasswordVisible) {
        // Show the actual password
        passwordInput.value = actualPassword;
        passwordInput.type = "text";  // Show the password as plain text
        icon.src = "/static/images/show.png";  // Change to show icon
    } else {
        // Mask the password and show fixed-length placeholder
        passwordInput.value = "●●●●●●●●●●●●";  // Placeholder dots
        passwordInput.type = "password";  // Mask the password again
        icon.src = "/static/images/hide.png";  // Change back to hide icon
    }

    // Toggle the flag
    isPasswordVisible = !isPasswordVisible;
});

// Function to copy text to clipboard
function copyToClipboard(targetId) {
    var input = document.getElementById(targetId);
    var valueToCopy = (targetId === 'passwordInput' && !isPasswordVisible) ? actualPassword : input.value;  // Copy the real password even if hidden

    // Use modern clipboard API to write text to the clipboard
    navigator.clipboard.writeText(valueToCopy).then(function() {
        alert("Copied to clipboard");
    }).catch(function(error) {
        console.error("Failed to copy text: ", error);  // Log error if copy fails
    });
}

// Add click event listeners to all copy buttons
document.querySelectorAll('.copy-btn').forEach(function(copyBtn) {
    copyBtn.addEventListener('click', function () {
        var targetId = copyBtn.getAttribute('data-copy-target');
        copyToClipboard(targetId);
    });
});
