# Security Policy

## Scope

This security policy applies to the AquaIntel codebase, including the Flask backend, ESP32 firmware, and web dashboard.

## Reporting a Vulnerability

If you discover a security vulnerability, **please do not open a public GitHub issue.**

Instead, report it privately by:

1. Opening a GitHub issue with the title prefix `[SECURITY]` — keep the description minimal (do not include exploit details publicly).
2. Emailing the maintainers directly (add contact email here before publishing).

We will acknowledge receipt within 72 hours and aim to release a patch within 14 days for confirmed vulnerabilities.

## Known Security Considerations

This is a **research prototype**. Before production deployment, be aware of:

| Area | Risk | Mitigation |
|------|------|-----------|
| Flask server | No authentication on API endpoints | Add API key or token auth before exposing to internet |
| ESP32 firmware | WiFi credentials hardcoded in `.ino` | Use NVS (Non-Volatile Storage) for credentials in production |
| Dashboard | CORS open to all origins | Restrict `flask-cors` allowed origins in production |
| Manual override | No operator authentication | Add session-based auth before production deployment |
| Model artifacts | Pickle files (`.pkl`) can execute arbitrary code | Only load models from trusted sources; verify checksums |

## Security Best Practices for Deployers

- Run the Flask server behind a reverse proxy (nginx) with HTTPS in production.
- Never expose the Flask API directly to the public internet without authentication.
- Store WiFi credentials and server IPs in ESP32 NVS, not hardcoded in firmware.
- Verify SHA-256 checksums of downloaded model artifacts before loading.
- Restrict access to the `/retrain` and `/feedback` endpoints to authenticated operators.
