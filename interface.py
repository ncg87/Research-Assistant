import os
import time
from typing import Dict, Optional
import sys
from dataclasses import dataclass, asdict
import json
import logging
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich.layout import Layout
from rich.text import Text
from rich import box
from rich.live import Live
from datetime import datetime

from ResearchAssistant import ResearchAssistant
from structures import ResearchAnalysisResult
from config import Config
# Update imports to use progress package
from progress import ProgressLogHandler, StatusProgress, setup_logging_for_progress, ResearchStage, ProgressEvent, ProgressTracker, ResearchProgressMonitor

@dataclass
class ResearchSettings:
    """Settings for the research process"""
    num_research_topics: int = 5
    max_papers_per_topic: int = 3
    llm_name: str = "CLAUDE"
    save_dir: str = "./research_results"

class ResearchCLI:
    def __init__(self):
        self.console = Console()
        self.config = Config()
        if not self.config.has_any_api_keys():
            self.settings = None
            return
            
        default_model = self.config.get_default_model()
        if default_model:
            self.settings = ResearchSettings(llm_name=default_model)
            self.assistant = ResearchAssistant(
                self.settings.llm_name,
                self.settings.save_dir
            )
        self.current_results: Optional[ResearchAnalysisResult] = None

    def _load_settings(self) -> ResearchSettings:
        """Load settings from file or create default"""
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                return ResearchSettings(**json.load(f))
        return ResearchSettings()

    def _save_settings(self):
        """Save current settings to file"""
        with open("settings.json", "w") as f:
            json.dump(asdict(self.settings), f, indent=2)

    def show_welcome(self):
        """Display welcome message and logo"""
        self.console.clear()
        welcome_text = """
╔══════════════════════════════════════════════════════════════╗
║                   Research Assistant v1.0                     ║
║----------------------------------------------------------  ║
║  An AI-powered tool for academic research and exploration    ║
║  Using arXiv papers and Large Language Models                ║
╚══════════════════════════════════════════════════════════════╝
        """
        self.console.print(Panel(welcome_text, style="bold blue"))

    def check_api_keys(self):
        """Display message when no API keys are configured"""
        if not self.config.has_any_api_keys():
            self.console.print("\n[red]No API keys found![/red]")
            self.console.print("Please add at least one API key to the .env file:")
            self.console.print("Available options:")
            self.console.print("- CLAUDE_API_KEY")
            self.console.print("- OPENAI_API_KEY")
            self.console.print("- LLAMA_API_KEY")
            self.console.print("- GEMINI_API_KEY")
            self.console.print("\nPress [3] to exit and add API keys.")
            return Prompt.ask("Select an option", choices=["3"])

    def show_menu(self) -> str:
        """Display main menu and get user choice"""
        self.check_api_keys()
        menu = Table(show_header=False, box=box.ROUNDED)
        menu.add_row("[1] Start New Research")
        menu.add_row("[2] Settings")
        menu.add_row("[3] Exit")
        
        self.console.print("\n", Panel(menu, title="Main Menu", border_style="blue"))
        return Prompt.ask("Select an option", choices=["1", "2", "3"])

    def show_settings(self):
        """Display and modify settings"""
        if not self.config.has_any_api_keys():
            self.console.print("[red]Cannot access settings without API keys configured.[/red]")
            return
        
        self.console.clear()
        while True:
            settings_table = Table(title="Current Settings", box=box.ROUNDED)
            settings_table.add_column("Setting", style="cyan")
            settings_table.add_column("Value", style="green")
            
            settings_dict = asdict(self.settings)
            for key, value in settings_dict.items():
                settings_table.add_row(key.replace("_", " ").title(), str(value))
            
            self.console.print(settings_table)
            
            settings_menu = Table(show_header=False, box=box.ROUNDED)
            settings_menu.add_row("[1] Change Number of Research Topics")
            settings_menu.add_row("[2] Change Maximum Papers per Topic")
            settings_menu.add_row("[3] Change LLM Model")
            settings_menu.add_row("[4] Change Save Directory")
            settings_menu.add_row("[5] Return to Main Menu")
            
            self.console.print("\n", Panel(settings_menu, title="Settings Menu", border_style="blue"))
            choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5"])
            
            if choice == "1":
                self.settings.num_research_topics = IntPrompt.ask("Enter number of research topics", default=5)
            elif choice == "2":
                self.settings.max_papers_per_topic = IntPrompt.ask("Enter maximum papers per topic", default=3)
            elif choice == "3":  # Change LLM Model
                available_models = self.config.get_available_models()
                if not available_models:
                    self.console.print("[red]No API keys configured. Cannot change model.[/red]")
                    continue
                    
                new_model = Prompt.ask(
                    "Select LLM model",
                    choices=available_models,
                    default=available_models[0]
                )
            
                if new_model != self.settings.llm_name:
                    self.settings.llm_name = new_model
                    self.assistant.update_model(new_model)  # Use new update_model method
                    self.console.print(f"[green]Successfully switched to {new_model}[/green]")
            elif choice == "4":
                self.settings.save_dir = Prompt.ask("Enter save directory", default="./research_results")
            elif choice == "5":
                self._save_settings()
                break
            
            self.console.clear()

    def show_research_progress(self, topic: str) -> ResearchAnalysisResult:
        """Display research progress with real-time updates from logs"""
        self.console.clear()
        research_panel = Panel(
            f"[bold]Researching:[/bold] {topic}\n\n"
            "[dim]The research process involves multiple stages:[/dim]\n"
            "1. Searching for relevant papers\n"
            "2. Analyzing research content\n"
            "3. Saving results",
            title="Research Progress",
            border_style="blue"
        )
        self.console.print(research_panel)

        # Setup fresh logging for this session
        setup_logging_for_progress()

        with StatusProgress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="green", finished_style="green"),
            TaskProgressColumn(),
            console=self.console,
            expand=True,
            refresh_per_second=10
        ) as progress:
            # Create and add the log handler
            progress_handler = ProgressLogHandler(progress)  # Removed tracker argument
            
            # Add handler to all relevant loggers
            loggers = ['concurrent_search', 'concurrent_analysis', 'utils', 'llm_wrapper', 'ResearchAssistant']
            for logger_name in loggers:
                logger = logging.getLogger(logger_name)
                logger.addHandler(progress_handler)

            try:
                # Run the research
                results = self.assistant.new_research(topic)
                return results
                
            finally:
                # Remove the progress handler
                for logger_name in loggers:
                    logger = logging.getLogger(logger_name)
                    logger.removeHandler(progress_handler)
    def _format_topic_for_file(self, analysis) -> str:
        """Format a research topic analysis for file output"""
        # Create a string builder
        output = []
        
        # Add decorative header
        output.append("=" * 80)
        output.append(f"Research Topic Analysis")
        output.append("=" * 80)
        output.append("")
        
        # Add main topic information
        output.append(f"Topic: {analysis.topic.topic}")
        output.append("-" * 40)
        output.append("")
        
        # Add topic summary
        output.append("Summary:")
        output.append("-" * 8)
        output.append(analysis.topic_summary)
        output.append("")
        
        # Add analyzed papers
        output.append("Analyzed Papers:")
        output.append("-" * 15)
        for i, (paper, paper_analysis) in enumerate(zip(analysis.topic.research_papers, analysis.paper_analyses), 1):
            output.append(f"\nPaper {i}: {paper.title}")
            output.append(f"Authors: {', '.join(str(author) for author in paper.authors)}")
            output.append(f"URL: {paper.url}")
            output.append("\nAnalysis:")
            output.append(paper_analysis)
            output.append("-" * 40)
        
        # Add new research direction
        output.append("\nNew Research Direction:")
        output.append("-" * 20)
        output.append(analysis.new_research)
        
        # Add timestamp
        output.append("\n" + "=" * 80)
        output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("=" * 80)
        
        return "\n".join(output)

    def save_topic_to_file(self, analysis, index: int) -> str:
        """Save a single topic analysis to a file"""
        try:
            # Create save directory if it doesn't exist
            save_dir = os.path.join(self.settings.save_dir, "topic_exports")
            os.makedirs(save_dir, exist_ok=True)
            
            # Create filename from topic and timestamp
            safe_topic = "".join(c if c.isalnum() else "_" for c in analysis.topic.topic[:30])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"topic_{index+1}_{safe_topic}_{timestamp}.txt"
            filepath = os.path.join(save_dir, filename)
            
            # Format and save the content
            content = self._format_topic_for_file(analysis)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
                
            return filepath
            
        except Exception as e:
            self.console.print(f"[red]Error saving topic to file: {e}[/red]")
            return None
                    
    def show_research_results(self, results: ResearchAnalysisResult):
        """Display research results and options"""
        self.console.clear()
        
        # Display summary table
        summary_table = Table(title="Research Results", box=box.ROUNDED)
        summary_table.add_column("#", style="dim", width=4)
        summary_table.add_column("Topic", style="cyan", width=40)
        summary_table.add_column("Papers", style="green", justify="center")
        summary_table.add_column("New Research Direction", style="yellow", width=40)
        summary_table.add_column("Actions", justify="center")
        
        for i, analysis in enumerate(results.research_analyses, 1):
            summary_table.add_row(
                str(i),
                analysis.topic.topic,
                str(len(analysis.paper_analyses)),
                analysis.new_research,
                f"[blue]Press {i} to save[/blue]"
            )
        
        self.console.print(summary_table)
        
        # Display options
        options_table = Table(show_header=False, box=box.ROUNDED)
        options_table.add_row("[1-5] Save Individual Topic")
        options_table.add_row("[N] Start New Research")
        options_table.add_row("[V] View Detailed Results")
        options_table.add_row("[C] Continue Research on Generated Topic")
        options_table.add_row("[S] Settings")
        options_table.add_row("[E] Exit")
        
        self.console.print("\n", Panel(options_table, title="Options", border_style="blue"))
        
        # Get user choice
        choices = ["N", "V", "C", "S", "E"] + [str(i) for i in range(1, len(results.research_analyses) + 1)]
        choice = Prompt.ask("Select an option", choices=choices).upper()
        
        # Handle numeric choices (saving topics)
        if choice.isdigit():
            idx = int(choice) - 1
            filepath = self.save_topic_to_file(results.research_analyses[idx], idx)
            if filepath:
                self.console.print(f"[green]Successfully saved topic to:[/green] {filepath}")
                self.console.print("\nPress Enter to continue...")
                input()
            return self.show_research_results(results)
        
        # Map other choices to return values
        choice_map = {
            "N": "1",
            "V": "2",
            "C": "3",
            "S": "4",
            "E": "5"
        }
        return choice_map[choice]
    
    def continue_research(self, results: ResearchAnalysisResult):
        """Continue research with one of the new research directions"""
        self.console.clear()
        
        # Display new research directions
        directions_table = Table(title="New Research Directions", box=box.ROUNDED)
        directions_table.add_column("#", style="dim", width=4)
        directions_table.add_column("Original Topic", style="cyan", width=40)
        directions_table.add_column("New Research Direction", style="yellow", width=60)
        
        for i, analysis in enumerate(results.research_analyses, 1):
            directions_table.add_row(
                str(i),
                analysis.topic.topic,
                analysis.new_research
            )
        
        self.console.print(directions_table)
        
        # Get user choice
        choice = IntPrompt.ask(
            "\nSelect a topic number to continue research",
            choices=[str(i) for i in range(1, len(results.research_analyses) + 1)]
        )
        
        # Get the selected new research direction
        selected_direction = results.research_analyses[choice - 1].new_research
        
        # Confirm with user
        self.console.print(f"\n[bold cyan]Selected Direction:[/bold cyan]")
        self.console.print(f"{selected_direction}")
        
        if Prompt.ask("\nContinue with this research direction?", choices=["y", "n"]) == "y":
            # Start new research with the selected direction
            return self.show_research_progress(selected_direction)
        return results

    def run(self):
        """Main CLI loop"""
        while True:
            self.show_welcome()
            choice = self.show_menu()
            
            if choice == "1":
                topic = Prompt.ask("\nEnter your research topic")
                self.current_results = self.show_research_progress(topic)
                while True:
                    next_choice = self.show_research_results(self.current_results)
                    if next_choice == "1":
                        break  # Start new research
                    elif next_choice == "2":
                        self.show_detailed_results(self.current_results)
                    elif next_choice == "3":
                        # Continue research on a generated topic
                        self.current_results = self.continue_research(self.current_results)
                    elif next_choice == "4":
                        self.show_settings()
                    elif next_choice == "5":
                        return
            
            elif choice == "2":
                self.show_settings()
            
            elif choice == "3":
                self.console.print("\nThank you for using Research Assistant!")
                break

    def show_detailed_results(self, results: ResearchAnalysisResult):
        """Display detailed research results"""
        self.console.clear()
        
        for analysis in results.research_analyses:
            self.console.print(Panel(
                f"Topic: {analysis.topic.topic}\n\n"
                f"Summary: {analysis.topic_summary}\n\n"
                f"New Research Direction: {analysis.new_research}",
                title=f"Research Analysis",
                border_style="blue"
            ))
            
            # Display paper analyses
            papers_table = Table(title="Analyzed Papers", box=box.ROUNDED)
            papers_table.add_column("Paper", style="cyan")
            papers_table.add_column("Analysis", style="green")
            
            for i, (paper, analysis) in enumerate(zip(analysis.topic.research_papers, analysis.paper_analyses)):
                papers_table.add_row(paper.title, Text(analysis, overflow="fold"))
            
            self.console.print(papers_table)
            self.console.print("\nPress Enter to continue...")
            input()

if __name__ == "__main__":
    cli = ResearchCLI()
    cli.run()