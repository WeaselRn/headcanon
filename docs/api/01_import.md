# Import API

## Purpose

The Import API is responsible for transforming an external story into a Headcanon Universe.

It accepts supported story formats, extracts the text, reconstructs the universe, initializes the World State, and stores the resulting universe for future interactions.

This is the entry point for every new Headcanon universe.

---

# Responsibilities

The Import API is responsible for

- Receiving story input
- Validating uploaded files
- Extracting text
- Building the Universe Model
- Initializing the World State
- Persisting the universe
- Returning a Universe ID

---

# Endpoint

POST

/api/v1/import

---

# Supported Input Types

The API accepts

- Plain Text
- PDF
- EPUB
- Markdown
- URL

Future formats may be added without changing the endpoint.

---

# Request

The request contains

- Story Source
- Source Type
- Universe Name (optional)
- Import Options (optional)

Example

{
    "type": "pdf",
    "title": "Harry Potter",
    "file": "...",
    "options": {
        "generate_media": false
    }
}

---

# Validation

Before processing

Validate

- Supported format
- File integrity
- Maximum file size
- Readable content
- Non-empty input

Invalid requests should return descriptive validation errors.

---

# Processing Pipeline

Request

↓

Import Service

↓

Text Extraction

↓

Universe Builder

↓

Universe Validation

↓

World State Initialization

↓

Persistence

↓

Response

---

# Successful Response

Return

- Universe ID
- Universe Name
- Import Status
- Processing Time
- Current World State Version

Example

{
    "universe_id": "...",
    "status": "completed",
    "world_state_version": 1
}

---

# Error Responses

Possible errors

400

Invalid Request

401

Unauthorized (future)

413

File Too Large

415

Unsupported Format

422

Universe Construction Failed

500

Internal Server Error

---

# Import Options

Optional configuration

- Generate media immediately
- Skip media generation
- Enable debug mode
- Preserve chapter structure

Future options may be added.

---

# Idempotency

Uploading the same story multiple times creates separate universes.

Each universe receives a unique Universe ID.

Universes are independent from one another.

---

# Security

Validate

- File type
- File size
- Malicious uploads
- Unsupported content

Never execute uploaded content.

---

# Performance

The endpoint should

- Return progress updates (future)
- Process asynchronously for large stories
- Avoid blocking other requests

---

# Future Extensions

Potential additions

- Batch imports
- ZIP archives
- Cloud storage imports
- Public story libraries
- OCR support

---

# Related Documents

- ../runtime_pipeline.md
- ../engines/01_universe_builder.md
- ../universe/01_universe_schema.md
- ../universe/09_world_state.md