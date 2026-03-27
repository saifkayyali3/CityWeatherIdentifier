document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form');
    const submit = document.getElementById('button');
    const Input = document.getElementById('city');

    if (!form || !submit || !Input) return;

    const text = submit.textContent; 

    form.addEventListener('submit', (event) => {
        const city = Input.value.trim();
        const submitter = event.submitter;

        if (!submitter) return;

        if (submitter.tagName === "BUTTON" && submitter.name === "recentCity") return;

        if (!city || !/^[\p{L}\s,.-]+$/u.test(city)) {
            event.preventDefault(); 
            alert("Please enter a valid city name (letters and spaces only).");

            submit.disabled = false;
            submit.textContent = text;
            Input.focus();
            return;
        }

        submit.disabled = true;
        submit.textContent = "Loading...";
    });

    const table=document.getElementById("table");
    if (table) {
        table.scrollIntoView({behavior: "smooth"});
    }
});
