"""Charter management CLI commands."""

import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(help="Manage your personal charter")
console = Console()


@app.command(name="show")
def show():
    """Show your personal charter."""
    from munger.db.database import get_session
    from munger.db.repository import UserRepository, CharterRepository

    with get_session() as session:
        user_repo = UserRepository(session)
        charter_repo = CharterRepository(session)

        profile = user_repo.get_default()
        if not profile:
            console.print("[yellow]No profile found. Run 'munger init' first.[/yellow]")
            raise typer.Exit(1)

        charter = charter_repo.get_by_user(profile.id)
        if not charter:
            console.print("[yellow]No charter defined yet. Run 'munger charter edit' to create one.[/yellow]")
            raise typer.Exit(1)

        console.print(f"\n[bold]Personal Charter for {profile.name}[/bold]\n")

        if charter.values:
            console.print("[bold cyan]Core Values[/bold cyan] (in priority order)")
            for i, value in enumerate(charter.values, 1):
                console.print(f"  {i}. {value}")
            console.print()

        if charter.non_negotiables:
            console.print("[bold cyan]Non-Negotiables[/bold cyan]")
            for item in charter.non_negotiables:
                console.print(f"  • {item}")
            console.print()

        if charter.long_term_goals:
            console.print("[bold cyan]Long-Term Goals[/bold cyan]")
            for item in charter.long_term_goals:
                console.print(f"  • {item}")
            console.print()

        if charter.anti_goals:
            console.print("[bold cyan]Things to Avoid[/bold cyan]")
            for item in charter.anti_goals:
                console.print(f"  • {item}")
            console.print()

        if charter.remember_topics:
            console.print("[bold cyan]Topics to Remember[/bold cyan]")
            for item in charter.remember_topics:
                console.print(f"  • {item}")
            console.print()


@app.command(name="edit")
def edit():
    """Edit your personal charter interactively."""
    from munger.db.database import get_session
    from munger.db.repository import UserRepository, CharterRepository
    from munger.core.models import Charter

    with get_session() as session:
        user_repo = UserRepository(session)
        charter_repo = CharterRepository(session)

        profile = user_repo.get_default()
        if not profile:
            console.print("[yellow]No profile found. Run 'munger init' first.[/yellow]")
            raise typer.Exit(1)

        charter = charter_repo.get_by_user(profile.id)
        is_new = charter is None

        if is_new:
            charter = Charter(user_id=profile.id)

        console.print(f"\n[bold]Personal Charter for {profile.name}[/bold]")
        console.print("[dim]Your charter helps me understand what matters most to you.[/dim]")
        console.print("[dim]Enter items separated by commas. Press Enter to keep current values.[/dim]\n")

        # Values
        console.print(Panel(
            "Your core values guide all decisions. List them in priority order.\n"
            "Examples: Family first, Integrity always, Continuous learning",
            title="Core Values",
        ))
        current_values = ", ".join(charter.values) if charter.values else ""
        new_values = typer.prompt("Values", default=current_values)
        charter.values = [v.strip() for v in new_values.split(",") if v.strip()]

        # Non-negotiables
        console.print(Panel(
            "Things you will never compromise on, no matter what.\n"
            "Examples: Never lie, Never sacrifice health for money",
            title="Non-Negotiables",
        ))
        current_non_neg = ", ".join(charter.non_negotiables) if charter.non_negotiables else ""
        new_non_neg = typer.prompt("Non-negotiables", default=current_non_neg)
        charter.non_negotiables = [v.strip() for v in new_non_neg.split(",") if v.strip()]

        # Long-term goals
        console.print(Panel(
            "Major life goals and aspirations.\n"
            "Examples: Financial independence by 60, Strong family relationships",
            title="Long-Term Goals",
        ))
        current_goals = ", ".join(charter.long_term_goals) if charter.long_term_goals else ""
        new_goals = typer.prompt("Long-term goals", default=current_goals)
        charter.long_term_goals = [v.strip() for v in new_goals.split(",") if v.strip()]

        # Anti-goals
        console.print(Panel(
            "Outcomes you actively want to avoid.\n"
            "Examples: Burnout, Regret from not spending time with family",
            title="Anti-Goals (What to Avoid)",
        ))
        current_anti = ", ".join(charter.anti_goals) if charter.anti_goals else ""
        new_anti = typer.prompt("Anti-goals", default=current_anti)
        charter.anti_goals = [v.strip() for v in new_anti.split(",") if v.strip()]

        # Remember topics
        console.print(Panel(
            "Topics I should always remember and reference in advice.\n"
            "Examples: Career transition, Family health situation",
            title="Topics to Remember",
        ))
        current_remember = ", ".join(charter.remember_topics) if charter.remember_topics else ""
        new_remember = typer.prompt("Remember topics", default=current_remember)
        charter.remember_topics = [v.strip() for v in new_remember.split(",") if v.strip()]

        # Sensitive topics
        console.print(Panel(
            "Topics requiring extra care when discussing.\n"
            "Examples: Past failures, Family conflicts",
            title="Sensitive Topics",
        ))
        current_sensitive = ", ".join(charter.sensitive_topics) if charter.sensitive_topics else ""
        new_sensitive = typer.prompt("Sensitive topics", default=current_sensitive)
        charter.sensitive_topics = [v.strip() for v in new_sensitive.split(",") if v.strip()]

        # Save
        if is_new:
            charter_repo.create(charter)
        else:
            charter_repo.update(charter)

        console.print("\n[green]✓ Charter saved![/green]")


@app.command(name="values")
def edit_values(
    values: list[str] = typer.Argument(None, help="Values to set (in priority order)"),
):
    """Quickly update your core values."""
    from munger.db.database import get_session
    from munger.db.repository import UserRepository, CharterRepository
    from munger.core.models import Charter

    if not values:
        console.print("Usage: munger charter values 'Family first' 'Integrity' 'Learning'")
        raise typer.Exit(1)

    with get_session() as session:
        user_repo = UserRepository(session)
        charter_repo = CharterRepository(session)

        profile = user_repo.get_default()
        if not profile:
            console.print("[yellow]No profile found. Run 'munger init' first.[/yellow]")
            raise typer.Exit(1)

        charter = charter_repo.get_by_user(profile.id)
        if not charter:
            charter = Charter(user_id=profile.id, values=values)
            charter_repo.create(charter)
        else:
            charter.values = values
            charter_repo.update(charter)

        console.print(f"[green]✓ Values updated: {', '.join(values)}[/green]")
