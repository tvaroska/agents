# Quick Start Guide

Get your stock research agent running in 5 minutes!

## 1. Install Dependencies

```bash
cd /home/boris/agents/news

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install packages
pip install google-adk python-dotenv
```

## 2. Get API Key

Visit [Google AI Studio](https://aistudio.google.com/app/apikey) and create an API key.

## 3. Configure Environment

```bash
# Create .env file
cat > .env << EOF
GOOGLE_API_KEY=your_api_key_here
GOOGLE_GENAI_USE_VERTEXAI=FALSE
EOF
```

Replace `your_api_key_here` with your actual API key.

## 4. Run the Agent

### Option A: Web UI (Recommended)

```bash
adk web
```

Then:
- Open browser to the URL shown (usually http://localhost:8000)
- Select `stock_research_agent`
- Type: "Research news for AAPL"
- Wait for the agent to generate the report

### Option B: Terminal

```bash
adk run
```

Type: "Research news for TSLA"

### Option C: Python Script

```bash
python example.py
```

## Example Queries

Try these prompts:

```
Research news for AAPL
Find recent articles about GOOGL stock
What's the latest news on NVDA?
Create a research report for TSLA
```

## What You'll Get

A comprehensive research report with:
- Executive summary
- Key developments from the last 24 hours
- Detailed article summaries with sources
- Market sentiment analysis
- Key themes and trends

The report is automatically saved as a markdown artifact.

## Troubleshooting

**Error: "API key not configured"**
- Check your .env file exists and has the correct API key

**Error: "Module not found: google.adk"**
- Run: `pip install google-adk`

**No results found**
- Try a more popular stock (AAPL, GOOGL, TSLA, NVDA, MSFT)
- Check the ticker symbol is correct

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [CLAUDE.md](CLAUDE.md) for ADK framework details
- Modify `agent.py` to customize the report format
- Build multi-agent systems for deeper analysis

---

Need help? Check the [ADK Documentation](https://github.com/google/adk-docs)
