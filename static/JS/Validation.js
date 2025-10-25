document.getElementById('form').addEventListener('submit', function (event) {
    const name=document.getElementById('city').value.trim();

    if (!name || !/^[A-Za-z\s]+$/.test(name)){
        alert("Please enter a valid city name (letters and spaces only).");
        event.preventDefault();
    }
})