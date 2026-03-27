# City Weather Identifier - Final Version (v3)

A web app that allows users to find detailed weather information of their preference for cities across the globe. Built with **Flask**, **HTML/CSS/JS/Bootstrap Styling**, and deployed on **Vercel**.

---

## Project History
This web app is the final version of a three-part evolution:
1. **[Jordan Weather Identifier v1](https://github.com/Skayyali3/Jordan-Weather-Identifier-v1)** 
    - The Prototype: First Python GUI using static file I/O.
2. **[City Weather Identifier v2](https://github.com/Skayyali3/City-Weather-Identifier-v2)** 
    - Data Visualizer: Desktop app with live API integration and Seaborn/Matplotlib graphs. 
3. **City Weather Identifier v3 (This Repo)** 
    - Full-Stack: Responsive web app with Flask backend, Pandas data processing and responsive design.

---

## Features

- Retrieve current temperature or hourly/daily weather statistics for any city.
- Data Customizability: Unlike v2's weekly overview, v3 provides both high-resolution hourly data & high-resolution weekly data using Pandas for backend processing
- Responsive design: works on mobile, tablet and desktop.
- Smart Validation: Filters out non-city regions to ensure data accuracy.

---

## Live Demo

Check out the live app here: **[City Weather Identifier](https://city-weather-identifier.vercel.app/)**

---

## Technologies Used

- **Backend:** Python 3.13, Flask  
- **APIs:** Geopy (Nominatim), Open-Meteo, Timezonefinder 
- **Data Processing:** Pandas  
- **Frontend:** HTML, CSS, JavaScript, Bootstrap  
- **Deployment:** Vercel  

---

## How to Run:

### 1. Clone the repository and enter:
```bash
git clone https://github.com/Skayyali3/City-Weather-Identifier-v3.git
cd City-Weather-Identifier-v3
```
### 2. Make a virtual environment
```bash
python -m venv venv

source venv/bin/activate # Linux/macOS
venv\Scripts\activate # Windows
```

### 3. Install the needed requirements
```bash
pip install -r requirements.txt
```

### 4. Run
```bash
python main.py
# Open your browser to http://127.0.0.1:5000 to check out the Weather Site Locally
```

## License

This project is licensed under the MIT License – see the **[license file](LICENSE)** for details.

## Author
**Saif Kayyali**


