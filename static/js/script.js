document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form');
    const submit = document.getElementById('button');
    const input = document.getElementById('city');
    const recentCity = document.querySelectorAll('.recent-city-btn')

    if (!form || !submit || !input) return;

    const text = submit.textContent;

    input.focus();

    form.addEventListener('submit', (event) => {
        const city = input.value.trim();
        const submitter = event.submitter;

        if (!submitter) return;

        if (!city || !/^[\p{L}\s,.-]+$/u.test(city)) {
            event.preventDefault();
            alert("Please enter a valid city name (letters and spaces only).");

            submit.disabled = false;
            submit.textContent = text;
            input.focus();
            return;
        }

        submit.classList.add('is-loading');
        submit.disabled = true;
    });

    recentCity.forEach(btn => {
        btn.addEventListener('click', () => {
            const selected = btn.getAttribute('data-city');
            input.value = selected;
            input.focus();
        });
    });

    const table = document.getElementById("table");
    if (table) {
        table.scrollIntoView({ behavior: "smooth" });
    }
});
