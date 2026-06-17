document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form');
    const submit = document.getElementById('button');
    const input = document.getElementById('city');
    const recentCityContainer = document.getElementById("recent-city-container");
    const errorDiv = document.getElementById("error-message");
    let recentCities = JSON.parse(localStorage.getItem("recent_cities")) || [];

    if (!form || !submit || !input) return;

    const cityNameSpan = document.querySelector("#cityname span");
    let currentCity = cityNameSpan ? cityNameSpan.textContent.trim() : "";
    if (currentCity) {
        recentCities = recentCities.filter(city => city !== currentCity);
        recentCities.unshift(currentCity);

        recentCities = recentCities.slice(0, 5);
        localStorage.setItem("recent_cities", JSON.stringify(recentCities));
    }

    if (recentCities.length > 0 && recentCityContainer) {
        recentCityContainer.innerHTML = `<h5>Recent Cities:</h5>`;
        recentCities.forEach(city => {
            recentCityContainer.innerHTML += `<button type="button" name="recentCity" data-city="${city}" class="recent-city-btn">${city}</button>`;
        });
    }

    const recentCityButton = document.querySelectorAll('.recent-city-btn');

    const text = submit.textContent;

    form.addEventListener('submit', (event) => {
        const city = input.value.trim();
        const submitter = event.submitter;
        if (errorDiv) {
            errorDiv.classList.add('d-none');
            errorDiv.textContent = '';
        }

        if (!submitter) return;

        if (!city || !/^[\p{L}\s,.-]+$/u.test(city)) {
            event.preventDefault();

            if (errorDiv) {
                errorDiv.textContent = "Please enter a valid city name (letters and spaces only).";
                errorDiv.classList.remove('d-none');
                errorDiv.scrollIntoView({ behavior: "smooth" });
            }

            submit.disabled = false;
            submit.textContent = text;
            input.focus();
            return;
        }

        submit.classList.add('is-loading');
        submit.disabled = true;
    });

    recentCityButton.forEach(btn => {
        btn.addEventListener('click', () => {
            const selected = btn.getAttribute('data-city');
            input.value = selected;
        });
    });

    const table = document.getElementById("table");
    if (table) {
        table.scrollIntoView({ behavior: "smooth" });
    }
});
