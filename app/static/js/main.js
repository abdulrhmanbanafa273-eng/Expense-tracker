document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
        if (!window.confirm(form.dataset.confirm)) {
            event.preventDefault();
        }
    });
});

// Disable the submit button and swap its label while a form is actually submitting.
// This also stops accidental double-submits on a slow connection.
document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", (event) => {
        if (event.defaultPrevented) {
            return;
        }
        const button = form.querySelector("button[data-loading-text]");
        if (button) {
            button.disabled = true;
            button.textContent = button.dataset.loadingText;
        }
    });
});
