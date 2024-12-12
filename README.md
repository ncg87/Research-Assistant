# Research Assistant

## Overview
Research Assistant is a powerful tool that automates academic research by combining arXiv paper discovery with Large Language Model (LLM) analysis. The system helps researchers explore topics deeply by automatically finding relevant papers, analyzing their content, and suggesting new research directions.

## Features
- **Multi-LLM Support**: Compatible with multiple LLM providers (Claude, GPT-4, LLaMA, Gemini)
- **Concurrent Processing**: Efficient parallel processing of papers and research topics
- **Intelligent Paper Selection**: Automatically evaluates paper relevance through title and abstract analysis
- **Deep Content Analysis**: Analyzes full paper content to extract key findings and methodologies
- **Research Synthesis**: Generates topic summaries and identifies new research directions
- **Progress Tracking**: Real-time visual progress tracking with detailed status updates
- **Result Export**: Structured saving of research results and analyses

## Installation

### Prerequisites
- Python 3.8+
- Poetry (recommended for dependency management)

### Required API Keys
Create a `.env` file in the project root with your API keys:
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

## Usage

### Command Line Interface
Run the assistant using:
```bash
python interface.py
```

The CLI provides options to:
- Start new research
- Adjust settings
- View and export results
- Continue research based on generated directions

### Configuration
Modify `settings.json` to customize:
- Number of research topics
- Maximum papers per topic
- Default LLM
- Save directory

### Example Usage
```python
from ResearchAssistant import ResearchAssistant

# Initialize with preferred LLM
assistant = ResearchAssistant(llm_name="CLAUDE")

# Start new research
results = assistant.new_research("quantum computing applications in cryptography")
```

## Project Structure

### Core Components
- `ResearchAssistant.py`: Main orchestrator class
- `concurrent_search.py`: Handles paper discovery and filtering
- `concurrent_analysis.py`: Manages paper analysis and synthesis
- `llm_wrapper.py`: Unified interface for different LLM providers
- `interface.py`: Command-line interface implementation

### Supporting Modules
- `structures.py`: Data structures and models
- `utils.py`: Helper functions for paper processing
- `prompts.py`: LLM prompt templates
- `saver.py`: Result storage and export
- `progress/`: Progress tracking and visualization

## Rate Limiting
The system includes sophisticated rate limiting for API calls:
- Token-based rate limiting with rolling windows
- Concurrent request management
- Automatic request retry with exponential backoff

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

## Acknowledgments
- ArXiv for providing research paper access
- Anthropic, OpenAI, Meta, and Google for LLM APIs

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

## Future Development
- [ ] Web interface implementation
- [ ] Additional LLM provider support
- [ ] Enhanced paper filtering algorithms
- [ ] Citation network analysis
- [ ] Research visualization tools
