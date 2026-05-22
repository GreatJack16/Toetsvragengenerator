// HOI, deze login.js controleert het login formuler voordat het naar de server wordt gestuurd. 
// Btw, deze wacht totdat het html-pagina HELEMAAL is ingeladen, daarna zoet deze code naar de velden. 

document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");

    if (!form || !emailInput || !passwordInput) return;

    form.addEventListener("submit", (event) => {
        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();    

        if (email === "" || password === "") {
            event.preventDefault();
            alert("Vul zowel e-mail als wachtwoord in.");
            return;
        }

        if (!email.endsWith(".nl")) {
            event.preventDefault();
            alert("Gebruik een geldig @uva.nl e-mailadres.");
            return;
        }

        if (password.length < 6) {
            event.preventDefault();
            alert("Wachtwoord moet minimaal 6 tekens bevatten.");
            return;
        }
    });
});