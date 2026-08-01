# Storage API

## Purpose

The Storage API manages the persistence, retrieval, and lifecycle of all universe data and media assets.

Rather than interacting directly with Backblaze B2 or other storage providers, all storage operations are routed through this API to provide a consistent abstraction layer.

The Storage API is responsible for storing both structured universe data and generated multimedia assets.

---

# Responsibilities

The Storage API is responsible for

- Saving universe data
- Loading universe data
- Managing snapshots
- Managing media assets
- Managing metadata
- Handling storage validation
- Supporting future storage providers

---

# Endpoint

GET

/api/v1/storage/health

Returns storage connectivity information.

---

# Endpoint

POST

/api/v1/storage/save

Persists runtime data.

Supported resources

- Universe
- World State
- Snapshot
- Metadata

---

# Endpoint

GET

/api/v1/storage/load

Loads stored runtime data.

Supported resources

- Universe
- Snapshot
- World State
- Metadata

---

# Endpoint

DELETE

/api/v1/storage/delete

Deletes a stored resource.

Supported resources

- Universe
- Snapshot
- Media Asset
- Metadata

Deletion policies are determined by the Storage Layer.

---

# Storage Resources

The API manages

- Universe Model
- World State
- Snapshots
- Scene Metadata
- Generated Images
- Narration Audio
- Ambient Audio
- Provenance

---

# Storage Workflow

Request

↓

Validate Resource

↓

Serialize Data

↓

Upload

↓

Verify Upload

↓

Update Metadata

↓

Return Success

---

# Retrieval Workflow

Request

↓

Locate Resource

↓

Validate

↓

Download

↓

Deserialize

↓

Return Resource

---

# Validation

Before every operation

Verify

- Resource exists
- Universe exists
- Valid identifiers
- Storage accessibility
- Resource integrity

Invalid requests should fail before contacting storage.

---

# Metadata

Every stored resource contains

- Resource ID
- Universe ID
- Resource Type
- Version
- Created Timestamp
- Last Modified
- Checksum

Metadata is used for validation and version control.

---

# Integrity Verification

After every upload

Verify

- Upload completed
- File size matches
- Checksum valid
- Metadata stored

Resources failing verification should be retried.

---

# Error Responses

400

Invalid Request

404

Resource Not Found

409

Resource Conflict

422

Validation Failed

500

Storage Failure

---

# Performance

The Storage API should

- Upload asynchronously where possible
- Support streaming for large assets
- Minimize duplicate uploads
- Cache frequently accessed metadata

---

# Security

Validate every request.

Never expose

- Storage credentials
- Internal bucket structure
- Access tokens
- Internal file paths

Signed URLs should be used for media access where applicable.

---

# Future Extensions

Potential additions

- Multiple storage providers
- Automatic backups
- Cross-region replication
- Storage analytics
- Cold storage
- Lifecycle policies

---

# Related Documents

- ../storage/01_backblaze.md
- ../storage/02_storage_schema.md
- ../storage/03_media_library.md
- ../storage/04_provenance.md
- ../storage/06_snapshots.md
