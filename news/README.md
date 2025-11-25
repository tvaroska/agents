# Stock News Research Agent

An AI-powered agent built with Google's Agent Development Kit (ADK) that researches stock news from the last 24 hours and generates comprehensive research reports saved as artifacts.

## Features

- **Google Search Integration**: Uses ADK's built-in Google Search tool for real-time news discovery
- **Automated Research**: Searches multiple queries to find comprehensive stock news coverage
- **Structured Reports**: Generates professional markdown research reports
- **Artifact Storage**: Automatically saves reports as artifacts for easy retrieval
- **Sentiment Analysis**: Analyzes overall market sentiment from news articles
- **Source Attribution**: Includes proper citations and links to original sources

## Prerequisites

- Python 3.8 or higher
- Google AI Studio API key OR Google Cloud Project with Vertex AI enabled
- Internet connection for Google Search

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd /home/boris/agents/news
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env and add your credentials
   nano .env  # or use your preferred editor
   ```

### Option 1: Google AI Studio (Development)

Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey) and add to `.env`:

```bash
GOOGLE_API_KEY=your_api_key_here
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

### Option 2: Vertex AI (Production)

Configure your Google Cloud project in `.env`:

```bash
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=TRUE
```

Then authenticate:
```bash
gcloud auth application-default login
```

## Usage

### Interactive Web UI (Recommended)

Launch the ADK Developer UI in your browser:

```bash
adk web
```

Then:
1. Select the `stock_research_agent` from the dropdown
2. Enter a stock ticker symbol (e.g., "AAPL", "GOOGL", "TSLA", "NVDA")
3. The agent will search for news and generate a comprehensive report
4. The report will be saved as an artifact automatically

### Terminal Interaction

Run the agent in your terminal:

```bash
adk run
```

Then type your request:
```
Research news for AAPL stock
```

### API Server

Start a local FastAPI server:

```bash
adk api_server
```

Then send requests to `http://localhost:8000`

## Example Queries

Here are some example prompts to use with the agent:

- `Research news for TSLA`
- `Find recent articles about AAPL stock`
- `What's the latest news on GOOGL in the last 24 hours?`
- `Create a research report for NVDA`
- `Search for news about META stock`

## How It Works

1. **User Input**: You provide a stock ticker symbol (e.g., "AAPL")

2. **Google Search**: The agent uses the built-in Google Search tool to find:
   - Recent news articles (last 24 hours)
   - Earnings announcements
   - Market analysis
   - Company developments

3. **Analysis**: The agent analyzes search results to:
   - Extract key developments
   - Identify themes and patterns
   - Assess market sentiment
   - Organize information chronologically

4. **Report Generation**: Creates a structured markdown report with:
   - Executive Summary
   - Key Developments
   - Detailed Article Summaries
   - Sentiment Analysis
   - Conclusions

5. **Artifact Storage**: The report is saved as a markdown artifact with timestamp

## Report Structure

Each research report includes:

```markdown
# Stock News Research Report: {TICKER}

## Executive Summary
Brief overview of key findings

## Key Developments
3-5 most important news items

## Detailed News Articles
Article 1: Title
- Source, Published time
- Summary and link

## Market Sentiment Analysis
Overall sentiment assessment

## Key Themes
Recurring topics across articles

## Conclusion
Summary and potential impact
```

## Project Structure

```
news/
├── __init__.py           # Package initialization
├── agent.py              # Main agent definition
├── .env.example          # Environment variables template
├── .env                  # Your actual credentials (gitignored)
├── .gitignore           # Git ignore rules
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── CLAUDE.md            # ADK documentation reference
```

## Agent Configuration

The agent is configured with:

- **Model**: `gemini-2.0-flash-exp` (supports built-in tools)
- **Tool**: `google_search` (built-in ADK tool)
- **Output**: Structured markdown research reports
- **Behavior**: Professional analyst persona with fact-based reporting

## Important Notes

### Built-in Tool Limitation

ADK built-in tools have a constraint: each agent can only use **one** built-in tool and **no other tools** can be combined with it. This agent uses the `google_search` built-in tool exclusively.

### Not Financial Advice

This agent provides research and analysis for informational purposes only. The output should NOT be considered as financial or investment advice. Always consult with a qualified financial advisor before making investment decisions.

### Search Results

- Results are limited to publicly available information via Google Search
- News coverage varies by stock popularity and market activity
- Some stocks may have limited recent news

## Troubleshooting

### "Agent not found" error

Make sure you're in the correct directory:
```bash
cd /home/boris/agents/news
adk web
```

### "API key not configured" error

Check your `.env` file:
```bash
cat .env
```

Make sure `GOOGLE_API_KEY` is set correctly.

### No search results

- Verify the ticker symbol is correct
- Try a more popular stock (e.g., AAPL, GOOGL, TSLA)
- Check your internet connection

### Import errors

Make sure dependencies are installed:
```bash
pip install -r requirements.txt
```

## Extending the Agent

### Add More Analysis

Modify the `instruction` in `agent.py` to include:
- Technical analysis sections
- Price movement correlation
- Industry comparison
- Historical context

### Custom Output Format

Change the report template in the instruction to generate:
- JSON format
- HTML reports
- Executive summaries only
- Specific sections

### Multi-Agent System

Combine with other agents:
```python
from google.adk import SequentialAgent
from news.agent import stock_research_agent
from analysis.agent import sentiment_agent

pipeline = SequentialAgent(
    name="stock_pipeline",
    sub_agents=[stock_research_agent, sentiment_agent]
)
```

## Development

### Running Tests

```bash
# Add your test commands here
pytest tests/
```

### Code Style

```bash
# Format code
black .

# Lint
pylint agent.py
```

## Resources

- [Google ADK Documentation](https://github.com/google/adk-docs)
- [Built-in Tools Guide](https://google.github.io/adk-docs/tools/built-in-tools/)
- [Gemini Models](https://ai.google.dev/models/gemini)
- [ADK GitHub](https://github.com/google/genai-adk)

## License

This project is provided as-is for educational and research purposes.

## Support

For issues related to:
- **ADK Framework**: Check [ADK Documentation](https://github.com/google/adk-docs)
- **This Agent**: Review this README and CLAUDE.md

---

**Disclaimer**: This tool is for research purposes only. Always verify information from multiple sources and consult professional financial advisors before making investment decisions.
