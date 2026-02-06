"""Interactive chat command."""

import typer
from rich.console import Console
from rich.panel import Panel

console = Console()


def chat(
    language: str = typer.Option(
        None,
        "--language", "-l",
        help="Output language (english or chinese). Overrides config setting."
    ),
):
    """Start an interactive chat session with Charlie Munger."""
    from munger.advisor.advisor import advisor
    from munger.db.database import get_session
    from munger.db.repository import UserRepository
    from munger.core.config import settings
    
    # Override language if specified
    if language:
        if language.lower() in ["english", "chinese"]:
            object.__setattr__(settings, "language", language.lower())
        else:
            console.print(f"[yellow]Warning: Invalid language '{language}'. Using {settings.language}.[/yellow]")

    console.print(Panel(
        "[bold]Interactive Chat with Charlie Munger[/bold]\n\n"
        "Type your questions and get advice in Munger's style.\n"
        "Commands:\n"
        "  /quit or /exit - End the conversation\n"
        "  /new - Start a new conversation\n"
        "  /help - Show this help message",
        title="Munger Chat",
    ))

    # Check for user profile
    with get_session() as session:
        user_repo = UserRepository(session)
        profile = user_repo.get_default()

        if not profile:
            console.print("[yellow]No profile found. Run 'munger init' first for personalized advice.[/yellow]")
            console.print("[dim]Continuing without personalization...[/dim]\n")

    conversation_id = None

    while True:
        try:
            # Get user input
            user_input = console.input("\n[bold cyan]You:[/bold cyan] ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ["/quit", "/exit", "/q"]:
                console.print("\n[dim]Goodbye. Remember: The best time to plant a tree was 20 years ago. The second best time is now.[/dim]")
                break

            if user_input.lower() == "/new":
                conversation_id = None
                console.print("[dim]Starting new conversation...[/dim]")
                continue

            if user_input.lower() == "/help":
                console.print(Panel(
                    "Commands:\n"
                    "  /quit, /exit, /q - End the conversation\n"
                    "  /new - Start a new conversation\n"
                    "  /help - Show this help message\n\n"
                    "Just type your question to get advice from Munger.",
                    title="Help",
                ))
                continue

            # Get response
            console.print("\n[bold green]Munger:[/bold green] ", end="")

            try:
                response_text = ""
                response, conversation_id = advisor.chat(
                    message=user_input,
                    conversation_id=conversation_id,
                    stream=True,
                )

                # Stream the response
                for chunk in response:
                    console.print(chunk, end="")
                    response_text += chunk

                console.print()

            except ValueError as e:
                console.print(f"\n[red]Error: {e}[/red]")
                console.print("Make sure your API key is set (MUNGER_OPENAI_API_KEY, MUNGER_ANTHROPIC_API_KEY, MUNGER_KIMI_API_KEY, or MUNGER_SILICONFLOW_API_KEY)")

        except KeyboardInterrupt:
            console.print("\n\n[dim]Interrupted. Type /quit to exit.[/dim]")
            continue

        except EOFError:
            break

    console.print()
