# Munger - Your Personal Charlie Munger Advisor

A CLI application that acts as your personal advisor, speaking with the wisdom and style of Charlie Munger. Unlike generic AI assistants, Munger knows you deeply - your life stages, events, concerns, and dreams - and gives candid, personalized advice using Munger's famous mental models and latticework thinking.

## Features

- **Personalized Advice**: Builds a deep understanding of you through your profile, personal charter, and life events
- **Munger's Voice**: Responses in Charlie Munger's distinctive style - direct, wise, with dry wit
- **Mental Models**: Applies Munger's famous latticework of mental models to your questions
- **RAG-Powered**: Retrieves relevant Munger wisdom to inform responses
- **Privacy-First**: All data stored locally on your machine
- **Life Event Tracking**: Record significant events that shape your advisor's understanding

## Installation

```bash
# Clone the repository
git clone https://github.com/yanmingcao/munger.git
cd munger

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

## Configuration

Set your LLM API key:

```bash
# For OpenAI (default)
export MUNGER_OPENAI_API_KEY="your-api-key"

# For Anthropic
export MUNGER_LLM_PROVIDER="anthropic"
export MUNGER_ANTHROPIC_API_KEY="your-api-key"

# For Kimi (Moonshot AI)
export MUNGER_LLM_PROVIDER="kimi"
export MUNGER_KIMI_API_KEY="your-api-key"
# Optional: specify a different model (default: kimi-k2-turbo-preview)
export MUNGER_KIMI_MODEL="kimi-k2-turbo-preview"

# For SiliconFlow
export MUNGER_LLM_PROVIDER="siliconflow"
export MUNGER_SILICONFLOW_API_KEY="your-api-key"
# Optional: specify a different model (default: deepseek-ai/DeepSeek-V3)
export MUNGER_SILICONFLOW_MODEL="deepseek-ai/DeepSeek-V3"

# Language setting (english or chinese)
export MUNGER_LANGUAGE="chinese"
export MUNGER_SILICONFLOW_MODEL="deepseek-ai/DeepSeek-V3"
```

## Quick Start

```bash
# 1. Initialize your profile
munger init

# 2. Seed the wisdom knowledge base
munger ingest seed

# 3. Define your personal charter (values, goals)
munger charter edit

# 4. Ask for advice
munger ask "Should I take this job offer that requires relocation?"

# 5. Start an interactive chat
munger chat
```

## Commands

### Profile Management

```bash
munger init           # Set up your profile
munger profile show   # View your profile
munger profile edit   # Update your profile
```

### Personal Charter

Your charter defines your core values, non-negotiables, and life goals:

```bash
munger charter show   # View your charter
munger charter edit   # Update your charter
munger charter values "Family first" "Integrity" "Learning"  # Quick update values
```

### Life Events

Record significant events to help Munger understand your journey:

```bash
munger event quick                    # Interactive event recording
munger event add --title "Got promoted" --desc "Promoted to Senior Director" --category career
munger event list                     # View recent events
munger event list --category family   # Filter by category
```

Event categories: `career`, `family`, `health`, `financial`, `relationship`, `education`, `personal_growth`, `other`

### Getting Advice

```bash
# Quick question
munger ask "What should I consider when evaluating this investment?"

# With additional context
munger ask "Should I change careers?" --context "I'm 45, have two kids, and feel unfulfilled"

# Interactive chat session
munger chat

# Reflection session (reviews your recent events and provides insights)
munger review
```

### Knowledge Base

```bash
munger ingest seed                    # Load built-in Munger wisdom
munger ingest add <url>               # Add wisdom from a URL
munger ingest add <file.pdf>          # Add wisdom from a PDF
munger ingest status                  # Show knowledge base status
munger ingest search "mental models"  # Search the knowledge base
```

### System Status

```bash
munger status  # Check setup status
```

## How It Works

### Three-Layer Context Model

1. **Stable Profile**: Your background, career stage, risk tolerance, time horizon
2. **Preferences**: How you like advice delivered (blunt, balanced, gentle)
3. **Session Context**: Current emotional state, immediate concerns

### Personal Charter

Define what matters most:
- **Core Values**: What you stand for (in priority order)
- **Non-Negotiables**: What you'll never compromise on
- **Long-Term Goals**: Your major life aspirations
- **Anti-Goals**: What you actively want to avoid

### Life Events

Track significant moments that shape the advisor's understanding:
- Career changes, promotions, setbacks
- Family milestones
- Health events
- Financial decisions
- Relationship changes

### Mental Models Applied

Munger draws from his famous latticework:
- **Inversion**: What would make this fail?
- **Incentives**: What motivates the players?
- **Circle of Competence**: Are you in your zone?
- **Margin of Safety**: What's your buffer?
- **Opportunity Cost**: What are you giving up?
- And 25+ more models...

## Example Interaction

```
$ munger ask "I'm considering leaving my stable corporate job to start a startup. What do you think?"

Let me consider your situation carefully.

You're 45, in a senior position, with family obligations - this isn't a decision to take lightly. Let me apply some mental models:

**Inversion**: What would guarantee this fails? Running out of money with kids depending on you. Burning bridges with no fallback. Starting without validating the idea.

**Opportunity Cost**: Your corporate job isn't just salary - it's also stability, health insurance, the option value of your reputation. What's the true cost of giving that up?

**Margin of Safety**: Do you have 18-24 months of runway? If not, you're gambling with your family's security.

My honest assessment: The fact that you feel unfulfilled is real and matters. But the "startup or nothing" framing is a false choice. Consider:

1. Can you validate the idea while still employed?
2. Is there a bridge option - consulting, part-time, sabbatical?
3. Have you discussed the real risks with your spouse?

The best time to start a company is when failure won't ruin you. Are you there?
```

## Project Structure

```
munger/
├── src/munger/
│   ├── cli/           # CLI commands
│   ├── core/          # Domain models, config
│   ├── db/            # Database and vector store
│   ├── ingest/        # Content ingestion
│   ├── persona/       # Munger persona, mental models
│   └── advisor/       # Advice generation
├── tests/
└── pyproject.toml
```

## Data Storage

All data is stored locally:
- **Location**: `~/.local/share/munger/` (Linux/Mac) or `%APPDATA%/munger/` (Windows)
- **Database**: SQLite for profiles, events, conversations
- **Vector Store**: ChromaDB for wisdom retrieval

## Contributing

Contributions welcome! Areas of interest:
- Additional Munger source materials
- More mental models
- Improved persona prompts
- Better context retrieval

## License

MIT License

## Acknowledgments

Inspired by the wisdom of Charlie Munger (1924-2023), who taught us that the best investment you can make is in yourself, and the best thing you can do is help others know more.

*"The best thing a human being can do is to help another human being know more."* - Charlie Munger
