# Conversational Dashboard - Frontend

A modern, intelligent dashboard that connects to your backend API and allows users to query data using natural language.

## Features

✨ **Natural Language Queries** - Ask questions about your data in plain English
📊 **Smart Visualizations** - Automatic chart generation based on query results
🎯 **Real-time Analysis** - Instant aggregations (sum, average, count, min, max, etc.)
⚡ **Quick Access** - Pre-built query buttons for common analyses
📈 **Data Overview** - Preview results in both chart and table formats
🎨 **Beautiful UI** - Dark modern design with glassmorphism effects

## Backend Integration

This frontend communicates with the backend API running on `http://127.0.0.1:8080`

### Backend Requirements

Backend must be running with these endpoints:
- `GET /` - Health check
- `GET /columns` - Get available columns
- `POST /query` - Process natural language queries

### Start Backend

```bash
cd Backend
python app.py
```

The backend will start on `http://127.0.0.1:8080`

## Frontend Setup

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- The backend running on port 8080

### Installation

```bash
# Install dependencies
npm install
# or
yarn install
# or
pnpm install
```

### Development

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

The frontend will start on `http://localhost:3000`

### Build for Production

```bash
npm run build
npm start
```

## Usage

1. **Open the Dashboard** - Navigate to `http://localhost:3000`

2. **Ask a Question** - Type your query in the input field:
   - "What is the average price by model?"
   - "Show me total tax grouped by transmission"
   - "How many cars by year?"
   - "Maximum mileage by fueltype"

3. **Quick Queries** - Click any of the suggested queries to run them instantly

4. **View Results** - See data visualized as charts and tables

5. **Query History** - Past queries are saved and can be clicked to re-run

## Query Examples

### Aggregation Functions
- **Average**: "What is the average price?", "Mean tax by transmission"
- **Sum/Total**: "Show me total mpg", "Sum of all taxes"
- **Count**: "How many cars?", "Count of vehicles by model"
- **Min/Max**: "Minimum mileage", "Highest tax by year"
- **Median/Std**: "Median enginesize", "Standard deviation of price"

### Grouping Patterns
- "price by model" - group by model
- "tax grouped by transmission" - group by transmission
- "mileage per fueltype" - group by fueltype
- "enginesize across years" - group by year

## Architecture

```
Frontend (Next.js + React)
         ↓ HTTP Request
    Backend API (FastAPI)
         ↓
    Intelligent Query Parser
         ↓
    Pandas Data Processing
         ↓
    Returns JSON
```

## API Response Format

```json
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

## Tech Stack

- **Framework**: Next.js 15
- **UI Library**: React 19
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **Backend**: FastAPI (Python)
- **Data Processing**: Pandas

## Troubleshooting

### Frontend can't connect to backend
- Ensure backend is running on `http://127.0.0.1:8080`
- Check if port 8080 is available
- Browser console should show connection errors

### No data displayed
- Verify column names in your dataset
- Check browser console for API errors
- Ensure JSON response from backend is valid

### Chart not rendering
- Open browser console and check for errors
- Verify data structure matches expected format
- Try a simpler query first

## Performance Notes

- Charts render efficiently with up to 1000+ data points
- Query history limited to 5 most recent queries
- Data table shows preview of first 10 records
- Automatic response validation and error handling

## Future Enhancements

- [ ] Export data to CSV/Excel
- [ ] Save favorite queries
- [ ] Multi-metric comparisons
- [ ] Custom chart type selection
- [ ] Data filtering and sorting
- [ ] Time-range selection

## License

MIT

## Support

For issues or questions, check the backend logs and browser console for detailed error messages.
