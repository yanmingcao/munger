"""Content processor for ingesting Munger materials."""

from pathlib import Path
from typing import Any

import httpx
from bs4 import BeautifulSoup

from munger.core.models import MungerWisdom, WisdomCategory
from munger.db.vector_store import WisdomVectorStore


class ContentProcessor:
    """Process and ingest content into the wisdom knowledge base."""

    def __init__(self):
        self.vector_store = WisdomVectorStore()

    def process_url(
        self,
        url: str,
        title: str | None = None,
        category: str = "quote",
    ) -> int:
        """
        Process content from a URL.

        Args:
            url: URL to fetch content from
            title: Optional title override
            category: Category for the wisdom

        Returns:
            Number of wisdom entries added
        """
        # Fetch content
        response = httpx.get(url, follow_redirects=True, timeout=30.0)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract text content
        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        # Get text
        text = soup.get_text(separator="\n", strip=True)

        # Use page title if not provided
        if not title:
            title_tag = soup.find("title")
            title = title_tag.get_text(strip=True) if title_tag else url

        # Process the text into chunks
        return self._process_text(text, title, url, category)

    def process_file(
        self,
        file_path: Path,
        title: str | None = None,
        category: str = "quote",
    ) -> int:
        """
        Process content from a file.

        Args:
            file_path: Path to the file
            title: Optional title override
            category: Category for the wisdom

        Returns:
            Number of wisdom entries added
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Determine file type and process accordingly
        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            return self._process_pdf(file_path, title, category)
        elif suffix in [".txt", ".md"]:
            return self._process_text_file(file_path, title, category)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

    def _process_pdf(
        self,
        file_path: Path,
        title: str | None,
        category: str,
    ) -> int:
        """Process a PDF file."""
        try:
            import pdfplumber
        except ImportError:
            raise ImportError("pdfplumber is required for PDF processing")

        text_parts = []

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

        full_text = "\n\n".join(text_parts)
        source = title or file_path.name

        return self._process_text(full_text, source, str(file_path), category)

    def _process_text_file(
        self,
        file_path: Path,
        title: str | None,
        category: str,
    ) -> int:
        """Process a text file."""
        text = file_path.read_text(encoding="utf-8")
        source = title or file_path.name

        return self._process_text(text, source, str(file_path), category)

    def _process_text(
        self,
        text: str,
        title: str,
        source: str,
        category: str,
    ) -> int:
        """
        Process text into wisdom chunks and add to vector store.

        Args:
            text: The text content
            title: Title for the content
            source: Source of the content
            category: Category for the wisdom

        Returns:
            Number of wisdom entries added
        """
        # Parse category
        try:
            wisdom_category = WisdomCategory(category)
        except ValueError:
            wisdom_category = WisdomCategory.QUOTE

        # Split into chunks
        chunks = self._chunk_text(text)

        # Create wisdom entries
        wisdom_items = []
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) < 50:  # Skip very short chunks
                continue

            wisdom = MungerWisdom(
                category=wisdom_category,
                title=f"{title} (Part {i+1})" if len(chunks) > 1 else title,
                content=chunk,
                source=source,
                tags=self._extract_tags(chunk),
            )
            wisdom_items.append(wisdom)

        # Add to vector store
        if wisdom_items:
            self.vector_store.add_wisdom_batch(wisdom_items)

        return len(wisdom_items)

    def _chunk_text(
        self,
        text: str,
        chunk_size: int = 1000,
        overlap: int = 100,
    ) -> list[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to split
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        # Clean up whitespace
        text = " ".join(text.split())

        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence end in the last portion of the chunk
                search_start = max(start + chunk_size - 200, start)
                best_break = end

                for punct in [".", "!", "?", "\n"]:
                    idx = text.rfind(punct, search_start, end + 50)
                    if idx > start:
                        best_break = idx + 1
                        break

                end = best_break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap

        return chunks

    def _extract_tags(self, text: str) -> list[str]:
        """Extract relevant tags from text based on keywords."""
        tags = []
        text_lower = text.lower()

        tag_keywords = {
            "investing": ["invest", "stock", "market", "portfolio", "dividend"],
            "mental_models": ["mental model", "framework", "thinking", "latticework"],
            "psychology": ["psychology", "bias", "behavior", "cognitive"],
            "business": ["business", "company", "management", "moat"],
            "wisdom": ["wisdom", "advice", "lesson", "learn"],
            "mistakes": ["mistake", "error", "failure", "wrong"],
            "success": ["success", "achievement", "excellence"],
            "character": ["character", "integrity", "honest", "trust"],
            "relationships": ["relationship", "partner", "marriage", "friend"],
            "career": ["career", "job", "work", "profession"],
        }

        for tag, keywords in tag_keywords.items():
            if any(kw in text_lower for kw in keywords):
                tags.append(tag)

        return tags[:5]  # Limit to 5 tags
