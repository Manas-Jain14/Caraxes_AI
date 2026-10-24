# ADR-001: Adopt Nebius Token Factory with NVIDIA Nemotron

- **Status:** Implemented on `phase-4-nebius-nemotron`; authenticated inference verification and review/merge pending.
- **Date:** 2026-10-24

## Context

The existing FastAPI chat route called Google Gemini. The Nebius x NVIDIA Global AI Hackathon phase requires the main chat path to use an eligible NVIDIA open model through Nebius Token Factory while preserving the existing `/api/chat` request and response format.

## Problem

The existing provider did not exercise the Nebius + NVIDIA model path required by this project phase. The provider change must not alter the public chat contract or introduce future agent functionality.

## Decision

Use Nebius Token Factory's documented OpenAI-compatible chat-completions API, through the OpenAI Python client, for the active `/api/chat` provider. Configure:

- Base URL: `https://api.tokenfactory.nebius.com/v1/`
- Authentication: `NEBIUS_API_KEY` (Bearer authentication handled by the SDK)
- Model: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`, configurable as `NEBIUS_MODEL`

The current Nebius [public model catalog](https://tokenfactory.nebius.com/model-catalog.md) lists this NVIDIA text-to-text model. NVIDIA describes the Nemotron family as open models in its [Nemotron overview](https://developer.nvidia.com/topics/ai/nemotron). Check event rules separately for final eligibility requirements.

## Alternatives considered

- Keep Gemini as the main provider: rejected because it would not satisfy the Phase 4 provider objective.
- Add a generic multi-provider framework: rejected as unnecessary for the current single active provider.
- Call the REST API directly: rejected in favor of the OpenAI client used by Nebius's own examples.

## Rationale

Nebius documents the OpenAI-compatible interface used by the existing backend, so the selected client supports the required integration without adding an orchestration framework. The configured Nemotron model is currently listed in Nebius's public catalog. Gemini is not a fallback on `/api/chat`; its helper remains only for the separate microphone test script. No comparative performance claims are made.

## Consequences

- Requires a Nebius API key and a valid model identifier in environment configuration.
- The chat route depends on Nebius availability and sends user chat text to that service.
- Configuration and upstream failures return explicit `503`/`502` responses without exposing credentials.
- Mocked provider/API tests and local health checks pass, but authenticated live inference remains unverified.
- The legacy Gemini code/dependency remains for the existing voice test helper; it is not a production fallback.

## Future considerations

The provider is isolated in one small AI module. Additional providers or fallback behavior should be considered only when a concrete requirement exists.
