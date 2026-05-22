document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("twofaForm");
    const errorBox = document.getElementById("error");
    const resendBtn = document.getElementById("resendBtn");
    const verifyBtn = document.getElementById("verifyBtn");
    const timerEl = document.getElementById("timer");

    const validDurationSeconds = 8 * 60; 
    let remainingSeconds = validDurationSeconds;
    let timerInterval = null;

    if (!form || !errorBox || !resendBtn || !verifyBtn || !timerEl) return; 

    function showMessage(message, success = false) {
        errorBox.textContent = message; 
        errorBox.style.display = "block";
        errorBox.style.color = success ? "green" : "red";
    }

    function hideMessage() {
        errorBox.style.display = "none";
        errorBox.textContent = "";
    }
     
    function formatTime(totalSeconds) {
        const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
        const seconds = String(totalSeconds % 60).padStart(2, "0");
        return `${minutes}:${seconds}`; 
    } 

    function stopTimer() {
        if (timerInterval) {
            clearInterval(timerInterval);
        }

        timerInterval = null;
    }

    function updateUI() {
        timerEl.textContent = formatTime(Math.max(remainingSeconds, 0));

        const expired = remainingSeconds <= 0;

        verifyBtn.disabled = expired;
        resendBtn.disabled = !expired;

        timerEl.style.color = expired ? "red" : "";
    }

    function startTimer(reset = true) {
        stopTimer();

        if (reset) {
            remainingSeconds = validDurationSeconds;
        }

        updateUI();

        timerInterval = setInterval(() => {
            remainingSeconds -= 1; 
            updateUI();

            if (remainingSeconds <= 0) {
                stopTimer();
                showMessage("Code is verlopen. Klik op 'Code opnieuw sturen'.");
            }
        }, 1000);
    }

    startTimer(true);

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        hideMessage();

        if (remainingSeconds <= 0) {
            showMessage("Code is verlopen. Klik op 'Code opnieuw sturen'.");
            return;
        }

        const code = form.code.value.trim();

        if (code === "") {
            showMessage("Vul de verificatiecode in.");
            return;
        }   

        try {
            const response = await fetch("/auth/verify-twofactor", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                }, 
                credentials: "same-origin",
                body: new URLSearchParams({ code: code })
            });

            const text = await response.text();

            if (!response.ok) {
                if (text === "2FA_EXPIRED") {
                    remainingSeconds = 0;
                    updateUI();
                    showMessage("Code is verlopen. Klik op 'Code opnieuw sturen'.");
                } else if (text === "2FA_INVALID") {
                    showMessage("Ongeldige code. Probeer het opnieuw.");
                } else if (text === "2FA_TOO_MANY_ATTEMPTS") {
                    showMessage("Te veel mislukte pogingen. Je wordt teruggestuurd naar de inlogpagina.");
                    setTimeout(() => {
                        window.location.href = "/login";
                    }, 2000);

                } else if (text === "2FA_NOT_STARTED") {
                    showMessage("2FA proces is niet gestart. Log opnieuw in.");
                } else {
                    showMessage("Verficatie mislukt. Probeer het opnieuw.");
                }

                return;
            } 

            window.location.href = "/index";
        } catch (error) {
            console.error(error);
            showMessage("Serverfout. Probeer het opnieuw.");
        }
    });

    resendBtn.addEventListener("click", async () => {
        hideMessage();

        try {
            const response = await fetch("/auth/resend-twofactor", {
                method: "POST",
                credentials: "same-origin"
            });

            const text = await response.text();

            if (!response.ok) {
                showMessage("Fout bij het opnieuw versturen van de code. Probeer het opnieuw.");
                return;
            }

            showMessage("Nieuwe code is verzonden!", true);

            form.code.value = "";
            startTimer(true);

        } catch (error) {
            console.error(error);
            showMessage("Serverfout. Probeer het opnieuw.");
        }
    });
});