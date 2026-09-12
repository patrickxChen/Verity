# Progress & Implementation Roadmap: Verity

**Event Timeline**: September 12-13, 2026 (24 hours)  
**Submission Deadline**: Sunday, September 13 @ 11:00 AM  
**Status**: Project Kickoff

## 🎯 Hackathon Sprint Timeline

### Saturday, September 12

#### 9:00 AM - 11:00 AM: Setup & Planning (2 hours)
- [ ] Team arrives & gets settled
- [ ] Review this documentation
- [ ] Attend opening ceremony & Steel.dev track announcement
- [ ] Set up development environment (git repo, local installs)
- [ ] Establish communication channels (Discord, shared docs)

**Checkpoint**: All team members can run `npm run dev` + `python -m uvicorn ... --reload`

#### 11:00 AM - 1:00 PM: Core Backend Setup (2 hours)
- [ ] Initialize FastAPI project structure
- [ ] Create basic endpoints: `/search`, `/analyze`
- [ ] Set up environment variables (.env)
- [ ] Import Steel.dev SDK, test API connectivity
- [ ] Stub out OpenRouter LLM client

**Deliverable**: Backend running on `localhost:8000`, health check endpoint works

#### 1:00 - 2:00 PM: Attend Steel.dev Workshop
- [ ] Take notes on Steel.dev API best practices
- [ ] Ask questions about search, crawling, rate limits
- [ ] Get tips on browser automation edge cases

#### 2:00 PM - 5:00 PM: Steel.dev Integration (3 hours)
- [ ] Implement Steel search function (queries web via browser API)
- [ ] Extract results: URL, title, snippet, content preview
- [ ] Handle errors: timeouts, rate limits, invalid queries
- [ ] Test with sample queries (3-5 test searches)

**Deliverable**: Working `/search` endpoint that returns 10 web results with extracted content

#### 5:00 PM - 6:00 PM: Dinner Break
- [ ] Team recharge 🍽️

#### 6:00 PM - 9:00 PM: Bias Detection Core (3 hours)
- [ ] Create bias detection prompts for 6 categories:
  - Political Bias
  - Corporate/Celebrity Bias
  - Scientific Bias
  - Climate Bias
  - Emotional Bias
  - Confirmation Bias
- [ ] Implement LLM service (OpenRouter API calls)
- [ ] Parse LLM responses → structured bias scores
- [ ] Create `/analyze` endpoint

**Deliverable**: Working bias analysis for 1 sample result

#### 9:00 PM - 11:30 PM: Frontend Scaffolding & Integration (2.5 hours)
- [ ] Initialize React app (Vite recommended)
- [ ] Create SearchBar component with input
- [ ] Implement API client for backend
- [ ] Create basic results display
- [ ] Connect front → back: working search flow

**Deliverable**: User can enter search query in web UI and see (unanalyzed) results

#### 11:30 PM - 1:00 AM: Bias Scoring Integration (1.5 hours)
- [ ] Implement result ranking service (sort by bias)
- [ ] Test full pipeline: search → analyze → rank
- [ ] Fix bugs in LLM parsing or Steel.dev calls

**Deliverable**: Full end-to-end search + bias analysis working

#### 1:00 AM - 3:00 AM: Frontend Polish (2 hours)
- [ ] Create BiasIndicator component (colored badges)
- [ ] Add bias score visualization (charts or gauges)
- [ ] Improve ResultCard styling
- [ ] Add loading states & error messages

**Deliverable**: Frontend looks polished, results are clearly readable

#### 3:00 AM - 5:00 AM: Break & Sleep
- [ ] Team rest (sleep rotation if possible)

---

### Sunday, September 13

#### 5:00 AM - 7:00 AM: Testing & Bug Fixes (2 hours)
- [ ] Test 10+ search queries across bias categories
- [ ] Fix any crashes or parsing errors
- [ ] Test in Chrome, Firefox, Safari
- [ ] Check for typos, styling bugs

**Deliverable**: Stable, crash-free app

#### 7:00 AM - 9:00 AM: Demo Preparation (2 hours)
- [ ] Write demo script (what to show judges)
- [ ] Practice live search demo (2-3 example queries planned)
- [ ] Prepare slides: problem, solution, demo, wow factor
- [ ] Screenshot key moments for reference

**Deliverable**: Polished demo ready, slides created

#### 9:00 AM - 10:30 AM: Final Tweaks & Testing (1.5 hours)
- [ ] Address any remaining edge cases
- [ ] Performance optimization if needed
- [ ] Test demo queries one more time
- [ ] Final git commit & push to Devpost

#### 10:30 AM - 11:00 AM: Submission (30 minutes)
- [ ] Submit to Devpost: https://battle-of-the-schools.devpost.com/
- [ ] Include:
  - Repository link (GitHub)
  - Live demo link (if deployed)
  - Video walkthrough (optional but recommended)
  - Devpost description
- [ ] Confirm submission receipt

**🎉 SUBMITTED**

#### 11:00 AM - 12:30 PM: Break & Lunch
- [ ] Eat, recharge before judging

#### 12:30 PM - 2:30 PM: Judging
- [ ] Be ready to demo at assigned time
- [ ] Explain bias detection approach
- [ ] Answer technical questions
- [ ] Show off "wow" features

#### 4:00 - 5:00 PM: Finals & Awards
- [ ] Watch finalist presentations (if made top 3)
- [ ] Closing ceremony
- [ ] Celebrate! 🏆

---

## 📋 Task Breakdown by Priority

### Phase 1: MVP (Minimal Viable Product) - Saturday
**Goal**: Working end-to-end demo with all 6 bias categories

#### Backend
- [x] FastAPI setup
- [ ] Steel.dev integration (search + content extraction)
- [ ] LLM service (all 6 bias category prompts)
- [ ] Bias analysis pipeline
- [ ] Result ranking service
- [ ] Error handling & logging

#### Frontend
- [ ] React setup
- [ ] Search component
- [ ] Results display
- [ ] Bias indicators
- [ ] API client

### Phase 2: Polish - Late Saturday/Early Sunday
**Goal**: Production-quality UI/UX

- [ ] BiasChart visualization (radar/bar chart)
- [ ] Responsive design (mobile-friendly)
- [ ] Improved styling & branding
- [ ] Loading spinners & error messages
- [ ] Smooth animations

### Phase 3: Wow Factor - Early Sunday
**Goal**: Stand out to judges

- [ ] Explanation of bias reasoning
- [ ] Source credibility scoring
- [ ] Comparison view (multiple queries side-by-side)
- [ ] Export/share functionality
- [ ] Real-time WebSocket updates (nice to have)

### Phase 4: Demo & Submission - Sunday Morning
**Goal**: Flawless presentation

- [ ] Test all demo queries
- [ ] Prepare talking points
- [ ] Create slides
- [ ] Record video walkthrough
- [ ] Submit to Devpost

---

## 🔄 Daily Standup Template

**Use at least 3x daily (morning, evening, before sleep)**

```
What we shipped:
- [Feature/fix completed]
- [Another thing]

What we're doing next:
- [Next priority]
- [Then...]

Blockers:
- [Issue preventing progress] → [Action to resolve]
```

---

## 📊 Success Metrics

### By 6 PM Saturday
- ✅ Frontend and backend talking to each other
- ✅ Steel.dev returning search results
- ✅ LLM calls working (at least 2 bias categories)

### By 6 AM Sunday
- ✅ Full pipeline working (search → analyze → display)
- ✅ All 6 bias categories detecting
- ✅ Polished UI (not ugly)

### By 11 AM Sunday
- ✅ No crashes in 30+ search queries
- ✅ Demo script practiced 3+ times
- ✅ Submitted to Devpost

### Demo Excellence
- ✅ Query loads results in < 5 seconds
- ✅ Bias indicators are clear & color-coded
- ✅ Judges understand the concept in 30 seconds
- ✅ At least one "wow" moment (chart, explanation, speed, accuracy)

---

## 🎯 Stretch Goals (If Time Permits)

- [ ] WebSocket real-time result streaming
- [ ] User accounts & saved searches (Firebase?)
- [ ] Confidence scores for each bias detection
- [ ] "Source credibility" score (historical bias tracking)
- [ ] Browser extension version
- [ ] Multi-language support
- [ ] Dark mode toggle
- [ ] Advanced filters (source type, date range, region)
- [ ] Side-by-side comparison of biased vs. balanced sources
- [ ] Integration with fact-checking APIs

---

## 🚨 Risk Mitigation

| Risk | Likelihood | Mitigation |
|------|------------|-----------|
| Steel.dev API errors | Medium | Test extensively, have fallback (Google Search API?) |
| LLM response parsing failures | Medium | Strict JSON schema validation, fallback to defaults |
| Search timeouts (slow results) | Medium | Implement request timeout, show partial results |
| Team timezone confusion | Low | Clear Discord channels, shared calendar |
| API rate limits hit | Low | Monitor credits, batch requests efficiently |
| Frontend rendering bugs | Medium | Test in Chrome, Safari, Firefox early |
| Judges confused by concept | Low | Perfect your demo explanation, create clear slides |

---

## 💡 Key Decision Points

### Backend Framework
- **Choice**: FastAPI (async, fast, great for hackathons)
- **Alternative**: Flask (simpler but slower for this use case)

### Frontend Framework
- **Choice**: React + Vite (modern, fast build, great DX)
- **Alternative**: Vue (simpler) or vanilla JS (fastest)

### LLM Provider
- **Choice**: OpenRouter (access to multiple models, $500 credits)
- **Alternative**: Direct OpenAI ($) or Claude API (could work too)

### Deployment
- **Choice**: Deploy to Vercel (frontend) + Railway/Render (backend)
- **Alternative**: Heroku (free but slower) or fly.io

---

## 📝 Notes & Brainstorming

### Demo Queries to Showcase
1. "Climate change" → Should show climate denial articles
2. "Tesla CEO" → Should flag articles with bias about Elon Musk
3. "COVID vaccines" → Should detect anti-vax content
4. "2024 election" → Should show left/right political bias
5. "Renewable energy" → Should find emotional language

### Bias Category Insights
- **Political**: Look for party names, loaded adjectives (weak/strong)
- **Corporate**: Flag known controversial companies (Facebook, Amazon, Koch Industries)
- **Scientific**: Cite peer-reviewed sources, check statistical claims
- **Climate**: Keywords: "hoax", "Chinese conspiracy", "natural cycles"
- **Emotional**: Count exclamation marks, caps, fear words ("alarming", "shocking")
- **Confirmation**: Analyze result diversity (all one viewpoint = bias)

### Marketing Angles for Judges
- "AI-powered fact-checking for the information age"
- "Help users see their own biases"
- "Make media literacy accessible to everyone"
- "Use case: journalists, researchers, students, general public"

---

## 🔗 Important Links

- **Devpost Submission**: https://battle-of-the-schools.devpost.com/
- **Steel.dev Docs**: https://steel.dev/
- **OpenRouter**: https://openrouter.ai/
- **Event Discord**: https://discord.gg/TJyVckp7G
- **Hackathon Schedule**: Battle of the Schools 2026
- **Judging Criteria**: Technical excellence, creativity, execution, wow factor

---

## ✅ Final Checklist (Before Submission)

### Code Quality
- [ ] No console errors or warnings
- [ ] Proper error handling on all API calls
- [ ] Clean, readable code with comments where needed
- [ ] .env template created (.env.example)

### Testing
- [ ] 30+ different search queries tested
- [ ] Results load < 5 seconds (acceptable for hackathon)
- [ ] No crashes on edge cases (empty queries, special characters, etc.)
- [ ] Mobile responsive (tested on 2 screen sizes)

### Documentation
- [ ] README.md complete
- [ ] Setup instructions clear
- [ ] API endpoints documented
- [ ] How to run locally clearly explained

### Submission
- [ ] GitHub repo pushed & public
- [ ] Devpost link added to repo
- [ ] Video walkthrough recorded (< 3 min)
- [ ] Slides look professional
- [ ] Team bios/photos if Devpost requires

### Demo Readiness
- [ ] Demo script rehearsed 5+ times
- [ ] 3-5 "test" queries pre-planned
- [ ] Live internet connection tested
- [ ] Backup plan if wifi fails (video on phone?)
- [ ] Team knows who's speaking when

---

## 🎊 Celebration Plan

When you win (and you will! 💪):
- [ ] Celebrate with team
- [ ] Post on social media
- [ ] Thank sponsors in follow-up
- [ ] Consider commercializing post-hackathon
- [ ] Submit to tech blogs (if impressive enough)

**Good luck! 🚀**
