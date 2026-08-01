# Deployment

## Purpose

This document describes how the Headcanon platform is deployed across development, staging, and production environments.

It covers infrastructure, required services, configuration, deployment workflow, monitoring, and maintenance.

---

# Deployment Architecture

Client (Next.js)

↓

Frontend Hosting

↓

FastAPI Backend

↓

Gemini API

↓

Backblaze B2

↓

Persistent Universe Storage

---

# Services

## Frontend

Technology

- Next.js
- React
- Tailwind CSS

Responsibilities

- Story import
- Universe exploration
- Character interaction
- Media gallery

---

## Backend

Technology

- FastAPI
- Python

Responsibilities

- Universe reconstruction
- Simulation
- Interaction
- Media generation
- Storage management

---

## External Services

Gemini

- Universe reconstruction
- Character reasoning
- Simulation
- Scene generation
- Media prompts

Backblaze B2

Stores

- Universes
- World states
- Snapshots
- Images
- Narration
- Metadata
- Provenance

---

# Environment Variables

Backend

GOOGLE_API_KEY

BACKBLAZE_KEY_ID

BACKBLAZE_APPLICATION_KEY

BACKBLAZE_BUCKET

BACKBLAZE_ENDPOINT

Frontend

NEXT_PUBLIC_API_URL

---

# Development Environment

Requirements

Python

Node.js

Backblaze account

Gemini API Key

Run

Frontend

↓

Backend

↓

Import Story

↓

Interact

↓

Verify Storage

---

# Production Environment

Recommended deployment

Frontend

Vercel

Backend

Cloud Run / Railway / Render

Storage

Backblaze B2

LLM

Gemini API

---

# Deployment Workflow

Developer

↓

Build Frontend

↓

Run Backend Tests

↓

Run Type Checks

↓

Run Prompt Validation

↓

Deploy Backend

↓

Deploy Frontend

↓

Smoke Tests

↓

Production

---

# Configuration

Separate configuration for

Development

Staging

Production

Never commit secrets.

Use environment variables.

---

# Monitoring

Monitor

- API latency
- Prompt failures
- Storage failures
- Simulation failures
- Snapshot failures

Collect logs from all services.

---

# Backup Strategy

Regularly back up

- Universe data
- World states
- Snapshots
- Metadata
- Prompt versions

Media assets remain stored in Backblaze B2.

---

# Scaling

Scale independently

Frontend

Backend

Storage

LLM requests

Universe simulations

Media generation

The simulation layer should remain stateless outside the persisted World State.

---

# Security

Never expose

- API keys
- Storage credentials
- Internal prompts
- User data

Validate all uploaded files before processing.

Sanitize user input before passing to LLMs.

---

# Release Checklist

Before every release

✓ Backend tests pass

✓ Frontend builds successfully

✓ Prompt validation passes

✓ Storage connectivity verified

✓ Gemini connectivity verified

✓ Snapshot loading verified

✓ Media generation verified

✓ Documentation updated

---

# Related Documents

- runtime_pipeline.md
- error_handling.md
- testing_strategy.md
- storage/01_backblaze.md
- storage/02_storage_schema.md
- api.md