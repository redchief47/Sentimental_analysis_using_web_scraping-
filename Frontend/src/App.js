import React, { useState } from 'react';
import axios from 'axios';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import './App.css';

ChartJS.register(ArcElement, Tooltip, Legend);

function App() {
  const [url, setUrl] = useState('');
  const [manualReviews, setManualReviews] = useState('');
  const [reviews, setReviews] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleScrape = async () => {
    setLoading(true);
    setProgress(0);
    const interval = setInterval(() => {
      setProgress(prev => Math.min(prev + 10, 90));
    }, 500);
    try {
      const response = await axios.post('/scrape', { url });
      setReviews(response.data.reviews);
      setProgress(100);
    } catch (error) {
      alert('Error scraping reviews');
    } finally {
      clearInterval(interval);
      setLoading(false);
      setProgress(0);
    }
  };

  const handleAddManualReviews = () => {
    const reviewsArray = manualReviews.split('\n').filter(r => r.trim());
    setReviews(reviewsArray);
    setManualReviews('');
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setProgress(0);
    const interval = setInterval(() => {
      setProgress(prev => Math.min(prev + 20, 90));
    }, 200);
    try {
      const response = await axios.post('/analyze', { reviews });
      setResults(response.data.results);
      setProgress(100);
    } catch (error) {
      alert('Error analyzing reviews');
    } finally {
      clearInterval(interval);
      setLoading(false);
      setProgress(0);
    }
  };

  const getChartData = () => {
    const positive = results.filter(r => r.sentiment === 'positive').length;
    const negative = results.filter(r => r.sentiment === 'negative').length;
    const neutral = results.filter(r => r.sentiment === 'neutral').length;
    return {
      labels: ['Positive', 'Negative', 'Neutral'],
      datasets: [
        {
          data: [positive, negative, neutral],
          backgroundColor: ['#4CAF50', '#F44336', '#FFC107'],
        },
      ],
    };
  };

  return (
    <div className="App">
      <h1>Product Review Sentiment Analysis</h1>
      <div className="section">
        <input
          type="text"
          placeholder="Enter Amazon, Flipkart, or Alibaba product URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button onClick={handleScrape} disabled={loading}>Scrape Reviews</button>
      </div>
      <div className="section">
        <h2>Or Add Reviews Manually</h2>
        <textarea
          placeholder="Enter reviews, one per line"
          value={manualReviews}
          onChange={(e) => setManualReviews(e.target.value)}
          rows={5}
        />
        <button onClick={handleAddManualReviews}>Add Reviews</button>
      </div>
      {loading && (
        <div className="progress-container">
          <progress value={progress} max={100} />
          <p>{progress}%</p>
        </div>
      )}
      {reviews.length > 0 && (
        <div className="section">
          <h2>Reviews ({reviews.length})</h2>
          <ul>
            {reviews.map((review, index) => (
              <li key={index}>{review}</li>
            ))}
          </ul>
          <button onClick={handleAnalyze} disabled={loading}>Analyze Sentiments</button>
        </div>
      )}
      {results.length > 0 && (
        <div className="section">
          <h2>Analysis Results</h2>
          <ul>
            {results.map((result, index) => (
              <li key={index}>
                <strong>{result.sentiment.toUpperCase()}</strong>: {result.text}
                <br />
                Score: {JSON.stringify(result.score)}
              </li>
            ))}
          </ul>
          <h2>Sentiment Distribution</h2>
          <div className="chart-container">
            <Pie data={getChartData()} />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
