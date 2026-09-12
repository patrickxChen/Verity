# Verity: AI Search Engine for Bias Detection

An intelligent search engine powered by AI agents that detects and flags various forms of biases in online content.

## 🎯 Project Overview

Verity is an AI-driven web search application that identifies multiple categories of bias in real-time search results:

- **Political Bias** - Left/right leaning perspectives
- **Corporate Bias** - Unethical or controversial companies/celebrities
- **Scientific Bias** - Misleading or false scientific claims
- **Climate Bias** - Climate change denial or misinformation
- **Emotional Bias** - Emotionally charged or manipulative language
- **Confirmation Bias** - Results that reinforce existing beliefs

## 🚀 Key Features

- **Automated Web Scraping**: Uses Steel.dev browser API to autonomously crawl and analyze web content
- **Multi-Category Bias Detection**: Analyzes search results across 6+ bias categories
- **Real-Time Analysis**: Processes search queries and returns bias scores instantly
- **User-Friendly Interface**: Clean web interface for running searches and viewing results
- **Bias Severity Scoring**: Quantifies bias level from 1-10 for each category
- **Source Credibility**: Tracks source reliability and known biases

## 📊 How It Works

1. **User Input**: Enters a search query or topic to analyze
2. **Web Crawling**: AI agent uses Steel.dev to search the web and gather results
3. **Content Analysis**: LLM analyzes each result for bias patterns
4. **Scoring**: Assigns bias scores across all categories
5. **Visualization**: Displays results with bias indicators and breakdowns
6. **Explanation**: Provides reasoning for detected biases

## 🏆 Hackathon Context

Built for **Battle of the Schools** Steel.dev Track:
- **Event**: Battle of the Schools (September 12-13, 2026)
- **Venue**: Bahen Centre, University of Toronto
- **Track**: Steel.dev Web Agents
- **Sponsor**: Steel.dev (Web Agents Track)
- **Prize**: $1,000 cash + $600 Steel Pro credits + $500 OpenRouter credits for 1st place
- **Submission Deadline**: Sunday, September 13 @ 11:00 AM
- **Devpost**: https://battle-of-the-schools.devpost.com/

## 🛠️ Technology Stack

See [TECH.md](TECH.md) for detailed technical specifications.

## 📖 Project Structure

```
verity/
├── README.md           # This file
├── CONTEXT.md          # Project background & requirements
├── TECH.md             # Technology stack & architecture
├── PROGRESS.md         # Implementation roadmap
├── backend/            # Flask/FastAPI server
├── frontend/           # React web interface
├── agents/             # AI agent logic using Steel.dev
└── tests/              # Test suite
```

## 🎓 Team & Attribution

Built by the team for Battle of the Schools 2026

## 📝 License

MIT License
