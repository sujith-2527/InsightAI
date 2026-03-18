# Conversational Dashboard 🚀

An intelligent, conversational data analytics dashboard that understands natural language queries and provides real-time visualizations.

## 🌟 Features

- **Natural Language Processing** - Ask questions in plain English, no SQL required
- **Intelligent Query Parser** - Automatically detects metrics, grouping, and aggregation functions
- **Optional Gemini AI Integration** - Enhanced query understanding with Google Gemini API (optional)
- **Real-time Visualization** - Dynamic charts and graphs based on your data
- **Multiple Aggregations** - Sum, Average, Count, Min, Max, Median, Standard Deviation
- **Modern UI** - Beautiful dark theme with glassmorphism effects
- **Query History** - Track and re-run previous analyses
- **Quick Queries** - Pre-built buttons for common analysis patterns
- **Hybrid Intelligence** - Fallback to local parser if API unavailable

## 🏗️ Architecture

```
Frontend (HTML/JavaScript/Chart.js)
    ↓ HTTP REST API
Backend (FastAPI + Pandas)
    ↓ Intelligent Query Parser
Data Processing Engine
    ↓ JSON Response
Visualization Layer
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ (for backend)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Git (for version control)

### Backend Setup

1. **Navigate to Backend Directory**
   ```bash
   cd Backend
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Optional: Configure Gemini API for Enhanced Query Understanding**
   
   To enable Google Gemini AI for better natural language understanding:
   
   a. Get your API key:
      - Visit: [Google AI Studio](https://aistudio.google.com/apikey)
      - Create a new API key
   
   b. Set environment variable:
      ```bash
      # On Windows (PowerShell)
      $env:GEMINI_API_KEY = "your_api_key_here"
      
      # On macOS/Linux (Bash)
      export GEMINI_API_KEY="your_api_key_here"
      ```
   
   c. Or create a `.env` file:
      ```bash
      cp .env.example .env
      # Edit .env and add your GEMINI_API_KEY
      ```
   
   **Note:** If GEMINI_API_KEY is not set, the system automatically falls back to the local query parser.

4. **Start the Backend Server**
   ```bash
   python app.py
   ```
   - Server starts on: `http://127.0.0.1:8080`
   - Data loaded from: `cars.csv`

### Frontend Setup

1. **Open in Browser**
   - Navigate to: `Frontend/index.html`
   - Or open the file directly in your browser

2. **Start Querying**
   - Type: `"What is the average price by model?"`
   - Click Query or press Enter
   - View results in charts and tables

## 📊 Query Examples

### Basic Queries
- "What is the average price by model?"
- "Show me total tax grouped by transmission"
- "How many cars by year?"

### Advanced Queries
- "Maximum mileage by fueltype"
- "Minimum enginesize per transmission"
- "What's the highest tax by year?"

### Aggregation Functions
- **Average** - "average price", "mean tax", "mean engine size"
- **Sum/Total** - "total tax", "sum of mileage", "total mpg"
- **Count** - "how many cars", "count of vehicles"
- **Min** - "minimum price", "lowest mileage"
- **Max** - "maximum tax", "highest mileage"
- **Median** - "median price by year"
- **Std Dev** - "standard deviation of price"

## 📁 Project Structure

```
conversational-dashboard/
├── Backend/
│   ├── app.py                      # FastAPI app with intelligent query parser
│   ├── cars.csv                    # Sample dataset
│   ├── test_intelligent.py         # Comprehensive test suite
│   └── requirements.txt            # Python dependencies
│
├── Frontend/
│   ├── index.html                  # Main dashboard UI
│   └── README.md                   # Frontend documentation
│
├── .gitignore                      # Git ignore patterns
├── .github/workflows/              # CI/CD workflows
├── README.md                       # This file
├── LICENSE                         # MIT License
└── DEPLOYMENT.md                   # Deployment guide
```

## 🔧 Backend API

### Endpoints

#### GET `/`
Health check endpoint
```
Request: GET http://127.0.0.1:8080/
Response: {"message": "Server running 🚀"}
```

#### GET `/columns`
Get available data columns
```
Request: GET http://127.0.0.1:8080/columns
Response: {"columns": ["model", "year", "price", ...]}
```

#### POST `/query`
Submit a natural language query
```
Request: POST http://127.0.0.1:8080/query
Body: {"user_query": "What is the average price by model?"}

Response:
{
  "data": [
    {"model": " 1 Series", "price": 15821.67},
    {"model": " 2 Series", "price": 19539.37}
  ],
  "meta": {
    "chart_type": "bar",
    "x": "model",
    "y": "price",
    "aggregation": "mean",
    "query_parsed": "mean(price) grouped by model",
    "record_count": 24
  }
}
```

## 🛠️ Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend | FastAPI | 0.104+ |
| Data Processing | Pandas | 2.0+ |
| Server | Uvicorn | 0.24+ |
| Frontend | HTML5/CSS3/JavaScript | ES6+ |
| Charting | Chart.js | 4.4+ |
| API Communication | Fetch API | Standard |
| AI Integration | Google Gemini API | Latest (Optional) |

## 📈 Performance

- **Query Response Time**: < 500ms (typical)
- **Chart Rendering**: Real-time with up to 1000+ data points
- **Data Table**: Paginated preview (first 10 records)
- **History Storage**: Last 5 queries in memory

## 🔐 Security Features

- CORS-aware design
- Input validation on all endpoints
- Error handling and sanitization
- JSON response validation

## 🚢 Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY Backend/requirements.txt .
RUN pip install -r requirements.txt

COPY Backend/ .
EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Cloud Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on deploying to:
- Heroku
- AWS
- Google Cloud
- Azure

## 🧪 Testing

Run comprehensive tests:
```bash
cd Backend
python test_intelligent.py
```

Expected output: ✅ All 10+ tests passed

## 📝 Sample Data

The project includes `cars.csv` with the following columns:
- **model** - Car model name
- **year** - Manufacturing year
- **price** - Vehicle price
- **transmission** - Transmission type (Automatic/Manual)
- **mileage** - Mileage in miles
- **fueltype** - Fuel type (Diesel/Petrol/etc)
- **tax** - Annual tax amount
- **mpg** - Miles per gallon
- **enginesize** - Engine displacement in liters

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Roadmap

- [ ] Database integration (SQL/MongoDB)
- [ ] User authentication & authorization
- [ ] Multi-file data source support
- [ ] Custom chart type selection
- [ ] Data export (CSV/Excel/PDF)
- [ ] Saved queries & dashboards
- [ ] Advanced filtering & sorting
- [ ] Real-time data updates
- [ ] Mobile app version
- [ ] Machine learning predictions

## 🐛 Troubleshooting

### Backend Connection Error
- Ensure backend is running: `python Backend/app.py`
- Check if port 8080 is available
- Verify firewall settings

### No Data in Charts
- Check browser console for errors (F12)
- Verify CSV file exists in Backend folder
- Test API directly: `curl http://127.0.0.1:8080/columns`

### Query Parsing Issues
- Check if column names match your data
- Try simpler queries first
- Check server logs for detailed errors

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

Created with ❤️ for intelligent data analysis

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Pandas for powerful data manipulation
- Chart.js for beautiful visualizations
- The open-source community

## 📞 Support

For issues, questions, or suggestions:

1. Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment help
2. Review test files for usage examples
3. Open an issue on GitHub
4. Check server logs for errors

---

**Built with intelligence. Powered by your questions.** 🚀
