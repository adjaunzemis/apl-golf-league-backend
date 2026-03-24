# AGENTS.md (Backend)

## Purpose
Defines architecture, conventions, and expectations for backend development.

---

## 🏗️ Architecture

- Framework: FastAPI (async-first)
- ORM: SQLModel
- Database: PostgreSQL
- Pattern: Service / Repository pattern

---

## 🧩 API Design

- Use RESTful conventions
- Keep endpoints thin (no business logic)
- Use Pydantic/SQLModel schemas for all inputs/outputs
- Always use explicit typing

### Endpoints
- Validate inputs at boundary
- Return consistent response models
- Use proper HTTP status codes

---

## 🧠 Services Layer

- Contains ALL business logic
- Must be independent of FastAPI
- Must NOT directly query DB (use repositories)
- Should be easily unit testable

---

## 🗄️ Repository Layer

- Encapsulates all database access
- No business logic
- Returns domain models, not raw queries
- Keep queries simple and readable

---

## 🧱 Models

- Use SQLModel for persistence
- Separate API schemas when necessary
- Avoid leaking DB models into API responses

---

## 🧪 Testing

- Use pytest
- Required for:
  - new endpoints
  - service logic

### Coverage expectations:
- happy path
- edge cases
- invalid inputs

---

## 🔒 Data Integrity

- Never trust frontend input
- Validate in services layer
- Fail loudly with clear error messages

---

## ⚙️ Async & Performance

- Prefer async endpoints
- Avoid blocking calls
- Use dependency injection for DB sessions

---

## 🔄 Migrations

- Ensure schema changes are handled properly
- Keep migrations small and reversible

---

## 🔄 Git

- Small, focused commits
- Conventional commit messages:
  - feat:
  - fix:
  - refactor:
  - test:

---

## ⚠️ Constraints

- Do NOT break existing API contracts
- Do NOT mix business logic into endpoints
- Avoid large refactors unless required

---

## 🎯 Definition of Done

- Feature implemented
- Tests added and passing
- Code follows architecture
- Clear commit message
