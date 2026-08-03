"""
Unit tests for Headcanon Story Import System.

Tests all importers (PDF, EPUB, Plain Text, Web), common cleaning rules,
exception handling, metadata extraction, and interface compliance.
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pypdf
import pytest

from app.importers.base import BaseStoryImporter, clean_text
from app.importers.epub_importer import EPUBImporter
from app.importers.exceptions import (
    CorruptFileError,
    EmptyDocumentError,
    InvalidEncodingError,
    MissingFileError,
    NetworkImportError,
    UnsupportedFormatError,
)
from app.importers.pdf_importer import PDFImporter
from app.importers.text_importer import TextImporter
from app.importers.web_importer import WebImporter
from app.models.document import StoryDocument

# ---------------------------------------------------------------------------
# Helpers to generate synthetic test assets in memory
# ---------------------------------------------------------------------------


def create_minimal_pdf_bytes(
    text: str = "Chapter 1: The Beginning\n\nOnce upon a time in a magical land.",
) -> bytes:
    """Create in-memory PDF bytes with extractable text using pypdf."""
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=612, height=792)
    # pypdf 4+ allows adding text or we can mock/write minimal valid PDF structure
    output = io.BytesIO()
    writer.write(output)

    # To ensure text is extractable in tests without complex PDF graphics,
    # we can construct a minimal valid PDF stream containing literal text
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kinds [3 0 R] /Count 1 >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]"
        b" /Contents 4 0 R /Resources << /Font << /F1 << /Type /Font"
        b" /Subtype /Type1 /BaseFont /Helvetica >> >> >> >> endobj\n"
        b"4 0 obj << /Length 55 >> stream\n"
        b"BT /F1 12 Tf 100 700 Td (Chapter 1) Tj ET\n"
        b"endstream\n"
        b"endobj\n"
        b"xref\n"
        b"0 5\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000270 00000 n \n"
        b"trailer << /Size 5 /Root 1 0 R >>\n"
        b"startxref\n"
        b"375\n"
        b"%%EOF\n"
    )
    return pdf_content


def create_minimal_epub_bytes(
    title: str = "Test Story",
    author: str = "Test Author",
    content: str = "<h1>Chapter 1</h1><p>The dragon soared through the sky.</p>",
) -> bytes:
    """Create in-memory EPUB zip bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("mimetype", "application/epub+zip")
        z.writestr(
            "META-INF/container.xml",
            '<?xml version="1.0"?>'
            '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
            '  <rootfiles><rootfile full-path="OEBPS/content.opf" '
            'media-type="application/oebps-package+xml"/></rootfiles>'
            '</container>',
        )
        z.writestr(
            "OEBPS/content.opf",
            '<?xml version="1.0" encoding="utf-8"?>'
            '<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="id" version="2.0">'
            '  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
            f"    <dc:title>{title}</dc:title>"
            f"    <dc:creator>{author}</dc:creator>"
            "    <dc:language>en</dc:language>"
            "  </metadata>"
            "  <manifest>"
            '    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>'
            "  </manifest>"
            "  <spine><itemref idref=\"chapter1\"/></spine>"
            "</package>",
        )
        z.writestr(
            "OEBPS/chapter1.xhtml",
            '<?xml version="1.0" encoding="utf-8"?>'
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">'
            '<html xmlns="http://www.w3.org/1999/xhtml">'
            f"<head><title>{title}</title></head>"
            f"<body>{content}</body>"
            "</html>",
        )
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Clean Text Tests
# ---------------------------------------------------------------------------


class TestCleanText:
    def test_normalizes_curly_quotes_and_apostrophes(self):
        raw = "“Hello,” she said. ‘It’s a secret.’"
        cleaned = clean_text(raw)
        assert '"Hello," she said.' in cleaned
        assert "'It's a secret.'" in cleaned

    def test_normalizes_line_endings(self):
        raw = "Line 1\r\nLine 2\rLine 3"
        cleaned = clean_text(raw)
        assert "\r" not in cleaned
        assert "Line 1\nLine 2\nLine 3" in cleaned

    def test_collapses_excessive_blank_lines(self):
        raw = "Paragraph 1\n\n\n\n\n\nParagraph 2"
        cleaned = clean_text(raw)
        assert "\n\n\n\n" not in cleaned
        assert "Paragraph 1\n\n\nParagraph 2" in cleaned

    def test_collapses_horizontal_whitespace(self):
        raw = "Hello      world!   This   is   a   test."
        cleaned = clean_text(raw)
        assert "Hello world! This is a test." in cleaned

    def test_preserves_dialogue_content(self):
        dialogue = '"What are you doing?" asked Harry.'
        cleaned = clean_text(dialogue)
        assert dialogue in cleaned


# ---------------------------------------------------------------------------
# Text Importer Tests
# ---------------------------------------------------------------------------


class TestTextImporter:
    def test_import_valid_string(self):
        importer = TextImporter()
        doc = importer.import_story("Chapter 1\n\nHarry walked into the room.")
        assert isinstance(doc, StoryDocument)
        assert doc.source_type == "txt"
        assert "Harry walked into the room." in doc.cleaned_text
        assert doc.chapter_count == 1

    def test_import_utf8_file(self, tmp_path: Path):
        file_path = tmp_path / "story.txt"
        file_path.write_text("Chapter 1: The Start\n\nThis is a story.", encoding="utf-8")

        importer = TextImporter()
        doc = importer.import_story(str(file_path))
        assert doc.source_type == "txt"
        assert "This is a story." in doc.cleaned_text

    def test_missing_file_raises_missing_file_error(self):
        importer = TextImporter()
        with pytest.raises(MissingFileError):
            importer.import_story("non_existent_file_12345.txt")

    def test_empty_text_raises_empty_document_error(self):
        importer = TextImporter()
        with pytest.raises(EmptyDocumentError):
            importer.import_story("   \n\n   ")

    def test_invalid_encoding_raises_error(self):
        importer = TextImporter()
        # Invalid UTF-8 sequence that fails utf-8 / utf-8-sig and yields invalid utf-8
        bad_bytes = b"\x80\x81\x82"
        with patch(
            "app.importers.text_importer._decode_bytes",
            side_effect=InvalidEncodingError("Invalid bytes"),
        ):
            with pytest.raises(InvalidEncodingError):
                importer.import_story(bad_bytes)


# ---------------------------------------------------------------------------
# PDF Importer Tests
# ---------------------------------------------------------------------------


class TestPDFImporter:
    def test_validate_non_existent_file_raises(self):
        importer = PDFImporter()
        with pytest.raises(MissingFileError):
            importer.validate_source("missing_file.pdf")

    def test_validate_non_pdf_file_raises(self, tmp_path: Path):
        file_path = tmp_path / "test.txt"
        file_path.write_text("Not a PDF file", encoding="utf-8")
        importer = PDFImporter()
        with pytest.raises(UnsupportedFormatError):
            importer.validate_source(str(file_path))

    def test_validate_invalid_bytes_raises(self):
        importer = PDFImporter()
        with pytest.raises(UnsupportedFormatError):
            importer.validate_source(b"NOT A PDF HEADER")

    def test_import_valid_pdf_bytes(self):
        pdf_bytes = (
            b"%PDF-1.4\n1 0 obj << /Type /Catalog >> endobj"
            b"\ntrailer << /Root 1 0 R >>\n%%EOF"
        )
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Chapter 1\n\nHarry walked into Hogwarts."
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_reader.metadata = None

        importer = PDFImporter()
        with patch.object(importer, "load", return_value=mock_reader):
            doc = importer.import_story(pdf_bytes)
            assert doc.source_type == "pdf"
            assert "Harry walked into Hogwarts." in doc.cleaned_text

    def test_empty_pdf_raises_empty_document_error(self):
        # Create PDF with page that returns empty text
        writer = pypdf.PdfWriter()
        writer.add_blank_page(width=612, height=792)
        buf = io.BytesIO()
        writer.write(buf)

        importer = PDFImporter()
        with pytest.raises(EmptyDocumentError):
            importer.import_story(buf.getvalue())


# ---------------------------------------------------------------------------
# EPUB Importer Tests
# ---------------------------------------------------------------------------


class TestEPUBImporter:
    def test_validate_missing_file_raises(self):
        importer = EPUBImporter()
        with pytest.raises(MissingFileError):
            importer.validate_source("missing_file.epub")

    def test_validate_non_zip_raises(self, tmp_path: Path):
        file_path = tmp_path / "fake.epub"
        file_path.write_text("Not a zip archive", encoding="utf-8")
        importer = EPUBImporter()
        with pytest.raises(UnsupportedFormatError):
            importer.validate_source(str(file_path))

    def test_import_valid_epub_bytes(self):
        epub_bytes = create_minimal_epub_bytes(
            title="The Dragon Adventure",
            author="Arthur Pendelton",
            content="<h1>Chapter 1</h1><p>The dragon soared through the sky.</p>",
        )
        importer = EPUBImporter()
        doc = importer.import_story(epub_bytes)
        assert doc.source_type == "epub"
        assert doc.title == "The Dragon Adventure"
        assert doc.author == "Arthur Pendelton"
        assert "The dragon soared" in doc.cleaned_text

    def test_corrupt_epub_raises_corrupt_file_error(self):
        importer = EPUBImporter()
        fake_zip = io.BytesIO()
        with zipfile.ZipFile(fake_zip, "w") as z:
            z.writestr("dummy.txt", "not an epub structure")

        with pytest.raises((CorruptFileError, EmptyDocumentError)):
            importer.import_story(fake_zip.getvalue())


# ---------------------------------------------------------------------------
# Web Importer Tests
# ---------------------------------------------------------------------------


class TestWebImporter:
    def test_validate_invalid_url_raises(self):
        importer = WebImporter()
        with pytest.raises(UnsupportedFormatError):
            importer.validate_source("ftp://invalid-url-schema")

    def test_import_ao3_html_content(self):
        html = """
        <html>
          <body>
            <div id="workskin">
              <h2 class="title">A Wandering Hero</h2>
              <h3 class="byline">by FamousAuthor</h3>
              <div class="userstuff">
                <p>Chapter 1: The Journey Begins.</p>
                <p>He packed his bags and left at dawn.</p>
              </div>
            </div>
          </body>
        </html>
        """
        importer = WebImporter()
        doc = importer.import_story(html)
        assert doc.source_type == "ao3"
        assert doc.title == "A Wandering Hero"
        assert doc.author == "by FamousAuthor"
        assert "The Journey Begins." in doc.cleaned_text

    def test_import_gutenberg_html_content(self):
        html = """
        <html>
          <body>
            Title: Pride and Prejudice
            Author: Jane Austen

            *** START OF THE PROJECT GUTENBERG EBOOK PRIDE AND PREJUDICE ***
            Chapter 1
            It is a truth universally acknowledged.
            *** END OF THE PROJECT GUTENBERG EBOOK PRIDE AND PREJUDICE ***
          </body>
        </html>
        """
        importer = WebImporter()
        doc = importer.import_story(html)
        assert doc.source_type == "gutenberg"
        assert doc.title == "Pride and Prejudice"
        assert doc.author == "Jane Austen"
        assert "universally acknowledged" in doc.cleaned_text

    def test_import_generic_web_page(self):
        html = """
        <html>
          <head><title>Generic Story Title</title></head>
          <body>
            <article>
              <h1>Chapter One</h1>
              <p>Once upon a time in a digital world.</p>
            </article>
          </body>
        </html>
        """
        importer = WebImporter()
        doc = importer.import_story(html)
        assert doc.source_type in ("web", "txt")
        assert "digital world" in doc.cleaned_text

    def test_http_404_raises_network_import_error(self):
        importer = WebImporter()
        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch("httpx.Client.get", return_value=mock_response):
            with pytest.raises(NetworkImportError):
                importer.import_story("https://archiveofourown.org/works/999999999")

    def test_empty_html_raises_empty_document_error(self):
        importer = WebImporter()
        html = "<html><body></body></html>"
        with pytest.raises(EmptyDocumentError):
            importer.import_story(html)


# ---------------------------------------------------------------------------
# Interface Compliance Test
# ---------------------------------------------------------------------------


def test_all_importers_implement_public_interface():
    importers = [PDFImporter(), EPUBImporter(), TextImporter(), WebImporter()]
    for imp in importers:
        assert isinstance(imp, BaseStoryImporter)
        assert hasattr(imp, "validate_source")
        assert hasattr(imp, "load")
        assert hasattr(imp, "extract")
        assert hasattr(imp, "clean")
        assert hasattr(imp, "import_story")
