"""
Main entry point for Dataset Searcher CLI.
"""
import asyncio
import typer
import sys
import pandas as pd
from fpdf import FPDF
from datetime import datetime
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich import print as rprint

from models import Dataset
from searchers import kaggle_search, huggingface_search, openml_search
from config import ENABLED_SOURCES

app = typer.Typer(help="Professional Dataset Searcher CLI")
console = Console()

async def perform_search(query: str, limit: int) -> List[Dataset]:
    tasks = []
    
    if "kaggle" in ENABLED_SOURCES:
        tasks.append(kaggle_search.search(query, limit))
    if "huggingface" in ENABLED_SOURCES:
        tasks.append(huggingface_search.search(query, limit))
    if "openml" in ENABLED_SOURCES:
        tasks.append(openml_search.search(query, limit))
        
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    flat_results = []
    for res in results:
        if isinstance(res, list):
            flat_results.extend(res)
        elif isinstance(res, Exception):
            # Log error silently or display in debug mode
            pass
            
    return flat_results

def display_results(results: List[Dataset], query: str):
    if not results:
        console.print(f"[bold red]No results found for '{query}'.[/bold red]")
        return

    table = Table(title=f"Search Results for '{query}'", show_header=True, header_style="bold magenta")
    table.add_column("Source", style="cyan")
    table.add_column("Title", style="white", no_wrap=False)
    table.add_column("Size/Format", style="green")
    table.add_column("Stats", style="yellow")
    table.add_column("URL", style="blue", overflow="fold")

    for ds in results:
        stats = []
        if ds.downloads is not None: stats.append(f"D: {ds.downloads}")
        if ds.votes is not None: stats.append(f"V: {ds.votes}")
        
        table.add_row(
            ds.source.upper(),
            f"[bold]{ds.title}[/bold]\n[dim]{ds.short_desc(80)}[/dim]",
            f"{ds.size}\n({ds.format_formats()})",
            " | ".join(stats) if stats else "-",
            ds.url
        )

    console.print(table)

def export_to_excel(results: List[Dataset], query: str):
    if not results:
        return None
    
    data = []
    for ds in results:
        data.append({
            "Source": ds.source.upper(),
            "Title": ds.title,
            "Description": ds.description,
            "Size": ds.size,
            "Formats": ds.format_formats(),
            "Downloads": ds.downloads,
            "Votes": ds.votes,
            "Author": ds.author,
            "Last Updated": ds.last_updated,
            "URL": ds.url
        })
    
    df = pd.DataFrame(data)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"datasets_{query.replace(' ', '_')}_{timestamp}.xlsx"
    
    # Ensure export directory exists
    from config import EXPORT_DIR
    filepath = EXPORT_DIR / filename
    
    df.to_excel(filepath, index=False)
    return filepath

def export_to_pdf(results: List[Dataset], query: str):
    if not results:
        return None
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, f"Dataset Search Results: {query}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("helvetica", "I", 10)
    pdf.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    
    for i, ds in enumerate(results, 1):
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, f"{i}. {ds.title} ({ds.source.upper()})", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("helvetica", "", 10)
        # Description might be long, use multi_cell
        pdf.multi_cell(0, 5, f"Description: {ds.description}")
        
        pdf.cell(0, 5, f"Size: {ds.size} | Formats: {ds.format_formats()}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 5, f"Stats: Downloads: {ds.downloads or 0} | Votes: {ds.votes or 0}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 255)
        pdf.cell(0, 5, f"URL: {ds.url}", new_x="LMARGIN", new_y="NEXT", link=ds.url)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)
        
        if pdf.get_y() > 250: # Check for page break
            pdf.add_page()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"datasets_{query.replace(' ', '_')}_{timestamp}.pdf"
    
    from config import EXPORT_DIR
    filepath = EXPORT_DIR / filename
    pdf.output(str(filepath))
    return filepath

@app.command()
def search(
    query: str = typer.Argument(..., help="The search query"),
    limit: int = typer.Option(10, "--limit", "-l", help="Max results per source"),
    excel: bool = typer.Option(False, "--excel", "-e", help="Export results to Excel file"),
    pdf: bool = typer.Option(False, "--pdf", "-p", help="Export results to PDF file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """
    Search for datasets across Kaggle, HuggingFace, and OpenML.
    """
    rprint(Panel.fit(
        "[bold blue]Dataset Searcher[/bold blue]\n[dim]Searching datasets across the internet...[/dim]",
        border_style="bright_blue"
    ))

    async def run():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description=f"Fetching datasets for '{query}'...", total=None)
            results = await perform_search(query, limit)
            return results

    results = asyncio.run(run())
    display_results(results, query)
    
    if excel and results:
        filepath = export_to_excel(results, query)
        if filepath:
            console.print(f"\n[bold green]✅ Results exported to Excel:[/bold green] [blue]{filepath}[/blue]")

    if pdf and results:
        filepath = export_to_pdf(results, query)
        if filepath:
            console.print(f"[bold green]✅ Results exported to PDF:[/bold green] [blue]{filepath}[/blue]")

if __name__ == "__main__":
    if sys.platform == "win32":
        # Force UTF-8 on Windows to prevent UnicodeEncodeError
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    app()
