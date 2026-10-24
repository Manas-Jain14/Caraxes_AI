# CARAXES Product Requirements

## Product vision

CARAXES is a multilingual, voice-first desktop assistant that can understand user requests, reason about them, and eventually perform useful tasks through controlled tools.

## Problem

People need an assistant that can accept natural spoken or written requests in English, Hindi, and Hinglish, respond clearly, and eventually help with tasks without taking unsafe or unverifiable actions.

## Target user

The initial target is an individual desktop user who wants a local, voice-oriented assistant with a simple text-chat interface and a path toward carefully controlled task automation.

## Current product state

### Implemented

- FastAPI health and chat endpoints.
- Main `POST /api/chat` inference through Nebius Token Factory and a configured NVIDIA Nemotron model (Phase 4 feature branch).
- Local audio recording and faster-whisper transcription utilities.
- An openWakeWord detection utility and a separate custom-model training workspace.

### In progress

- Production custom Caraxes wake-word model training and validation (Phase 3B).
- Authenticated live verification and review/merge of the Nebius + Nemotron provider change (Phase 4).

### Planned

- End-to-end voice conversation, wake-word activation, text-to-speech, tool use, web research, personal knowledge retrieval, persistent memory, and desktop UI.

## Requirements

### Goals

- Provide a minimal, testable chat API using the selected hosted NVIDIA model.
- Develop toward natural English, Hindi, and Hinglish interaction.
- Add future assistant actions only through controlled, verifiable capabilities.

### Functional requirements

- The current backend exposes `GET /health` and `POST /api/chat`.
- The chat route forwards text to the configured Nebius Token Factory model and returns the existing response shape.
- Voice recording, speech transcription, and a pretrained wake-word utility are separate local components; they are not yet an end-to-end assistant flow.

### Non-functional requirements

- Keep provider configuration out of source-controlled files.
- Keep backend components focused, testable, and incrementally replaceable.
- Do not claim live provider availability, language quality, model performance, or hackathon eligibility without verification.

### Voice-first interaction — planned end-to-end

The product should support microphone input, wake-word activation, speech recognition, reasoning, and spoken responses. Audio recording and speech recognition utilities exist, but the complete voice loop and TTS are not implemented.

### Multilingual interaction

CARAXES is intended to support English, Hindi, and Hinglish. The current API forwards text to the configured language model; no separate language detector or quality guarantee is implemented.

### Agentic task execution — planned

The assistant should eventually request actions through explicitly defined tools rather than executing arbitrary commands. Tool calling is not implemented in the current chat path.

### Personal knowledge — planned

Future versions may retrieve relevant information from user-approved documents and persistent memory. RAG and memory are not implemented.

### Controlled computer interaction — planned

Future computer actions must be restricted to approved capabilities and a user-controlled workspace. Unrestricted shell execution is out of scope.

### Safety, permissions, and verification — planned

Tool input validation, least privilege, user confirmation for dangerous actions, and post-action verification are requirements for future execution features. No permission manager or action-verification framework currently exists.

## Hackathon objective

For the Nebius x NVIDIA Global AI Hackathon, the current Phase 4 objective is to route the existing chat API through Nebius Token Factory to an NVIDIA Nemotron model. This integration alone does not implement the longer-term agent vision or establish eligibility under event rules.
