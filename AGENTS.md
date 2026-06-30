# Global Soil Explorer

## Mission
Build a modern, open-source Web GIS platform that makes global soil datasets understandable, explorable, and accessible.

## Project Philosophy
- **User-Centric**: Solve real user problems first, keeping the application focused on the needs of scientists, planners, and field workers.
- **Data-First Design**: Design the architecture around the structures, scales, and dimensionalities of the underlying datasets.
- **Reproducibility**: Ensure data preprocessing, database generation, and deployment pipelines are fully repeatable and verifiable.
- **Open Standards**: Use open GIS, database, and metadata standards to facilitate interoperability and community collaboration.
- **Dataset-Agnostic Architecture**: Build application interfaces and database layer interfaces that can accommodate diverse datasets beyond the current scope.
- **Maintainability**: Write clean, self-documenting code with clear boundaries to ensure long-term ease of maintenance.

## Current Scope
- Dataset: HWSD v2.0
- Stage: Reverse engineering and platform foundation
- Do not implement features beyond the current task.

## Scope Control
- **Sprint Focus**: Remain strictly focused on the current sprint tasks and do not implement out-of-scope features.
- **No Speculative Coding**: Avoid implementing speculative logic, APIs, or data models for features that are not currently required.
- **Explicit Approval**: Always wait for explicit stakeholder/user approval before implementing new roadmap items or architectural changes.

## Tech Stack
- Backend: FastAPI (Python)
- Frontend: React + TypeScript
- Maps: MapLibre GL JS
- Database: PostgreSQL/PostGIS (later)
- Package Manager: uv
- Version Control: Git

## Engineering Principles
- Keep code simple.
- Prefer readability over cleverness.
- Prefer the simplest solution that satisfies the current requirements.
- Do not optimize prematurely.
- Avoid introducing abstraction until there is a demonstrated need.
- Avoid duplication.
- Use type hints.
- Add docstrings for public functions.
- Write modular code.
- Never modify files inside data/raw/.

## Coding Rules
- Don't add dependencies unless requested.
- Don't invent soil attributes or scientific data.
- Don't change repository structure.
- Ask before making architectural decisions.

## Decision Making Rules
- Before proposing an implementation, verify whether a project decision already exists in `docs/decisions/` or `AGENTS.md`.
- **Trade-Off Analysis**: When multiple solutions exist, present an explicit comparison of pros, cons, and performance/complexity trade-offs.
- **Explicit Assumptions**: Clearly identify and list assumptions made during research or system design.
- **Scientific & Technical Citations**: Provide authoritative citations for external technical or scientific claims when appropriate.
- **No Inventions**: Never invent architecture, technologies, datasets, or workflows that have not been explicitly approved.
- **Clarify Uncertainties**: If information is missing, ask the user for clarification instead of making assumptions.
- **Plan Before Action**: Prefer detailed planning and design reviews before starting implementation.
- **Incremental Progress**: Keep changes small, reviewable, and reversible.
- **Respect Repository Boundaries**: Respect the repository structure and never modify files inside `data/raw/`.
- **Docs First**: For non-trivial features, establish or update the relevant documentation and Architecture Decision Records (ADRs) before implementation. Small bug fixes and routine refactoring do not require new ADRs.

## Development Workflow
Follow the structured engineering lifecycle for every development task:
`Understand` → `Research` → `Plan` → `Review` → `Implement` → `Test` → `Document` → `Commit`.
- **Understand**: Comprehend the problem statement, user requirements, and constraints.
- **Research**: Investigate the codebase, database schemas, and academic literature if necessary.
- **Plan**: Design the solution and present it clearly to the user.
- **Review**: Align and get user confirmation on the proposed design.
- **Implement**: Write simple, modular, and type-hinted code.
- **Test**: Write and run unit, integration, and UI tests to prove correctness.
- **Document**: Update user manuals, APIs, system diagrams, or ADRs.
- **Commit**: Commit code incrementally with clean, structured commits.

## Output Style
- Explain the plan before changing code.
- Keep commits small.
- Update documentation when necessary.
