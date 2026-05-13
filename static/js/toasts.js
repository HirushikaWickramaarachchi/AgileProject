(() => {
    const AUTO_DISMISS_MS = 4500;
    const EXIT_ANIMATION_MS = 240;

    const dismissToast = (toast) => {
        if (!toast || toast.classList.contains("is-hiding")) {
            return;
        }

        toast.classList.add("is-hiding");
        window.setTimeout(() => {
            toast.remove();
        }, EXIT_ANIMATION_MS);
    };

    document.querySelectorAll("[data-toast-message]").forEach((toast, index) => {
        window.setTimeout(() => {
            toast.classList.add("is-visible");
        }, index * 80);

        const closeButton = toast.querySelector("[data-toast-dismiss]");
        if (closeButton) {
            closeButton.addEventListener("click", () => dismissToast(toast));
        }

        window.setTimeout(() => {
            dismissToast(toast);
        }, AUTO_DISMISS_MS + index * 300);
    });
})();
