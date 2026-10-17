# Changelog

All notable changes to Moatbreak. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-10-17

First public release.

### Changed

- New name: Moatbreak, skill ID `moatbreak`. The skill was previously used
  privately as `competitor-teardown` 1.1. The four modes, the references, the
  templates and the scripts are unchanged from that version apart from the
  name.
- The working folder for user data is still `teardown/`, so existing projects
  keep working.

### Added

- Claude Code plugin and marketplace manifests in `.claude-plugin/`, so the
  skill installs with `/plugin marketplace add bogaja/moatbreak`.
- GitHub Actions workflow that runs the 71 tests on Python 3.8 to 3.13.
- README with install instructions for claude.ai, Claude Code and manual
  copy, plus a short German section.
