"""Main CLI entry point for Munger advisor."""

import typer
from rich.console import Console

from munger.cli import profile as profile_cmd
from munger.cli import charter as charter_cmd
from munger.cli import event as event_cmd
from munger.cli import ask as ask_cmd
from munger.cli import chat as chat_cmd
from munger.cli import ingest as ingest_cmd

# Create the main app
app = typer.Typer(
    name="munger",
    help="Charlie Munger Personal Advisor - Your wise friend who knows you deeply.",
    no_args_is_help=False,
)

console = Console()

# Register subcommands
app.add_typer(profile_cmd.app, name="profile", help="Manage your profile")
app.add_typer(charter_cmd.app, name="charter", help="Manage your personal charter")
app.add_typer(event_cmd.app, name="event", help="Record and view life events")
app.add_typer(ingest_cmd.app, name="ingest", help="Ingest Munger wisdom materials")

# Direct commands
app.command(name="ask")(ask_cmd.ask)
app.command(name="chat")(chat_cmd.chat)


@app.command()
def init():
    """Initialize Munger advisor with your profile."""
    from munger.db.database import init_db, get_session
    from munger.db.repository import UserRepository
    from munger.core.models import UserProfile, Background, CareerStage
    from munger.core.config import settings

    console.print("\n[bold blue]Welcome to Munger - Your Personal Advisor[/bold blue]\n")
    console.print("Let's set up your profile so I can give you personalized advice.\n")

    # Initialize database
    settings.ensure_data_dir()
    init_db()

    with get_session() as session:
        user_repo = UserRepository(session)

        # Check if profile already exists
        existing = user_repo.get_default()
        if existing:
            if not typer.confirm(f"Profile for '{existing.name}' already exists. Update it?"):
                console.print("[yellow]Setup cancelled.[/yellow]")
                raise typer.Exit()

        # Collect basic info
        name = typer.prompt("What's your name?")

        age = typer.prompt("How old are you?", type=int, default=0)
        if age == 0:
            age = None

        # Career stage
        career_options = ["early (0-5 years)", "mid (5-15 years)", "senior (15-25 years)", "executive (25+ years)", "retired"]
        console.print("\nCareer stage:")
        for i, opt in enumerate(career_options, 1):
            console.print(f"  {i}. {opt}")
        career_choice = typer.prompt("Select", type=int, default=2)
        career_map = {1: CareerStage.EARLY, 2: CareerStage.MID, 3: CareerStage.SENIOR, 4: CareerStage.EXECUTIVE, 5: CareerStage.RETIRED}
        career_stage = career_map.get(career_choice, CareerStage.MID)

        industry = typer.prompt("What industry do you work in?", default="")
        occupation = typer.prompt("What's your occupation?", default="")

        bio = typer.prompt(
            "Tell me about yourself (background, family, interests - optional)",
            default="",
        )

        # Create or update profile
        background = Background(
            age=age,
            career_stage=career_stage,
            industry=industry if industry else None,
            occupation=occupation if occupation else None,
        )

        if existing:
            existing.name = name
            existing.background = background
            existing.bio = bio if bio else None
            user_repo.update(existing)
            profile = existing
        else:
            profile = UserProfile(
                name=name,
                background=background,
                bio=bio if bio else None,
            )
            user_repo.create(profile)

    console.print(f"\n[green]✓ Profile saved for {name}![/green]")
    console.print("\nNext steps:")
    console.print("  • Run [bold]munger charter edit[/bold] to define your values")
    console.print("  • Run [bold]munger ask 'your question'[/bold] to get advice")
    console.print("  • Run [bold]munger chat[/bold] for interactive conversation")


@app.command()
def review(
    language: str = typer.Option(
        None,
        "--language", "-l",
        help="Output language (english or chinese). Overrides config setting."
    ),
):
    """Have a reflection session with Munger."""
    from rich.markdown import Markdown
    from munger.core.config import settings

    from munger.advisor.advisor import advisor

    # Override language if specified
    if language:
        if language.lower() in ["english", "chinese"]:
            object.__setattr__(settings, "language", language.lower())
        else:
            console.print(f"[yellow]Warning: Invalid language '{language}'. Using {settings.language}.[/yellow]")

    if settings.language == "chinese":
        console.print("\n[bold blue]与查理·芒格的反思对话[/bold blue]\n")
        console.print("[dim]让我看看你最近生活中发生的事情...[/dim]\n")
    else:
        console.print("\n[bold blue]Reflection Session with Charlie Munger[/bold blue]\n")
        console.print("[dim]Let me look at what's been happening in your life...[/dim]\n")

    try:
        # Stream the response
        response_text = ""
        for chunk in advisor.reflect(stream=True):
            console.print(chunk, end="")
            response_text += chunk

        console.print("\n")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("Run [bold]munger init[/bold] to set up your profile first.")
        raise typer.Exit(1)


@app.command()
def status():
    """Check the status of your Munger advisor setup."""
    from munger.core.config import settings
    from munger.db.database import get_session
    from munger.db.repository import UserRepository, CharterRepository, EventRepository
    from munger.db.vector_store import WisdomVectorStore

    console.print("\n[bold]Munger Advisor Status[/bold]\n")

    # Check data directory
    console.print(f"Data directory: {settings.data_dir}")
    console.print(f"  Exists: {'[green]Yes[/green]' if settings.data_dir.exists() else '[red]No[/red]'}")

    # Check database
    console.print(f"\nDatabase: {settings.db_path}")
    console.print(f"  Exists: {'[green]Yes[/green]' if settings.db_path.exists() else '[red]No[/red]'}")

    if settings.db_path.exists():
        with get_session() as session:
            user_repo = UserRepository(session)
            charter_repo = CharterRepository(session)
            event_repo = EventRepository(session)

            profile = user_repo.get_default()
            if profile:
                console.print(f"\n[bold]Profile:[/bold] {profile.name}")
                console.print(f"  Career stage: {profile.background.career_stage.value if profile.background.career_stage else 'Not set'}")
                console.print(f"  Industry: {profile.background.industry or 'Not set'}")

                charter = charter_repo.get_by_user(profile.id)
                console.print(f"\n[bold]Charter:[/bold] {'[green]Defined[/green]' if charter and charter.values else '[yellow]Not defined[/yellow]'}")
                if charter and charter.values:
                    console.print(f"  Values: {', '.join(charter.values[:3])}")

                events = event_repo.list_by_user(profile.id, limit=100)
                console.print(f"\n[bold]Life events:[/bold] {len(events)} recorded")
            else:
                console.print("\n[yellow]No profile found. Run 'munger init' to get started.[/yellow]")

    # Check vector store
    console.print(f"\nVector store: {settings.vector_store_path}")
    if settings.vector_store_path.exists():
        try:
            store = WisdomVectorStore()
            count = store.get_count()
            console.print(f"  Wisdom entries: {count}")
        except Exception as e:
            console.print(f"  [red]Error loading: {e}[/red]")
    else:
        console.print("  [yellow]Not initialized[/yellow]")

    # Check LLM configuration
    console.print(f"\n[bold]LLM Provider:[/bold] {settings.llm_provider}")
    if settings.llm_provider == "openai":
        console.print(f"  API Key: {'[green]Set[/green]' if settings.openai_api_key else '[red]Not set[/red]'}")
        console.print(f"  Model: {settings.openai_model}")
    elif settings.llm_provider == "anthropic":
        console.print(f"  API Key: {'[green]Set[/green]' if settings.anthropic_api_key else '[red]Not set[/red]'}")
        console.print(f"  Model: {settings.anthropic_model}")
    elif settings.llm_provider == "kimi":
        console.print(f"  API Key: {'[green]Set[/green]' if settings.kimi_api_key else '[red]Not set[/red]'}")
        console.print(f"  Model: {settings.kimi_model}")
    else:  # siliconflow
        console.print(f"  API Key: {'[green]Set[/green]' if settings.siliconflow_api_key else '[red]Not set[/red]'}")
        console.print(f"  Model: {settings.siliconflow_model}")

    console.print()


@app.command(name="wisdom")
def wisdom(
    language: str = typer.Option(
        None,
        "--language", "-l",
        help="Output language (english or chinese). Overrides config setting."
    ),
):
    """Get a random daily wisdom from Charlie Munger."""
    from rich.panel import Panel
    from munger.db.vector_store import WisdomVectorStore
    from munger.core.config import settings
    from munger.advisor.llm import generate_response
    
    # Override language if specified
    if language:
        if language.lower() in ["english", "chinese"]:
            object.__setattr__(settings, "language", language.lower())
        else:
            console.print(f"[yellow]Warning: Invalid language '{language}'. Using {settings.language}.[/yellow]")
    
    try:
        store = WisdomVectorStore()
        wisdom_item = store.get_random_wisdom()
        
        if not wisdom_item:
            if settings.language == "chinese":
                console.print("[yellow]没有找到智慧语录。请先运行 'munger ingest seed'。[/yellow]")
            else:
                console.print("[yellow]No wisdom found. Run 'munger ingest seed' first.[/yellow]")
            raise typer.Exit(1)
        
        content = wisdom_item["content"]
        metadata = wisdom_item["metadata"]
        title = metadata.get("title", "Munger Wisdom")
        source = metadata.get("source", "Unknown")
        category = metadata.get("category", "wisdom")
        
        # Translate to Chinese if needed
        if settings.language == "chinese":
            # Translate the quote content
            translation_prompt = [
                {
                    "role": "system",
                    "content": "You are a professional translator. Translate the following Charlie Munger quote to natural, idiomatic Simplified Chinese (简体中文). Preserve the wisdom and tone. Only return the translation, no explanations."
                },
                {
                    "role": "user",
                    "content": content
                }
            ]
            try:
                translated = generate_response(translation_prompt, stream=False)
                if translated and isinstance(translated, str):
                    content = translated.strip()
            except Exception:
                # If translation fails, keep original English
                pass
            
            # Translate the title
            title_translation_prompt = [
                {
                    "role": "system",
                    "content": "Translate the following title to Simplified Chinese (简体中文). Keep it concise and elegant. Only return the translation."
                },
                {
                    "role": "user",
                    "content": title
                }
            ]
            try:
                title_translated = generate_response(title_translation_prompt, stream=False)
                if title_translated and isinstance(title_translated, str):
                    title = title_translated.strip()
            except Exception:
                # If translation fails, keep original English title
                pass
            
            # Translate the source
            source_translation_prompt = [
                {
                    "role": "system",
                    "content": "Translate the following source attribution to Simplified Chinese (简体中文). Be natural and concise. Only return the translation."
                },
                {
                    "role": "user",
                    "content": source
                }
            ]
            try:
                source_translated = generate_response(source_translation_prompt, stream=False)
                if source_translated and isinstance(source_translated, str):
                    source = source_translated.strip()
            except Exception:
                # If translation fails, keep original English source
                pass
            
            panel_title = f"[yellow]每日智慧: {title}[/yellow]"
            panel_subtitle = f"[bright_cyan]{source} (名言)[/bright_cyan]"
        else:
            panel_title = f"[yellow]Daily Wisdom: {title}[/yellow]"
            panel_subtitle = f"[bright_cyan]{source} ({category})[/bright_cyan]"
        
        # Display the wisdom
        console.print()
        console.print(Panel(
            f"[bold]{content}[/bold]",
            title=panel_title,
            subtitle=panel_subtitle,
            border_style="blue",
            padding=(1, 2),
        ))
        console.print()
        
    except Exception as e:
        if settings.language == "chinese":
            console.print(f"[red]加载智慧语录时出错: {e}[/red]")
        else:
            console.print(f"[red]Error loading wisdom: {e}[/red]")
        raise typer.Exit(1)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    language: str = typer.Option(
        None,
        "--language", "-l",
        help="Output language (english or chinese). Overrides config setting."
    ),
):
    """Charlie Munger Personal Advisor - Your wise friend who knows you deeply.
    
    When run without arguments, displays a random daily wisdom.
    """
    from munger.core.config import settings
    
    # Override language if specified
    if language:
        if language.lower() in ["english", "chinese"]:
            object.__setattr__(settings, "language", language.lower())
        else:
            console.print(f"[yellow]Warning: Invalid language '{language}'. Using {settings.language}.[/yellow]")
    
    # If no command is given, show daily wisdom
    if ctx.invoked_subcommand is None:
        # Invoke the wisdom command (without language arg since it's already set)
        ctx.invoke(wisdom, language=None)


if __name__ == "__main__":
    app()
