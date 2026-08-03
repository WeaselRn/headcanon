"""
Web Story Importer for Headcanon.

Imports and extracts readable story content from web sources including AO3
(Archive of Our Own), Wattpad, Project Gutenberg, and generic web pages.
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup, Tag

from app.importers.base import BaseStoryImporter
from app.importers.exceptions import (
    EmptyDocumentError,
    NetworkImportError,
    ParsingFailureError,
    UnsupportedFormatError,
)


class WebImporter(BaseStoryImporter):
    """
    Importer for Web documents (AO3, Wattpad, Project Gutenberg, Generic Web).

    Responsibilities:
      - Fetch HTML from HTTP/HTTPS URL using httpx (or accept raw HTML for testing)
      - Route parsing to site-specific parsers (AO3, Wattpad, Gutenberg, Generic)
      - Strip navigation, ads, headers, footers, comments, and scripts
      - Extract title, author, chapter structure, and story text
      - Return clean UTF-8 text
    """

    def validate_source(self, source: str) -> bool:
        """Validate URL syntax or raw HTML string."""
        if not isinstance(source, str):
            raise UnsupportedFormatError(
                f"Web source must be a URL string or HTML string, got {type(source)}."
            )

        src = source.strip()
        if not src:
            raise UnsupportedFormatError("Web source string is empty.")

        # Check if URL
        if src.startswith(("http://", "https://")):
            parsed = urlparse(src)
            if not parsed.netloc:
                raise UnsupportedFormatError(f"Invalid URL: '{src}'")
            return True

        # Check if raw HTML string
        if (
            "<html" in src.lower()
            or "<body" in src.lower()
            or "<div" in src.lower()
            or "<p" in src.lower()
        ):
            return True

        raise UnsupportedFormatError(
            f"Source '{src}' is neither a valid HTTP(S) URL nor an HTML snippet."
        )

    def load(self, source: str) -> tuple[str, str]:
        """
        Fetch HTML content from HTTP(S) URL or return raw HTML.

        Returns:
            Tuple of (html_content, url_or_source).
        """
        src = source.strip()
        if src.startswith(("http://", "https://")):
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Headcanon/1.0"}
                with httpx.Client(follow_redirects=True, timeout=15.0) as client:
                    response = client.get(src, headers=headers)
                    if response.status_code >= 400:
                        raise NetworkImportError(
                            f"HTTP request to '{src}' failed with status code "
                            f"{response.status_code}."
                        )
                    return response.text, src
            except httpx.HTTPError as exc:
                raise NetworkImportError(f"Network failure while fetching '{src}': {exc}") from exc
            except Exception as exc:
                if isinstance(exc, NetworkImportError):
                    raise
                raise NetworkImportError(
                    f"Unexpected network error fetching '{src}': {exc}"
                ) from exc

        # Raw HTML string
        return src, "http://localhost/raw-html"

    def extract(self, loaded_data: tuple[str, str]) -> tuple[str, dict[str, Any]]:
        """Parse HTML content using site-specific parser strategy."""
        html_content, url = loaded_data
        if not html_content or not html_content.strip():
            raise EmptyDocumentError("Web page HTML content is empty.")

        soup = BeautifulSoup(html_content, "html.parser")

        # Select parser
        parser = _select_web_parser(url, html_content)
        raw_text, metadata = parser.parse(soup, url, html_content)

        if not raw_text or not raw_text.strip():
            raise EmptyDocumentError("Failed to extract story text from web page.")

        return raw_text, metadata


# ---------------------------------------------------------------------------
# Site Parsers
# ---------------------------------------------------------------------------


class BaseWebParser:
    """Base interface for site-specific HTML parsers."""

    def can_handle(self, url: str, html: str) -> bool:
        return False

    def parse(self, soup: BeautifulSoup, url: str, html: str) -> tuple[str, dict[str, Any]]:
        raise NotImplementedError


class AO3Parser(BaseWebParser):
    """Parser for Archive of Our Own (AO3) stories."""

    def can_handle(self, url: str, html: str) -> bool:
        return "archiveofourown.org" in url or "userstuff" in html or "workskin" in html

    def parse(self, soup: BeautifulSoup, url: str, html: str) -> tuple[str, dict[str, Any]]:
        # Title
        title_elem = soup.select_one("#workskin h2.title, .title.heading")
        title = title_elem.get_text().strip() if title_elem else "Untitled AO3 Story"

        # Author
        author_elem = soup.select_one("a[rel='author'], #workskin h3.byline")
        author = author_elem.get_text().strip() if author_elem else "Unknown"

        # Story content
        work_elem = soup.select_one("#workskin, #chapters, .userstuff")
        if not work_elem:
            raise ParsingFailureError(
                "Could not locate story content element (#workskin or .userstuff) on AO3 page."
            )

        # Clean non-content elements inside workskin
        for elem in work_elem.select(".kudos, .bookmarks, .comments, nav, script, style"):
            elem.decompose()

        chapters = work_elem.select(".userstuff")
        chapter_texts = []

        if chapters:
            for ch in chapters:
                t = _soup_to_clean_text(ch)
                if t:
                    chapter_texts.append(t)
        else:
            t = _soup_to_clean_text(work_elem)
            if t:
                chapter_texts.append(t)

        raw_text = "\n\n".join(chapter_texts)

        metadata = {
            "source_type": "ao3",
            "title": title,
            "author": author,
            "language": "English",
            "chapter_count": len(chapter_texts),
            "url": url,
        }

        return raw_text, metadata


class WattpadParser(BaseWebParser):
    """Parser for Wattpad stories."""

    def can_handle(self, url: str, html: str) -> bool:
        return "wattpad.com" in url

    def parse(self, soup: BeautifulSoup, url: str, html: str) -> tuple[str, dict[str, Any]]:
        # Title
        title_elem = soup.select_one("h1, .header-title, title")
        title = title_elem.get_text().strip() if title_elem else "Untitled Wattpad Story"

        # Author
        author_elem = soup.select_one(".author-name, .byline, a[href*='/user/']")
        author = author_elem.get_text().strip() if author_elem else "Unknown"

        # Story paragraphs
        paras = soup.select("pre, .story-part p, div[data-p-id] p")
        if not paras:
            # Fallback to pre tag
            pre = soup.find("pre")
            if pre:
                raw_text = pre.get_text().strip()
            else:
                raise ParsingFailureError("Could not locate Wattpad story content.")
        else:
            raw_text = "\n\n".join(p.get_text().strip() for p in paras if p.get_text().strip())

        metadata = {
            "source_type": "wattpad",
            "title": title,
            "author": author,
            "language": "English",
            "chapter_count": 1,
            "url": url,
        }

        return raw_text, metadata


class GutenbergParser(BaseWebParser):
    """Parser for Project Gutenberg texts."""

    def can_handle(self, url: str, html: str) -> bool:
        return "gutenberg.org" in url or "PROJECT GUTENBERG EBOOK" in html

    def parse(self, soup: BeautifulSoup, url: str, html: str) -> tuple[str, dict[str, Any]]:
        # Strip Gutenberg header and footer blocks
        text = soup.get_text()

        start_match = re.search(
            r"\*\*\*\s*START OF TH(?:IS|E) PROJECT GUTENBERG EBOOK[^\n]*\*\*\*", text, re.I
        )
        end_match = re.search(
            r"\*\*\*\s*END OF TH(?:IS|E) PROJECT GUTENBERG EBOOK[^\n]*\*\*\*", text, re.I
        )

        start_pos = start_match.end() if start_match else 0
        end_pos = end_match.start() if end_match else len(text)

        body_text = text[start_pos:end_pos].strip()

        # Title & Author from Gutenberg header
        title_match = re.search(r"Title:\s*([^\n]+)", text)
        title = title_match.group(1).strip() if title_match else "Gutenberg Story"

        author_match = re.search(r"Author:\s*([^\n]+)", text)
        author = author_match.group(1).strip() if author_match else "Unknown"

        metadata = {
            "source_type": "gutenberg",
            "title": title,
            "author": author,
            "language": "English",
            "chapter_count": 1,
            "url": url,
        }

        return body_text, metadata


class GenericWebParser(BaseWebParser):
    """Fallback parser for generic HTML web pages."""

    def can_handle(self, url: str, html: str) -> bool:
        return True

    def parse(self, soup: BeautifulSoup, url: str, html: str) -> tuple[str, dict[str, Any]]:
        # Remove nav, footer, scripts, ads, comments
        for elem in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
            elem.decompose()

        for selector in (".ad", ".ads", ".comments", ".comment-list", ".navigation", "#comments"):
            for elem in soup.select(selector):
                elem.decompose()

        # Title
        title_elem = (
            soup.select_one("meta[property='og:title']") or soup.find("h1") or soup.find("title")
        )
        if title_elem:
            title = (
                title_elem.get("content") if title_elem.name == "meta" else title_elem.get_text()
            )
            title = str(title).strip()
        else:
            title = "Web Import"

        # Author
        author_elem = soup.select_one("meta[name='author'], meta[property='article:author']")
        author = str(author_elem.get("content")).strip() if author_elem else "Unknown"

        # Target main content area
        main_elem = soup.select_one("article, main, .entry-content, .post-content, #content, body")
        if not main_elem:
            main_elem = soup.find("body") or soup

        raw_text = _soup_to_clean_text(main_elem)

        metadata = {
            "source_type": "web",
            "title": title,
            "author": author,
            "language": "English",
            "chapter_count": 1,
            "url": url,
        }

        return raw_text, metadata


def _select_web_parser(url: str, html: str) -> BaseWebParser:
    """Select the appropriate web parser strategy based on URL and HTML content."""
    parsers = [AO3Parser(), WattpadParser(), GutenbergParser(), GenericWebParser()]
    for p in parsers:
        if p.can_handle(url, html):
            return p
    return GenericWebParser()


def _soup_to_clean_text(elem: Tag) -> str:
    """Extract paragraphs and headings from a DOM element into clean text."""
    lines: list[str] = []
    for child in elem.find_all(["h1", "h2", "h3", "h4", "p", "blockquote", "pre"]):
        t = child.get_text().strip()
        if t:
            if child.name.startswith("h"):
                lines.append(f"\n\n{t}\n\n")
            else:
                lines.append(t)

    if not lines:
        return elem.get_text().strip()

    return "\n\n".join(lines)
