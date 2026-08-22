<!--
SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
SPDX-License-Identifier: Apache-2.0
-->

# Decision Engine Modules v2.0.6 \[2026-08-21\]

Fixed GCE billing. Improved install, setup, and control procedures. Compatible with HTCondor Python binding v2.

## Changes Since Last Release

### New features / functionalities

- Added release as RPM plus PyPI packages
- Improved compatibility and separation with GlideinWMS Frontend
- Remove AWS mentions in glidein_requests.py (PR #521)
- Extended cluster token duration to 30 days (PR #523)
- Added HTCondor v2 Python binding support (PR #526)

### Changed defaults / behaviours

### Deprecated / removed options and commands

### Security Related Fixes

### Bug Fixes

- Improved GCE Billing and added unit tests (PR #516)
- Fixed monitoring bugs (PR #518)
- Fixed glideclient deadvertising (PR #519)

### Testing / Development

### Known Issues

## Template

This template section should stay at the bottom of the document.
Whenever a new release is cut, the section title should change, empty subsections removed, and a new "Changes Since Last Release" with the template subsections added on top.
This should be a description of the changes, not a Git log. Operators and users affecting changes are especially important to highlight.
Please classify the code changes using the listed subsections. If a new one is needed, add it also to the template.

## Changes Since Last Release OR vX.Y.Z \[yyyy-mm-dd\]

### New features / functionalities

- item one of the list
- item N

### Changed defaults / behaviours

### Deprecated / removed options and commands

### Security Related Fixes

### Bug Fixes

### Testing / Development

### Known Issues
