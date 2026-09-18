---
on:
  workflow_dispatch:
  issues:
    types: [opened, labeled]
permissions:
  contents: write
  issues: read
  pull-requests: write
  copilot-requests: write
safe-outputs:
  create-pull-request:
engine: copilot
---

# Medjool Farm Manager — Full Frontend Redesign Agent

Act as the lead UI engineering agent and implement the redesign directly in the repository.

## Mission
Transform the existing PySide6 Arabic RTL desktop ERP into a coherent production-quality farm management application while preserving all working business functionality.

## Mandatory sequence

### Phase 1 — Audit
Inspect every file under `app/`, `tests/`, `.github/`, and packaging/configuration files. Map each presentation page to its service/repository and identify existing workflows. Do not delete anything.

### Phase 2 — Shared design system
Build one reusable presentation foundation for typography, spacing, colors, controls, tables, cards, badges, dialogs, page headers, toolbars and empty/error states. Keep styling centralized.

### Phase 3 — Application shell
Redesign `MainWindow`: RTL sidebar, application identity, grouped navigation, active item, top context/header, window-level status and consistent content margins.

### Phase 4 — Modules
Implement coherent production UI for every module that already has backend support:
- Dashboard
- Farm structure
- Irrigation/fertilization / agriculture
- Inventory
- Purchases
- Operations / maintenance
- Harvest / crop
- Sales / customers
- Assets / equipment
- Employees / payroll
- Consultants
- Reports
- Settings

Where backend support is missing, create a clearly designed non-destructive placeholder rather than inventing persistence behavior.

### Phase 5 — UX quality
Replace developer-style controls with real forms and dialogs where practical. Add validation, search/filter, sorting, status badges, confirmations, refresh behavior, useful empty states and readable error handling. Ensure 1180x720 remains usable.

### Phase 6 — Verification
Run:
- `python -m compileall app`
- `python -m pytest -q`

Fix regressions minimally. Do not change database schema for visual work.

### Phase 7 — Release review
Verify `.github/workflows/android-release.yml`, `desktop-release.yml`, `generate-keystore.yml`, `frontend-agent.yml`, `ci.yml`, and this workflow remain present and syntactically coherent. Do not replace or delete release automation.

## Non-negotiable constraints
- PySide6 only for desktop UI.
- SQLite remains local/offline.
- Business logic stays out of presentation.
- Repositories/services remain the access boundary for data operations.
- No paid runtime APIs or network dependencies.
- No deletion of domain models, repositories, tests or existing workflows.
- Arabic RTL throughout the UI.
- No gradients or excessive decoration.
- Do not claim completion unless verification was actually run.

## Completion report
Summarize changed files, tests, compile status, remaining limitations, and the final UI areas reviewed.
