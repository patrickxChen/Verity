# Context: Bias Detective Project

## 🎯 Problem Statement

In the digital age, information bias is increasingly difficult to identify. Search results are often filtered through algorithmic bubbles, and content creators—intentionally or not—embed various biases into their work. Users struggle to:

- Identify whether sources lean toward specific political ideologies
- Recognize when companies/celebrities with questionable ethics are discussed
- Distinguish scientific consensus from fringe claims
- Spot emotionally manipulative language designed to trigger reactions
- Realize when their searches are reinforcing existing beliefs (confirmation bias)

**Bias Detective** provides a solution by automatically scanning web search results and flagging these biases in real-time.

## 🎪 Hackathon Context

### Event: Battle of the Schools
- **When**: September 12-13, 2026
- **Where**: Bahen Centre, University of Toronto
- **Scale**: 200+ student participants, 2 universities (U of T vs Waterloo)
- **Format**: 24-hour AI/ML hackathon with sponsor tracks

### Track: Steel.dev Web Agents
- **Sponsor**: Steel.dev (https://steel.dev/)
- **Challenge**: Build creative AI solutions involving browser use
- **Technology**: Steel browser API for cloud-based web automation
- **Why Relevant**: Perfect use case for autonomous web scraping and analysis

### Prize Structure
- **1st Place**: $1,000 cash + $600 Steel Pro credits + $500 OpenRouter credits
- **2nd Place**: Gaming peripherals + $300 Steel Pro credits
- **3rd Place**: JBL speakers + $100 Steel Pro credits
- **Wildcards**: Steel Computer Wildcard ($500) + Most Unhinged Idea ($200 UberEats)

### School Points System
- Track placement contributes to overall university score
- 1st: 1000 pts | 2nd: 600 pts | 3rd: 400 pts | Honorable Mention: 200 pts
- Winning team represents their school during finals presentation

## 📋 Bias Categories Targeted

### 1. Political Bias
- **Definition**: Left or right-leaning perspectives in news/analysis
- **Detection Signals**: 
  - Language favoring specific political parties
  - Selective reporting of facts
  - Partisan framing of issues
- **Example**: Article about climate policy with heavy partisan language

### 2. Corporate/Celebrity Bias
- **Definition**: Coverage of ethically questionable companies or celebrities
- **Detection Signals**:
  - Positive framing of companies with scandal histories
  - Omission of known controversies
  - Whitewashing language
- **Example**: Articles about a company accused of environmental violations

### 3. Scientific Bias
- **Definition**: Misrepresentation or denial of scientific consensus
- **Detection Signals**:
  - Claims contradicting peer-reviewed research
  - Appeal to fringe experts vs. mainstream science
  - Misuse of statistics or cherry-picked data
- **Example**: Climate change denial articles or vaccine misinformation

### 4. Climate Bias
- **Definition**: Denial or minimization of climate change
- **Detection Signals**:
  - "Climate change isn't real" rhetoric
  - Extreme-case dismissals ("one cold winter disproves warming")
  - Fossil fuel industry talking points
- **Example**: Articles downplaying climate crisis severity

### 5. Emotional Bias
- **Definition**: Manipulative language designed to trigger emotional responses
- **Detection Signals**:
  - All-caps words, excessive punctuation
  - Fear-mongering or outrage-inducing language
  - Loaded adjectives without facts
- **Example**: Sensationalized headlines with emotional triggers

### 6. Confirmation Bias
- **Definition**: Search results that reinforce existing beliefs
- **Detection Signals**:
  - Results predominantly one-sided on divisive topics
  - Lack of opposing viewpoints
  - Echo chamber effect in result clustering
- **Example**: Searching a divisive topic yields only one perspective

## 🎬 User Journey

1. **Search**: User enters query (e.g., "climate change impacts")
2. **Crawl**: Steel.dev agent autonomously searches web and gathers results
3. **Analyze**: LLM processes each result for bias patterns
4. **Score**: Each result gets bias scores (1-10) per category
5. **Display**: Results ranked by overall bias level with visual indicators
6. **Explain**: User can click results to see reasoning behind bias detection
7. **Export**: Option to save report or share findings

## 💡 Competitive Advantages

- **Real-time Bias Scoring**: Instant analysis vs. manual checking
- **Multi-Category Analysis**: 6+ bias types in one tool vs. single-focus tools
- **Explainable AI**: Users understand *why* something was flagged
- **Visual Dashboard**: Easy-to-read bias indicators and charts
- **Scalable**: Steel.dev backend handles multiple concurrent searches

## 🤝 Stakeholders

### Internal
- **Development Team**: Building the application
- **UX Designer**: Interface and user experience

### External
- **Steel.dev Team**: Providing API support and beta access
- **Judges**: Evaluating technical excellence, creativity, execution
- **Users**: Students, researchers, journalists seeking bias awareness

## 📅 Timeline

- **Saturday 9 AM**: Registration & kickoff
- **Saturday 10 AM**: Opening ceremony, Steel.dev track announced
- **Saturday 1 PM**: Steel.dev workshop (BA2135)
- **Saturday-Sunday**: 24-hour hacking sprint
- **Sunday 11 AM**: Submission deadline (Devpost)
- **Sunday 12:30 PM**: Judging begins
- **Sunday 4 PM**: Finalist presentations
- **Sunday 4:30 PM**: Closing ceremony & winner announcement

## 🎨 Success Criteria

### Technical Excellence
- Stable Steel.dev integration
- Accurate bias detection across all 6+ categories
- Sub-2 second query response time
- Handles 100+ concurrent searches without degradation

### Creativity
- Novel approach to bias detection
- Interesting visualizations
- Unexpected use of Steel.dev capabilities
- Potential for real-world impact

### Execution
- Polished, bug-free interface
- Clear explanations for bias detection
- Professional presentation
- Solid demo performance under pressure

### Wow Factor
- Surprising accuracy in detecting subtle biases
- Engaging user interface
- Thoughtful consideration of edge cases
- Potential commercialization angle

## 📚 Research Resources

- **Steel.dev Docs**: https://steel.dev/ (API reference, examples)
- **Bias Research**: Papers on media bias, political slant, misinformation
- **LLM APIs**: OpenRouter (credits provided), OpenAI, Anthropic Claude
- **Battle of Schools Info**: https://battle-of-the-schools.devpost.com/

## 🚫 Out of Scope

- Real-time fact-checking (too slow for hackathon scope)
- Comprehensive historical bias tracking
- Multi-language support
- Deep learning custom models
- Production-grade deployment infrastructure

## ✅ Success Metrics

- **Functional**: Working demo with live search capability
- **Accurate**: Correctly identifies biases 80%+ of the time (user testing)
- **Fast**: Results within 5 seconds per query
- **Polish**: Professional UI with clear bias indicators
- **Wow**: Judges or audience members impressed by capability or insight
