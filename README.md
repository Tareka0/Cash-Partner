#  Cash Partner: Financial Advisory Dashboard

**Cash Partner** is an integrated financial advisory system designed to help wealth managers and clients analyze investment portfolios manage. This project showcases the integration of Python for financial data processing with a modern, interactive web dashboard.

##  Key Features
* **Portfolio Analytics:** Real-time visualization of total assets, Year-to-Date (YTD) returns, and asset allocation.
* **Investment Simulator:** A recommendation engine that suggests the best investment vehicle based on amount, duration, goal, and risk profile.
* **Automated Advisory Reports:** Generates instant recommendations (e.g., cash reserve reallocation) based on portfolio performance.
* **Interactive UI:** A fully responsive RTL dashboard featuring dynamic data visualization using Chart.js.

##  Tech Stack
* **Backend:** Python 3.x, Flask (RESTful API).
* **Data Analysis:** NumPy (for statistical and financial calculations).
* **Frontend:** HTML5, CSS3, JavaScript (ES6+).
* **Visualization:** Chart.js.

##  How to Run
1. **Start the API:**
   ```bash
   python cash_partner_local.py

The server will run on http://localhost:5002.

Launch the Dashboard:
Open CashPartner_local.html in any modern web browser.

Connect:
Ensure the API URL is correct in the dashboard to fetch live data.

📊 Project Structure
cash_partner_local.py: Main backend logic containing financial formulas and API endpoints.

CashPartner_local.html: The interactive front-end advisory portal.

