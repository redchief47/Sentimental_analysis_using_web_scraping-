# Sentiment Analysis App

## Deployment Instructions

### Backend Setup
1. Ensure Python 3.7+ is installed.
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate  (Windows)
   source venv/bin/activate  (Linux/macOS)
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the backend Flask app:
   ```
   python backend/app.py
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```
   cd frontend
   ```
2. Install Node.js dependencies:
   ```
   npm install
   ```
3. Build the React app for production:
   ```
   npm run build
   ```
4. The build output will be placed in `frontend/build` directory.

### Running the Full Application
- The Flask backend is configured to serve the React frontend build files.
- After building the frontend, start the backend server.
- Access the app at `http://localhost:5000`.

## Features
- Input product URL from Amazon, Flipkart, or Alibaba to scrape reviews.
- Option to manually add reviews.
- Progress bar shown during scraping and analysis.
- Sentiment analysis results displayed with charts.

## Notes
- Ensure Microsoft Edge browser is installed for Selenium scraping.
- The backend uses Selenium with Edge WebDriver for scraping.
- For any scraping issues, check the backend logs.

Made by Shreyash Vinchurkar
