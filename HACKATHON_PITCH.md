# Conversational AI for Instant BI Dashboards - 10 Minute Demo Script

## 1) Opening (1 minute)
Problem:
- Business users wait on data teams for simple dashboards.
- SQL and BI tools create a skill barrier for executives.

Solution:
- A conversational BI web app where users ask in plain English and instantly get interactive dashboards.

Value:
- Faster decisions, reduced reporting bottlenecks, and higher data accessibility for non-technical teams.

## 2) Product Walkthrough (1 minute)
Show the app flow:
- User enters natural-language question.
- Backend planner converts text into a safe query plan.
- Data gets aggregated and chart type is selected.
- Frontend renders insights + multiple chart views.

Call out:
- Loading-state UX while dashboard is generated.
- Error and warning cards for ambiguous prompts.

## 3) Architecture (2 minutes)
Pipeline:
1. Text input from user
2. Query planning:
   - Gemini planner when API key is available
   - Local deterministic planner fallback when Gemini is unavailable
3. Guardrails:
   - Column validation against actual schema
   - Safe defaults for aggregation and group-by
   - Filter validation and no-data handling
4. Execution:
   - Pandas aggregation over active dataset
5. Visualization output:
   - Backend returns chart hints, confidence, warnings, and filters applied
   - Frontend creates a cohesive dashboard (primary + supporting chart)

Why this wins:
- Accuracy + reliability + graceful fallback, not just LLM output.

## 4) Live Demo Queries (4 minutes)
Use these in order (simple -> complex):

Query A (basic):
- show me average price by model
Expected:
- Correct grouped aggregation
- Bar chart + supporting line/area chart

Query B (time and trend intent):
- show me yearly average mileage trend
Expected:
- Time-style chart recommendation (line)
- Clear summary and numeric insights

Query C (follow-up complexity):
- now only show automatic transmission top 5
Expected:
- Context-aware conversational behavior
- Filter applied in metadata
- Top-N result trimming and warnings if needed

Bonus demo (data format agnostic):
- Upload a CSV and ask a query immediately
Expected:
- New schema loaded server-side
- Dashboard updates without code changes

## 5) Evaluation Rubric Mapping (1.5 minutes)
Accuracy (40):
- Planner validates columns and aggregations
- Metadata shows what was applied (filters, confidence, parsed query)
- Explicit no-data/error messaging prevents hallucinated numbers

Aesthetics & UX (30):
- Modern chat-like dashboard interface
- Interactive charts with hover tooltips
- Loading progression and user-friendly flow

Approach & Innovation (30):
- Hybrid planner: Gemini + deterministic fallback
- Context-aware follow-up prompts
- Upload-and-query architecture for arbitrary CSV data

## 6) Closing (0.5 minute)
Takeaway:
- This is not just a demo chart generator.
- It is a resilient conversational BI assistant that executives can use immediately.

Ask judges:
- Give us a dataset and a business question right now, and we will answer it live.
