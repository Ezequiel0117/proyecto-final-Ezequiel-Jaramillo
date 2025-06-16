function togglePassword(fieldName) {
  const input = document.querySelector(`input[name="${fieldName}"]`);
  const icon = input.nextElementSibling;
  if (input.type === "password") {
    input.type = "text";
    icon.classList.remove("fa-eye");
    icon.classList.add("fa-eye-slash");
  } else {
    input.type = "password";
    icon.classList.remove("fa-eye-slash");
    icon.classList.add("fa-eye");
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const passwordInput = document.querySelector('input[name="password1"]');
  const hints = {
    uppercase: document.getElementById("uppercase"),
    lowercase: document.getElementById("lowercase"),
    number: document.getElementById("number"),
    special: document.getElementById("special"),
    length: document.getElementById("length"),
    requirementsMet: document.getElementById("requirements-met"),
  };

  if (passwordInput && hints.uppercase && hints.lowercase && hints.number && hints.special && hints.length && hints.requirementsMet) {
    passwordInput.addEventListener("input", function () {
      const value = passwordInput.value;
      const hasUppercase = /[A-Z]/.test(value);
      const hasLowercase = /[a-z]/.test(value);
      const hasNumber = /[0-9]/.test(value);
      const hasSpecial = /[!@#$%^&*]/.test(value);
      const hasLength = value.length >= 8;

      hints.uppercase.classList.toggle("valid", hasUppercase);
      hints.lowercase.classList.toggle("valid", hasLowercase);
      hints.number.classList.toggle("valid", hasNumber);
      hints.special.classList.toggle("valid", hasSpecial);
      hints.length.classList.toggle("valid", hasLength);

      const metCount = [hasUppercase, hasLowercase, hasNumber, hasSpecial, hasLength].filter(Boolean).length;
      hints.requirementsMet.textContent = `Requisitos cumplidos: ${metCount}/3`;
      hints.requirementsMet.classList.toggle("valid", metCount >= 3);
    });
  }
});