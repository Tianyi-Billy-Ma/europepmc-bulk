# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-05-02

### Fixed
- README badges now render correctly on GitHub (cache-bust by removing `.svg` extension)
- PyPI license metadata now uses SPDX expression (`license = "MIT"`) instead of deprecated file-embed format

## [0.1.0] - 2026-05-01

### Added
- Initial release
- REST search with cursor pagination (`AbstractHarvester`)
- Bulk FTP/HTTPS downloads (`FTPDownloader`)
- Annotations API batch collection (`AnnotationsCollector`)
- OAI-PMH incremental harvester (`OAIUpdater`)
- JATS XML parser (`parse_jats_article`)
- Click CLI: `europepmc-bulk`
- Sync HTTP client with retry/backoff
- Atomic file writes and persistent resume state
- Documentation site
