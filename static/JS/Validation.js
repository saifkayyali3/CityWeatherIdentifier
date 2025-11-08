document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form');
    const submit = document.getElementById('button');
    const Input = document.getElementById('city');

    if (!form || !submit || !Input) return;

    const text = submit.textContent; 




    form.addEventListener('submit', (event) => {
        const city = Input.value.trim();

        
        if (!city || !/^[A-Za-z\s]+$/.test(city)) {
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
});


