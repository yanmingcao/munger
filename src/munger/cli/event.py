"""Life event management CLI commands."""

from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Record and view life events")
console = Console()


@app.command(name="add")
def add(
    title: str = typer.Option(..., "--title", "-t", help="Brief title of the event"),
    description: str = typer.Option(..., "--desc", "-d", help="What happened"),
    category: str = typer.Option(
        "other",
        "--category", "-c",
        help="Category: career, family, health, financial, relationship, education, personal_growth, other"
    ),
    date: str = typer.Option(
        None,
        "--date",
        help="Date of event (YYYY-MM-DD), defaults to today"
    ),
    significance: int = typer.Option(
        5,
        "--significance", "-s",
        min=1, max=10,
        help="How significant (1-10)"
    ),
    emotions: str = typer.Option(
        None,
        "--emotions", "-e",
        help="Emotions felt (comma-separated)"
    ),
):
    """Add a new life event."""
    from munger.db.database import get_session
    from munger.db.repository import UserRepository, EventRepository
    from munger.core.models import LifeEvent, EventCategory

    with get_session() as session:
        user_repo = UserRepository(session)
        event_repo = EventRepository(session)

        profile = user_repo.get_default()
        if not profile:
            console.print("[yellow]No profile found. Run 'munger init' first.[/yellow]")
            raise typer.Exit(1)

        # Parse date
        if date:
            try:
                event_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                console.print("[red]Invalid date format. Use YYYY-MM-DD[/red]")
                raise typer.Exit(1)
        else:
            event_date = datetime.now()

        # Parse category
        try:
            event_category = EventCategory(category.lower())
        except ValueError:
            console.print(f"[yellow]Invalid category '{category}', using 'other'[/yellow]")
            event_category = EventCategory.OTHER

        # Parse emotions
        emotion_list = []
        if emotions:
            emotion_list = [e.strip() for e in emotions.split(",") if e.strip()]

        # Create event
        event = LifeEvent(
            user_id=profile.id,
            date=event_date,
            title=title,
            description=description,
            category=event_category,
            significance=significance,
            emotions=emotion_list,
        )

        event_repo.create(event)
        console.print(f"[green]✓ Event recorded: {title}[/green]")


@app.command(name="quick")
def quick_add():
    """Quickly add an event interactively."""
    from munger.db.database import get_session
    from munger.db.repository import UserRepository, EventRepository
    from munger.core.models import LifeEvent, EventCategory

    with get_session() as session:
        user_repo = UserRepository(session)
        event_repo = EventRepository(session)

        profile = user_repo.get_default()
        if not profile:
            console.print("[yellow]No profile found. Run 'munger init' first.[/yellow]")
            raise typer.Exit(1)

        console.print("\n[bold]Record a Life Event[/bold]\n")

        title = typer.prompt("What happened? (brief title)")
        description = typer.prompt("Tell me more about it")

        # Category selection
        categories = ["career", "family", "health", "financial", "relationship", "education", "personal_growth", "other"]
        console.print("\nCategory:")
        for i, cat in enumerate(categories, 1):
            console.print(f"  {i}. {cat}")
        cat_choice = typer.prompt("Select", type=int, default=8)
        category = EventCategory(categories[min(cat_choice - 1, len(categories) - 1)])

        significance = typer.prompt("How significant? (1-10)", type=int, default=5)
        significance = max(1, min(10, significance))

        emotions_str = typer.prompt("How did you feel? (e.g., happy, anxious, proud)", default="")
        emotions = [e.strip() for e in emotions_str.split(",") if e.strip()]

        # Create event
        event = LifeEvent(
            user_id=profile.id,
            date=datetime.now(),
            title=title,
            description=description,
            category=category,
            significance=significance,
            emotions=emotions,
        )

        event_repo.create(event)
        console.print(f"\n[green]✓ Event recorded![/green]")


@app.command(name="list")
def list_events(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of events to show"),
    category: str = typer.Option(None, "--category", "-c", help="Filter by category"),
):
    """List recent life events."""
    from munger.db.database import get_session
    from munger.db.repository import UserRepository, EventRepository
    from munger.core.models import EventCategory

    with get_session() as session:
        user_repo = UserRepository(session)
        event_repo = EventRepository(session)

        profile = user_repo.get_default()
        if not profile:
            console.print("[yellow]No profile found. Run 'munger init' first.[/yellow]")
            raise typer.Exit(1)

        # Parse category filter
        cat_filter = None
        if category:
            try:
                cat_filter = EventCategory(category.lower())
            except ValueError:
                console.print(f"[yellow]Invalid category '{category}'[/yellow]")

        events = event_repo.list_by_user(profile.id, category=cat_filter, limit=limit)

        if not events:
            console.print("[yellow]No events recorded yet. Use 'munger event add' or 'munger event quick'.[/yellow]")
            return

        table = Table(title="Life Events")
        table.add_column("Date", style="cyan")
        table.add_column("Category")
        table.add_column("Title")
        table.add_column("Sig", justify="center")
        table.add_column("Emotions")

        for event in events:
            date_str = event.date.strftime("%Y-%m-%d")
            emotions_str = ", ".join(event.emotions[:3]) if event.emotions else ""
            table.add_row(
                date_str,
                event.category.value,
                event.title[:40],
                str(event.significance),
                emotions_str,
            )

        console.print(table)


@app.command(name="show")
def show_event(
    event_id: str = typer.Argument(..., help="Event ID to show"),
):
    """Show details of a specific event."""
    from munger.db.database import get_session
    from munger.db.repository import EventRepository

    with get_session() as session:
        event_repo = EventRepository(session)
        event = event_repo.get(event_id)

        if not event:
            console.print(f"[red]Event not found: {event_id}[/red]")
            raise typer.Exit(1)

        console.print(f"\n[bold]{event.title}[/bold]")
        console.print(f"Date: {event.date.strftime('%Y-%m-%d')}")
        console.print(f"Category: {event.category.value}")
        console.print(f"Significance: {event.significance}/10")

        if event.emotions:
            console.print(f"Emotions: {', '.join(event.emotions)}")

        console.print(f"\n{event.description}")

        if event.lessons_learned:
            console.print(f"\n[bold]Lessons learned:[/bold]\n{event.lessons_learned}")

        if event.people_involved:
            console.print(f"\n[bold]People involved:[/bold] {', '.join(event.people_involved)}")

        console.print()
