# Changelog

All notable changes to this project are documented in this file.

## [1.0.1] - 2026-08-18

### Security

- Reject untrusted or non-HTTPS API base URLs by default before an API key can be sent, with an explicit opt-in for trusted custom endpoints.
- Redact sensitive configuration values by default and require an interactive confirmation before a secret can be displayed.
- Remove request payloads and response bodies from debug output.
- Validate presigned upload URLs as HTTPS and disable redirects during upload.

### Fixed

- Stream file uploads instead of loading entire files into memory.
- Use an event cursor in `task watch` so that new events and terminal statuses are not skipped after the first page.
- Make interactive and manual task confirmation default to rejection.
- Handle invalid browser selection indexes without sending an action.
- Add Python 3.10 compatibility for TOML parsing.
- Align package, security policy, and changelog versions on the `1.x` release line.

### Changed

- Add dependency auditing to CI and restrict the workflow token to read-only repository content.
- Add regression tests for endpoint validation, cursor-based watching, configuration redaction, upload validation, and confirmation defaults.

## [0.1.0] - 2026-08-12

- Initial release of `Manus-im-CLI` supporting authentication, task creation and lifecycle management (`--watch`, `send`, `confirm`), projects, file uploads, browser listing, and config management.
