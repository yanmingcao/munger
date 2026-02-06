"""Content ingestion CLI commands."""

import warnings
# Suppress the transformers tokenization warning
warnings.filterwarnings("ignore", message=".*clean_up_tokenization_spaces.*")
warnings.filterwarnings("ignore", category=FutureWarning)

import sys
import typer
from pathlib import Path

app = typer.Typer(help="Ingest Munger wisdom materials")


# Presets: built-in wisdom sources
PRESETS = {
    "web": [
        {
            "url": "https://fs.blog/great-talks/psychology-human-misjudgment/",
            "title": "The Psychology of Human Misjudgment",
            "category": "speech_excerpt",
        },
        {
            "url": "https://fs.blog/great-talks/a-lesson-on-worldly-wisdom/",
            "title": "Elementary Worldly Wisdom",
            "category": "speech_excerpt",
        },
        {
            "url": "https://singjupost.com/full-transcript-charlie-mungers-speech-at-usc-commencement-2007/",
            "title": "USC Commencement Speech 2007",
            "category": "speech_excerpt",
        },
        {
            "url": "https://www.octafinance.com/charlie-munger-quotes/",
            "title": "Charlie Munger Quotes Collection",
            "category": "quote",
        },
        {
            "url": "https://www.joshuakennon.com/the-complete-list-of-charlie-munger-quotes/",
            "title": "Complete List of Charlie Munger Quotes",
            "category": "quote",
        },
    ],
    "pdfs": [
        {
            "filename": "poor-charlies-almanack.pdf",
            "title": "Poor Charlie's Almanack",
            "category": "book_excerpt",
            "description": "Charlie Munger's collected wisdom and investment philosophy",
        },
        {
            "filename": "berkshire-letters.pdf",
            "title": "Berkshire Hathaway Letters",
            "category": "book_excerpt",
            "description": "Annual letters from Berkshire Hathaway shareholders",
        },
        {
            "filename": "psychology-of-human-misjudgment-2005.pdf",
            "title": "The Psychology of Human Misjudgment",
            "category": "speech_excerpt",
            "description": "Charlie Munger's famous speech on cognitive biases",
        },
        {
            "filename": "daily-journal-2021.pdf",
            "title": "Daily Journal 2021 Meeting",
            "category": "speech_excerpt",
            "description": "Charlie Munger's remarks at Daily Journal annual meeting",
        },
    ],
}


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


@app.command(name="presets")
def ingest_presets(
    source: str = typer.Option(
        "all",
        "--source",
        "-s",
        help="Which presets to ingest: all, web, or pdfs",
    ),
    preset: str = typer.Option(
        None,
        "--preset",
        "-p",
        help="Specific preset to ingest (web title key or pdf filename key)",
    ),
):
    """Ingest built-in wisdom presets from web and PDF resources."""
    from munger.ingest.processor import ContentProcessor

    try:
        if source not in {"all", "web", "pdfs"}:
            output("Invalid --source. Use: all, web, or pdfs")
            raise typer.Exit(1)

        processor = ContentProcessor()
        total_count = 0
        failed = []

        if source in {"all", "web"}:
            output("Ingesting web presets...")
            web_presets = PRESETS.get("web", [])
            for entry in web_presets:
                if preset and preset != entry.get("title"):
                    continue
                try:
                    output(f"Ingesting {entry['title']}...")
                    count = processor.process_url(
                        entry["url"],
                        title=entry["title"],
                        category=entry["category"],
                    )
                    total_count += count
                    output(f"  Added {count} entries from {entry['title']}")
                except Exception as e:
                    output(f"Error processing {entry['title']}: {e}")
                    failed.append(entry["title"])

        if source in {"all", "pdfs"}:
            output("Ingesting PDF presets...")

            try:
                import munger
                resource_dir = Path(munger.__file__).parent / "resources" / "pdfs"
            except Exception:
                output("Error: Could not locate munger package resources")
                raise typer.Exit(1)

            if not resource_dir.exists():
                output(f"Error: Resources directory not found: {resource_dir}")
                raise typer.Exit(1)

            pdf_presets = PRESETS.get("pdfs", [])
            for entry in pdf_presets:
                if preset and preset != entry.get("filename"):
                    continue
                pdf_path = resource_dir / entry["filename"]

                if not pdf_path.exists():
                    output(f"Warning: Preset PDF not found: {pdf_path}")
                    failed.append(entry["filename"])
                    continue

                try:
                    output(f"Ingesting {entry['title']}...")
                    count = processor.process_file(
                        pdf_path,
                        title=entry["title"],
                        category=entry["category"],
                    )
                    total_count += count
                    output(f"  Added {count} entries from {entry['title']}")
                except Exception as e:
                    output(f"Error processing {entry['title']}: {e}")
                    failed.append(entry["title"])

        output("")
        if total_count > 0:
            output(f"Successfully ingested {total_count} wisdom entries from presets")

        if failed:
            output(f"Failed presets: {', '.join(failed)}")
            if total_count == 0:
                raise typer.Exit(1)

    except typer.Exit:
        raise
    except Exception as e:
        output(f"Error ingesting presets: {e}")
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
