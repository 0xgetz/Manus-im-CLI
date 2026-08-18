# Security Policy

The maintainers and contributors of **Manus-im-CLI** take security seriously and appreciate responsible disclosure of vulnerabilities.

## Supported Versions

Security updates are provided for the latest minor version in the `1.x` release line.

| Version | Supported |
|---|---|
| 1.0.x | Yes |
| < 1.0.0 | No |

## Reporting a Vulnerability

Please do not disclose a suspected security vulnerability publicly before it has been assessed. Report it privately to **[api-support@manus.ai](mailto:api-support@manus.ai)** and include a concise description, affected version, reproducible steps, impact, and relevant environment details.

If encrypted communication is necessary, request the current PGP key through the reporting channel before transmitting sensitive proof-of-concept material.

## Disclosure Process

The maintainers aim to acknowledge a report within 48 hours, validate the issue, prepare and test a patch where appropriate, then publish a release and a security advisory. Credit will be given to the reporter unless they request otherwise.

## Release Integrity

Security releases should use a version that matches `pyproject.toml`, an annotated signed Git tag, release artifacts with checksums, and a software bill of materials. CI, dependency audit, lint, formatting, and test checks should pass before publication.
