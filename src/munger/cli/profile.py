"""Profile management CLI commands."""

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Manage your profile")
console = Console()


@app.command(name="show")
def show():
    """Show your current profile."""
    from munger.db.database import get_session
    from munger.db.repository import UserRepository

    with get_session() as session:
        user_repo = UserRepository(session)
        profile = user_repo.get_default()

        if not profile:
            console.print("[yellow]No profile found. Run 'munger init' to create one.[/yellow]")
            raise typer.Exit(1)

        console.print(f"\n[bold]Profile: {profile.name}[/bold]\n")

        table = Table(show_header=False, box=None)
        table.add_column("Field", style="cyan")
        table.add_column("Value")

        # Background
        bg = profile.background
        table.add_row("Age", str(bg.age) if bg.age else "Not set")
        table.add_row("Career Stage", bg.career_stage.value if bg.career_stage else "Not set")
        table.add_row("Industry", bg.industry or "Not set")
        table.add_row("Occupation", bg.occupation or "Not set")
        table.add_row("Location", bg.current_location or "Not set")

        # Constraints
        cons = profile.constraints
        table.add_row("", "")  # Spacer
        table.add_row("Time Horizon", cons.time_horizon.value)
        table.add_row("Risk Tolerance", cons.risk_tolerance.value)
        table.add_row("Has Dependents", "Yes" if cons.has_dependents else "No" if cons.has_dependents is False else "Not set")

        # Preferences
        prefs = profile.preferences
        table.add_row("", "")  # Spacer
        table.add_row("Advice Tone", prefs.tone.value)
        table.add_row("Preferred Examples", ", ".join(prefs.preferred_examples))

        console.print(table)

        if profile.bio:
            console.print(f"\n[bold]Bio:[/bold]\n{profile.bio}")

        console.print()


@app.command(name="edit")
def edit():
    """Edit your profile interactively."""
    from munger.db.database import get_session
    from munger.db.repository import UserRepository
    from munger.core.models import (
        CareerStage,
        TimeHorizon,
        RiskTolerance,
        AdviceTone,
    )

    with get_session() as session:
        user_repo = UserRepository(session)
        profile = user_repo.get_default()

        if not profile:
            console.print("[yellow]No profile found. Run 'munger init' first.[/yellow]")
            raise typer.Exit(1)

        console.print(f"\n[bold]Editing profile for {profile.name}[/bold]")
        console.print("[dim]Press Enter to keep current value[/dim]\n")

        # Name
        new_name = typer.prompt("Name", default=profile.name)
        profile.name = new_name

        # Age
        current_age = str(profile.background.age) if profile.background.age else ""
        new_age = typer.prompt("Age", default=current_age)
        profile.background.age = int(new_age) if new_age else None

        # Career stage
        console.print("\nCareer stages: early, mid, senior, executive, retired")
        current_career = profile.background.career_stage.value if profile.background.career_stage else "mid"
        new_career = typer.prompt("Career stage", default=current_career)
        try:
            profile.background.career_stage = CareerStage(new_career)
        except ValueError:
            console.print(f"[yellow]Invalid career stage, keeping {current_career}[/yellow]")

        # Industry
        new_industry = typer.prompt("Industry", default=profile.background.industry or "")
        profile.background.industry = new_industry if new_industry else None

        # Occupation
        new_occupation = typer.prompt("Occupation", default=profile.background.occupation or "")
        profile.background.occupation = new_occupation if new_occupation else None

        # Time horizon
        console.print("\nTime horizons: short (<1y), medium (1-5y), long (5-10y), very_long (10+y)")
        current_horizon = profile.constraints.time_horizon.value
        new_horizon = typer.prompt("Time horizon", default=current_horizon)
        try:
            profile.constraints.time_horizon = TimeHorizon(new_horizon)
        except ValueError:
            console.print(f"[yellow]Invalid time horizon, keeping {current_horizon}[/yellow]")

        # Risk tolerance
        console.print("\nRisk tolerance: low, medium, high")
        current_risk = profile.constraints.risk_tolerance.value
        new_risk = typer.prompt("Risk tolerance", default=current_risk)
        try:
            profile.constraints.risk_tolerance = RiskTolerance(new_risk)
        except ValueError:
            console.print(f"[yellow]Invalid risk tolerance, keeping {current_risk}[/yellow]")

        # Has dependents
        current_deps = "yes" if profile.constraints.has_dependents else "no" if profile.constraints.has_dependents is False else ""
        new_deps = typer.prompt("Has dependents? (yes/no)", default=current_deps)
        if new_deps.lower() in ["yes", "y"]:
            profile.constraints.has_dependents = True
        elif new_deps.lower() in ["no", "n"]:
            profile.constraints.has_dependents = False

        # Advice tone
        console.print("\nAdvice tone: blunt, balanced, gentle")
        current_tone = profile.preferences.tone.value
        new_tone = typer.prompt("Preferred advice tone", default=current_tone)
        try:
            profile.preferences.tone = AdviceTone(new_tone)
        except ValueError:
            console.print(f"[yellow]Invalid tone, keeping {current_tone}[/yellow]")

        # Bio
        console.print("\nBio (your background, family, interests - helps personalize advice)")
        new_bio = typer.prompt("Bio", default=profile.bio or "")
        profile.bio = new_bio if new_bio else None

        # Save
        user_repo.update(profile)
        console.print("\n[green]✓ Profile updated![/green]")


@app.command(name="delete")
def delete():
    """Delete your profile and all associated data."""
    from munger.db.database import get_session
    from munger.db.repository import UserRepository

    if not typer.confirm("This will delete your profile and all associated data. Continue?"):
        raise typer.Abort()

    with get_session() as session:
        user_repo = UserRepository(session)
        profile = user_repo.get_default()

        if not profile:
            console.print("[yellow]No profile found.[/yellow]")
            raise typer.Exit(1)

        user_repo.delete(profile.id)
        console.print("[green]✓ Profile deleted.[/green]")
