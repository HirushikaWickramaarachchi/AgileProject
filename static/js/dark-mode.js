(() => {
    const KEY       = 'darkMode';
    const ADMIN_KEY = 'adminDarkMode';
    const root      = document.documentElement;

    const apply = (dark) => {
        root.classList.toggle('dark-mode', dark);
        document.querySelectorAll('.navbar-dark-toggle, .page-dark-toggle').forEach(btn => {
            const icon = btn.querySelector('i');
            if (icon) icon.className = dark ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
            btn.setAttribute('title',      dark ? 'Switch to light mode' : 'Switch to dark mode');
            btn.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
        });
    };

    // Read either key so admin dark mode carries over to user pages
    const isDark = localStorage.getItem(KEY) === 'true' || localStorage.getItem(ADMIN_KEY) === 'true';
    apply(isDark);

    document.querySelectorAll('.navbar-dark-toggle, .page-dark-toggle').forEach(btn => {
        btn.addEventListener('click', () => {
            const dark = root.classList.toggle('dark-mode');
            // Write both keys so the other system stays in sync
            localStorage.setItem(KEY,       dark);
            localStorage.setItem(ADMIN_KEY, dark);
            apply(dark);
        });
    });
})();
