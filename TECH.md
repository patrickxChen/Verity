an# Technical Stack: Verity

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                         │
│  - Search UI                                                │
│  - Bias Result Display & Charts                             │
│  - Source Analysis View                                     │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/WebSocket
┌────────────────────▼────────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│  - Search orchestration                                     │
│  - Bias analysis pipeline                                   │
│  - Result aggregation & ranking                             │
│  - WebSocket for real-time updates                          │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐      ┌────────▼────────┐
│  Steel.dev     │      │   LLM API       │
│  Browser API   │      │   (OpenRouter)  │
│                │      │   - Bias        │
│  - Search      │      │     Detection   │
│  - Crawl       │      │   - Analysis    │
│  - Extract     │      │   - Scoring     │
└────────────────┘      └─────────────────┘
```

## 🔧 Core Technologies

### Frontend
- **Framework**: React 18+
- **Styling**: Tailwind CSS
- **Charts**: Recharts or Chart.js (for bias visualizations)
- **HTTP Client**: Axios or Fetch API
- **WebSocket**: Socket.io (for real-time updates)
- **Build Tool**: Vite or Create React App

### Backend
- **Framework**: FastAPI (async Python)
- **Web Server**: Uvicorn
- **Async Tasks**: Celery (optional for long-running searches)
- **WebSocket Support**: Starlette/FastAPI built-in
- **Environment**: Python 3.10+

### AI/ML Components
- **LLM Provider**: OpenRouter (primary)
  - Model suggestions: Claude 3.5, GPT-4, or Mistral
  - $500 credits provided by hackathon
- **Prompt Engineering**: Custom prompts for each bias category
- **LLM Calls**: Simple REST API requests (no complex frameworks)

### Browser Automation
- **Steel.dev API**:
  - Browser session management
  - Autonomous web searching and crawling
  - JavaScript execution
  - Screenshot/content extraction
  - **Pricing**: $600 Pro credits provided + free tier available
  - **Docs**: https://steel.dev/

## 🗂️ Project Structure

```
verity/
├── README.md                 # Project overview
├── CONTEXT.md               # Project background & requirements
├── TECH.md                  # This file
├── PROGRESS.md              # Implementation roadmap
│
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example          # Environment variables template
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py         # Configuration (API keys, etc.)
│   │   │
│   │   ├── routers/
│   │   │   ├── search.py     # Search endpoint
│   │   │   └── results.py    # Results endpoint
│   │   │
│   │   ├── services/
│   │   │   ├── steel_service.py     # Steel.dev integration
│   │   │   ├── analysis_service.py  # Bias analysis
│   │   │   ├── llm_service.py       # LLM API calls
│   │   │   └── ranking_service.py   # Result ranking
│   │   │
│   │   └── models/
│   │       ├── search.py     # Request/response schemas
│   │       └── analysis.py   # Bias analysis models
│   │
│   └── tests/
│       ├── test_search.py
│       ├── test_analysis.py
│       └── test_steel_service.py
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js (or webpack.config.js)
│   │
│   ├── public/
│   │   └── index.html
│   │
│   ├── src/
│   │   ├── index.css         # Tailwind CSS
│   │   ├── App.tsx (or .jsx)
│   │   │
│   │   ├── components/
│   │   │   ├── SearchBar.tsx
│   │   │   ├── ResultCard.tsx
│   │   │   ├── BiasIndicator.tsx
│   │   │   ├── BiasChart.tsx
│   │   │   └── SourceDetails.tsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   └── Results.tsx
│   │   │
│   │   ├── hooks/
│   │   │   └── useSearch.ts  # Custom hook for API calls
│   │   │
│   │   └── utils/
│   │       ├── api.ts        # API client
│   │       └── colors.ts     # Bias color mapping
│   │
│   └── tests/
│       └── components.test.tsx
│
└── docs/
    ├── API.md               # API endpoint documentation
    ├── DEPLOYMENT.md        # Deployment instructions
    └── TROUBLESHOOTING.md   # Common issues & solutions
```

## 📦 Key Dependencies

### Backend (Python)
```
fastapi==0.104+
uvicorn==0.24+
python-dotenv==1.0+
aiohttp==3.9+              # For async HTTP requests
pydantic==2.0+             # Data validation
```

### Frontend (JavaScript/TypeScript)
```
react==18+
react-dom==18+
recharts==2.10+            # Charts library
axios==1.6+                # HTTP client
tailwindcss==3.3+
typescript==5.2+           # If using TypeScript
```

## 🔐 Environment Variables

### Backend (.env)
```
# Steel.dev API
STEEL_API_KEY=your_steel_api_key_here
STEEL_BASE_URL=https://api.steel.dev

# LLM Provider (OpenRouter)
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=claude-3.5-sonnet  # or gpt-4-turbo, etc.

# Server
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000

# Development
DEBUG=true
LOG_LEVEL=INFO
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WEBSOCKET_URL=ws://localhost:8000/ws
```

## 🔌 API Integrations

### Steel.dev Browser API
- **Authentication**: API key in headers
- **Endpoints**:
  - Session management
  - Search execution
  - Content extraction
  - Screenshot capture
- **Rate Limits**: Check documentation (included in credits)
- **Timeout Handling**: Implement retry logic with exponential backoff

### OpenRouter LLM API
- **Authentication**: Bearer token
- **Models Available**: 
  - Claude 3.5 Sonnet (recommended)
  - GPT-4 Turbo
  - Mistral Large
  - Others (see OpenRouter marketplace)
- **Request Format**: Standard OpenAI-compatible API
- **Error Handling**: Rate limiting, quota management, fallback models

## 🎯 Data Flow

### Search Query
```
User Input → Frontend Search Bar
    ↓
POST /api/search
{
  "query": "climate change impacts",
  "num_results": 10
}
    ↓
Backend Search Service
    ├── Steel.dev: Execute web search
    ├── Extract: URLs, titles, snippets
    └── Return raw results
    ↓
Analysis Service
    ├── For each result:
    │   ├── LLM: Analyze for each bias category
    │   └── Score: 1-10 per category
    ├── Aggregate: Overall bias score
    └── Rank: Sort by bias level
    ↓
Results → Frontend
    ├── Display results with indicators
    ├── Show bias charts
    └── Allow drilling into details
```

## 🚀 Performance Targets

- **Search Query**: < 3 seconds (with Steel.dev + LLM)
- **Concurrent Searches**: 50+ simultaneous users
- **Result Count**: 10-20 results per search (balanced speed/accuracy)
- **UI Responsiveness**: < 100ms for interactions
- **Memory**: < 512MB base, scales with concurrent users

## 🧪 Testing Strategy

### Backend Tests
- **Unit Tests**: Service functions (bias detection, ranking)
- **Integration Tests**: API endpoints + Steel.dev integration
- **Mocking**: Mock Steel.dev and LLM API calls for speed

### Frontend Tests
- **Component Tests**: React component rendering
- **Integration Tests**: UI + API interactions
- **E2E Tests**: Search → Results flow (if time permits)

## 🔄 Development Workflow

1. **Local Setup**:
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   python -m uvicorn app.main:app --reload

   # Frontend
   cd frontend
   npm install
   npm run dev  # or npm start
   ```

2. **API Testing**: Postman/Insomnia for endpoint testing

3. **Git Workflow**:
   - Feature branches off `main`
   - Commit early and often
   - Descriptive commit messages
   - Push to remote for team visibility

## 📊 Bias Detection Architecture

### Prompt Engineering Strategy
Each bias category uses a specialized prompt to LLM:

```
# Example: Political Bias Detection
You are a political bias detector. Analyze this text:
[ARTICLE CONTENT]

Rate political bias 1-10 (1=neutral, 10=extremely partisan)
Identify left/right leaning indicators
Explain your reasoning

Return JSON: {"bias_score": X, "indicators": [...], "reasoning": "..."}
```

### Multi-Pass Analysis (Optional Enhancement)
- **Pass 1**: Initial bias scoring
- **Pass 2**: Verify scores with different prompt phrasing
- **Pass 3**: Cross-check with reference datasets (if time permits)

## 🎨 Frontend Components Breakdown

### SearchBar
- Input field with autocomplete (optional)
- Search button + loading state
- Result count selector (5, 10, 20 results)

### ResultCard
- Source URL/domain
- Title + snippet
- Bias indicators (colored badges per category)
- Overall bias score gauge
- "Explain" button for details

### BiasIndicator
- Color-coded severity (green→yellow→red)
- Numerical score (1-10)
- Tooltip with category name

### BiasChart
- Radar chart: 6 bias categories as axes
- Individual result data point
- Aggregated average across all results

### SourceDetails (Expandable)
- Full article snippet/preview
- Reasoning for each bias detection
- Confidence scores
- Link to original source

## ⚠️ Known Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| LLM hallucination in bias scoring | Use structured prompts + JSON responses |
| Steel.dev rate limits | Implement queue + batching |
| False positives in bias detection | Confidence thresholds + user feedback |
| Slow response times | Cache common queries, optimize LLM calls |
| WebSocket connection drops | Auto-reconnect with exponential backoff |
| CORS issues | Configure FastAPI CORS middleware properly |

## 🔮 Future Enhancements (Post-Hackathon)

- Multi-language support
- Historical bias tracking
- User accounts & saved searches
- Community reporting system
- Mobile app
- Browser extension
- Real-time fact-checking integration
- Custom bias category definitions
