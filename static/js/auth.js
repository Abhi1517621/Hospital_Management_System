document.addEventListener("DOMContentLoaded", () => {
    const loginBtn = document.getElementById("show-login");
    const signupBtn = document.getElementById("show-signup");
    const loginForm = document.getElementById("login-form");
    const signupForm = document.getElementById("signup-form");

    loginBtn.addEventListener("click", () => {
        loginForm.style.display = "block";
        signupForm.style.display = "none";
        loginBtn.classList.add("active");
        signupBtn.classList.remove("active");
    });

    signupBtn.addEventListener("click", () => {
        loginForm.style.display = "none";
        signupForm.style.display = "block";
        signupBtn.classList.add("active");
        loginBtn.classList.remove("active");
    });
});