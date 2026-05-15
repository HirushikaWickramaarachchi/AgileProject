(() => {
    const dialog = document.querySelector("[data-leave-club-dialog]");

    if (!dialog) {
        return;
    }

    const title = dialog.querySelector("#leave-club-dialog-title");
    const message = dialog.querySelector("[data-leave-club-message]");
    const eventsPanel = dialog.querySelector("[data-leave-club-events-panel]");
    const eventsList = dialog.querySelector("[data-leave-club-events-list]");
    const cancelButton = dialog.querySelector("[data-leave-club-cancel]");
    const confirmButton = dialog.querySelector("[data-leave-club-confirm]");
    let activeForm = null;
    let activeTrigger = null;

    const resetDialog = () => {
        activeForm = null;
        if (eventsList) {
            eventsList.innerHTML = "";
        }
        if (eventsPanel) {
            eventsPanel.hidden = true;
        }
        if (confirmButton) {
            confirmButton.disabled = false;
        }
    };

    const closeDialog = () => {
        if (dialog.open) {
            dialog.close();
        }
    };

    document.querySelectorAll("[data-leave-club-trigger]").forEach((trigger) => {
        trigger.addEventListener("click", () => {
            const form = trigger.closest("form");

            if (!form) {
                return;
            }

            activeForm = form;
            activeTrigger = trigger;

            const clubName = trigger.dataset.clubName || "this club";
            const eventItems = form.querySelectorAll("[data-leave-club-events] li");

            title.textContent = `Leave ${clubName}?`;

            if (eventItems.length > 0) {
                message.textContent =
                    "You are currently attending the following events from this club. " +
                    "Leaving the club will also cancel your attendance for these events.";
                eventsPanel.hidden = false;
                eventsList.innerHTML = "";
                eventItems.forEach((item) => {
                    const eventItem = document.createElement("li");
                    eventItem.innerHTML = item.innerHTML;
                    eventsList.appendChild(eventItem);
                });
            } else {
                message.textContent =
                    "You will no longer be a member of this club. " +
                    "You are not currently attending any events from this club.";
                eventsPanel.hidden = true;
                eventsList.innerHTML = "";
            }

            if (typeof dialog.showModal === "function") {
                dialog.showModal();
            } else {
                dialog.setAttribute("open", "");
            }
        });
    });

    cancelButton?.addEventListener("click", closeDialog);

    confirmButton?.addEventListener("click", () => {
        if (!activeForm) {
            closeDialog();
            return;
        }

        confirmButton.disabled = true;
        activeForm.submit();
    });

    dialog.addEventListener("click", (event) => {
        if (event.target === dialog) {
            closeDialog();
        }
    });

    dialog.addEventListener("close", () => {
        activeTrigger?.focus();
        activeTrigger = null;
        resetDialog();
    });
})();
