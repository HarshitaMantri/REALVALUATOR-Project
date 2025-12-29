# RealValuator - Smart Real Estate Price Predictor

## Why Do I Need to Run the Server?

Your RealValuator application requires a **Flask web server** to run because:

1. **API Endpoints**: The price prediction feature uses API calls (`/api/predict_home_price`) that need the Flask backend
2. **Location Data**: The app fetches location names from the server (`/api/get_location_names`)
3. **File Serving**: The server serves all HTML, CSS, JS, and image files

## How to Start the Server

### Option 1: Double-click the startup script (Easiest!)
- **Windows**: Double-click `start_server.bat`
- **PowerShell**: Double-click `start_server.ps1` (or right-click → Run with PowerShell)

### Option 2: Run from Command Line
```bash
cd server
python server.py
```

### Option 3: Run from Project Root
```bash
python server/server.py
```

## After Starting the Server

Once the server is running, you'll see:
```
* Running on http://127.0.0.1:5000
```

Then open your browser and go to:
- **Homepage**: http://127.0.0.1:5000/
- **Price Predictor**: http://127.0.0.1:5000/app.html
- **Listings**: http://127.0.0.1:5000/listings.html
- **Contact**: http://127.0.0.1:5000/contact.html

## Note

You **cannot** just double-click the HTML files to open them because:
- The navigation links point to `http://127.0.0.1:5000/...`
- The price prediction requires API calls to the server
- Without the server running, these features won't work

The server must be running for the application to work properly!

## Stopping the Server

Press `Ctrl+C` in the terminal window where the server is running.

