# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-03-18

### Added
- **Google Gemini API Integration** - Optional LLM-powered query understanding
  - Enhanced natural language processing for more complex queries
  - Intelligent detection of metrics, groupby columns, and aggregation functions
  - Automatic fallback to local parser if API unavailable
- Configuration support for `GEMINI_API_KEY` environment variable
- New `parse_query_with_gemini()` function for AI-enhanced query parsing
- `.env.example` template with Gemini API configuration
- Documentation for setting up and using Gemini API

### Improved
- Better handling of ambiguous natural language queries
- More robust JSON parsing from Gemini responses
- Enhanced error handling with graceful fallbacks

## [1.0.0] - 2026-01-15

### Added
- Initial release of Conversational Dashboard
- FastAPI backend with RESTful API endpoints
- Intelligent natural language query parser supporting multiple aggregation functions
- Frontend dashboard with interactive Chart.js visualizations
- Support for the following aggregations:
  - Average (Mean)
  - Sum (Total)
  - Count
  - Min (Minimum)
  - Max (Maximum)
  - Median
  - Standard Deviation
- Column name fuzzy matching for flexible queries
- Query history tracking (last 5 queries)
- Dark theme UI with glasmorphism styling
- CSV data processing with proper null handling
- Comprehensive error handling and user-friendly messages
- Health check endpoint `/health`
- Columns endpoint `/columns` for discovering available data
- Query processing endpoint `/query` for intelligent analysis

### Features
- **Natural Language Understanding**: Parse conversational queries like "What is the average price by model?"
- **Multiple Data Types**: Support for numeric, categorical, and text columns
- **Real-time Visualizations**: Bar charts, line charts, and data tables
- **Responsive Design**: Works on desktop, tablet, and mobile browsers
- **Data Validation**: Automatic null value handling and data type detection

### Documentation
- Comprehensive README with architecture overview
- Setup and installation guide
- Deployment instructions for multiple cloud platforms
- Contributing guidelines
- API endpoint documentation
- Troubleshooting guide

## [0.1.0] - 2026-01-10

### Initial Work
- Project scaffolding
- CSV data file setup
- Basic API structure planning
- Frontend prototype development

---

## Planned Features (Roadmap)

### v1.1.0
- Database support (PostgreSQL, MongoDB)
- User authentication and session management
- Data export functionality (PDF, Excel)
- Advanced filtering and date range selection
- Caching for improved performance

### v1.2.0
- Machine learning predictions (regression, classification)
- Anomaly detection in data
- Scheduled report generation
- Email notifications
- API rate limiting

### v2.0.0
- Multi-dataset support
- Data import wizard
- Custom field calculations
- Real-time data streaming
- WebSocket support for live updates

---

For detailed changes and updates, see the [GitHub Releases](https://github.com/your-username/conversational-dashboard/releases) page.
