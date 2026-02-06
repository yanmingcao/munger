"""Content ingestion CLI commands."""

import warnings
# Suppress the transformers tokenization warning
warnings.filterwarnings("ignore", message=".*clean_up_tokenization_spaces.*")
warnings.filterwarnings("ignore", category=FutureWarning)

import sys
import typer

app = typer.Typer(help="Ingest Munger wisdom materials")


def output(msg: str):
    """Force output to stdout."""
    print(msg, flush=True)
    sys.stdout.flush()


@app.command(name="add")
def add_content(
    source: str = typer.Argument(..., help="URL or file path to ingest"),
    title: str = typer.Option(None, "--title", "-t", help="Title for the content"),
    category: str = typer.Option(
        "quote",
        "--category", "-c",
        help="Category: quote, mental_model, principle, story, speech_excerpt, book_excerpt"
    ),
):
    """Add wisdom content from a URL or file."""
    from pathlib import Path
    from munger.ingest.processor import ContentProcessor

    output("Processing content...")

    try:
        processor = ContentProcessor()

        # Check if it's a file or URL
        if Path(source).exists():
            count = processor.process_file(Path(source), title=title, category=category)
        else:
            count = processor.process_url(source, title=title, category=category)

        output(f"Added {count} wisdom entries from {source}")

    except Exception as e:
        output(f"Error processing content: {e}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)


@app.command(name="seed")
def seed_wisdom():
    """Seed the database with built-in Munger wisdom."""
    output("Seeding Munger wisdom...")

    try:
        output("Importing seed module...")
        from munger.ingest.seed import seed_munger_wisdom
        
        output("Calling seed_munger_wisdom()...")
        count = seed_munger_wisdom()
        output(f"Returned count: {count}")

        if count == 0:
            output("Wisdom already seeded (found existing entries).")
        else:
            output(f"Seeded {count} wisdom entries")

    except Exception as e:
        output(f"Error seeding wisdom: {e}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)


@app.command(name="status")
def show_status():
    """Show the status of the wisdom knowledge base."""
    output("Checking status...")
    
    try:
        output("Importing vector store...")
        from munger.db.vector_store import WisdomVectorStore
        
        output("Creating store instance...")
        store = WisdomVectorStore()
        
        output("Getting count...")
        count = store.get_count()
        output(f"Count: {count}")
        
        output("Getting categories...")
        categories = store.get_all_categories()

        output(f"\nWisdom Knowledge Base")
        output(f"  Total entries: {count}")

        if categories:
            output(f"  Categories: {', '.join(categories)}")

        if count == 0:
            output("\nNo wisdom loaded. Run 'munger ingest seed' to add built-in wisdom.")

    except Exception as e:
        output(f"Error accessing knowledge base: {e}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)


@app.command(name="search")
def search_wisdom(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(5, "--limit", "-n", help="Number of results"),
):
    """Search the wisdom knowledge base."""
    from munger.db.vector_store import WisdomVectorStore

    try:
        store = WisdomVectorStore()
        results = store.search(query, n_results=limit)

        if not results:
            output("No matching wisdom found.")
            return

        output(f"\nSearch results for '{query}'\n")

        for i, result in enumerate(results, 1):
            title = result.get("metadata", {}).get("title", "Untitled")
            source = result.get("metadata", {}).get("source", "Unknown")
            content = result.get("content", "")[:300]
            distance = result.get("distance", 0)

            output(f"{i}. {title} (relevance: {1-distance:.2f})")
            output(f"   Source: {source}")
            output(f"   {content}...")
            output("")

    except Exception as e:
        output(f"Error searching: {e}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)


@app.command(name="clear")
def clear_wisdom():
    """Clear all wisdom from the knowledge base."""
    if not typer.confirm("This will delete all wisdom entries. Continue?"):
        raise typer.Abort()

    from munger.db.vector_store import WisdomVectorStore

    try:
        store = WisdomVectorStore()
        store.clear()
        output("Wisdom knowledge base cleared.")

    except Exception as e:
        output(f"Error clearing: {e}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)
