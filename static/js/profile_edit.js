let selectedForm = null;

// Switch between sections (left menu)
function showSection(sectionId, clickedButton) {
    const sections = document.querySelectorAll(".settings-section");
    const buttons = document.querySelectorAll(".sidebar-item");

    sections.forEach(section => {
        section.classList.remove("active-section");
    });

    buttons.forEach(button => {
        button.classList.remove("active");
    });

    document.getElementById(sectionId).classList.add("active-section");
    clickedButton.classList.add("active");

    localStorage.setItem("currentProfileSection", sectionId);
}

document.addEventListener("DOMContentLoaded", function () {

    const forms = document.querySelectorAll(".edit-form");
    const saveButtons = document.querySelectorAll(".save-changes-btn");

    const modal = document.getElementById("confirmModal");
    const yesBtn = document.getElementById("confirmYesBtn");
    const noBtn = document.getElementById("confirmNoBtn");

    //  Prevent Enter from submitting form
    forms.forEach(form => {
        form.addEventListener("keydown", function (event) {
            if (event.key === "Enter" && event.target.tagName !== "TEXTAREA") {
                event.preventDefault();
            }
        });
    });

    // Click Save → open confirm modal
    saveButtons.forEach(button => {
    button.addEventListener("click", function () {
        selectedForm = button.closest("form");

        const confirmText = document.getElementById("confirmText");

        const inputs = selectedForm.querySelectorAll("input, textarea, select");
        let hasChange = false;
        if (selectedForm.querySelector('input[name="email_notifications"], input[name="phone_notifications"]')) {
        hasChange = true;
        } 

        inputs.forEach(input => {
            if (input.type === "checkbox") {
                if (input.checked) {
                    hasChange = true;
                }
            } else {
                if (input.value.trim() !== "") {
                    hasChange = true;
                }
            }
        });

        if (!hasChange) {
            confirmText.textContent = "No changes were made. Do you want to stay on this page?";
        } else {
            confirmText.textContent = "Confirm changes?";
        }

        modal.style.display = "flex";
    });
});

    /* yes button → submit form  */
   yesBtn.addEventListener("click", function () {
    if (selectedForm) {
        modal.style.display = "none";
        selectedForm.submit();
    }
});
    // Click NO → close modal (no save)
    noBtn.addEventListener("click", function () {
        modal.style.display = "none";
        selectedForm = null;
    });

});

// Auto hide success message after 3 seconds
document.addEventListener("DOMContentLoaded", function () {
    const msg = document.getElementById("successMessage");

    if (msg) {
        setTimeout(() => {
            msg.style.display = "none";
        }, 2000); // 2000ms = 2 seconds
    }
});
    
/* Remember last section user was on and show it when they come back to the page */
    document.addEventListener("DOMContentLoaded", function () {
    const savedSection = localStorage.getItem("currentProfileSection");

    if (savedSection) {
        const button = document.querySelector(`button[onclick*="${savedSection}"]`);

        if (button) {
            showSection(savedSection, button);
        }
    }
});
