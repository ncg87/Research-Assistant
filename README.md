# Research Assistant

## Overview
Research Assistant is a command-line tool that automates academic research by combining arXiv paper discovery with Large Language Model (LLM) analysis. Through an interactive CLI interface, researchers can explore topics, analyze papers, and discover new research directions with real-time progress tracking.

## Features
- **Interactive CLI**: User-friendly command-line interface with menus and progress tracking
- **Real-time Progress**: Visual feedback on search, analysis, and saving phases
- **Multi-LLM Support**: Compatible with multiple LLM providers (Claude, GPT-4, LLaMA, Gemini)
- **Concurrent Processing**: Efficient parallel processing of papers and research topics
- **Research Synthesis**: Generates topic summaries and identifies new research directions
- **Result Export**: Structured saving of research results and analyses

## Installation

### Prerequisites
- Python 3.8+

### Required API Keys
Create a `.env` file in the project root with at least one API key:
```
CLAUDE_API_KEY=your_claude_key
OPENAI_API_KEY=your_openai_key
LLAMA_API_KEY=your_llama_key
GEMINI_API_KEY=your_gemini_key
```

### Setup
1. Clone the repository
```bash
git clone https://github.com/yourusername/research-assistant.git
cd research-assistant
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

## CLI Usage

### Starting the Interface
```bash
python interface.py
```

### Main Menu Options
1. **Start New Research**: Begin a new research topic
2. **Settings**: Configure tool parameters
3. **Exit**: Close the application

### Research Flow
1. Enter your research topic when prompted
2. Watch real-time progress through three phases:
   - Search Phase: Finding and filtering relevant papers
   - Analysis Phase: Processing paper content
   - Saving Phase: Storing results

### Viewing Results
After analysis completes, you can:
- Save individual topic analyses
- View detailed results
- Continue research on generated topics
- Start new research
- Modify settings

### Settings Configuration
Through the CLI, you can adjust:
- Number of research topics (default: 5)
- Maximum papers per topic (default: 3)
- LLM provider (based on available API keys)
- Save directory for results

### Progress Display
The CLI shows real-time progress with:
- Color-coded progress bars for each phase
- Current operation status
- Paper and topic tracking
- Detailed status messages

## Requirements
```
arxiv==2.0.0
anthropic==0.8.1
openai==1.12.0
google-generativeai==0.3.2
PyMuPDF==1.23.8
rich==13.7.0
python-dotenv==1.0.1
llamaapi==0.1.38
```

## Output Structure
Research results are saved in a structured format:
```
research_results/
├── topic_name_timestamp/
│   ├── metadata.json
│   ├── topic1.json
│   ├── topic2.json
│   └── ...
```

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Credits
Inspired by [Automated-AI-Web-Researcher-Ollama](https://github.com/TheBlewish/Automated-AI-Web-Researcher-Ollama)

## Troubleshooting

### Common Issues
1. **API Rate Limits**: Adjust `tokens_per_minute` in settings if hitting rate limits
2. **Memory Usage**: Reduce `max_papers_per_topic` for lower memory consumption
3. **PDF Processing**: Ensure proper permissions for paper downloads

### Debug Logs
Logs are stored in the `logs/` directory:
- `llm_search.log`: Paper discovery logs
- `llm_analyzer.log`: Analysis process logs
- `research_assistant.log`: General operation logs