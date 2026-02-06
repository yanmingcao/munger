"""Ask command for getting advice."""

import typer
from rich.console import Console
from rich.markdown import Markdown

console = Console()


def ask(
    question: str = typer.Argument(..., help="Your question for Charlie Munger"),
    context: str = typer.Option(
        None,
        "--context", "-c",
        help="Additional context about your situation"
    ),
    no_stream: bool = typer.Option(
        False,
        "--no-stream",
        help="Disable streaming output"
    ),
):
    """Ask Charlie Munger for advice."""
    from munger.advisor.advisor import advisor

    console.print()

    # Add context to question if provided
    full_question = question
    if context:
        full_question = f"{question}\n\nContext: {context}"

    try:
        if no_stream:
            response = advisor.ask(full_question, stream=False)
            console.print(Markdown(response))
        else:
            # Stream the response
            for chunk in advisor.ask(full_question, stream=True):
                console.print(chunk, end="")
            console.print()

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("\nMake sure you have:")
        console.print("  1. Run 'munger init' to set up your profile")
        console.print("  2. Set your API key (MUNGER_OPENAI_API_KEY, MUNGER_ANTHROPIC_API_KEY, MUNGER_KIMI_API_KEY, or MUNGER_SILICONFLOW_API_KEY)")
        raise typer.Exit(1)

    console.print()
