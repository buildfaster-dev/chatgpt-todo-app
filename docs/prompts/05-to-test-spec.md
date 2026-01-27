# Prompt: PRD + TDD → Test Specification

## When to Use
When you have PRD and TDD defined and need to generate test specifications before implementing (Test-Driven approach).

## Required Input
- PRD with user stories and acceptance criteria
- TDD with technical design
- API Spec (if exists)

---

## Prompt

```markdown
Act as a senior QA Engineer / SDET. Generate a comprehensive test specification based on the following documents.

IMPORTANT: This is a new conversation. Do not use any context from previous chats. Only use the information explicitly provided in this prompt.

## PRD
[PASTE PRD HERE]

## TDD
[PASTE TDD HERE]

## API Spec (optional)
[PASTE API SPEC HERE]

## Instructions

### 1. Test Strategy Overview
- Types of tests to implement
- Prioritization (what to test first)
- Coverage targets
- Tools and frameworks

### 2. Unit Tests Specification
For each component/module:
- Function/method to test
- Scenarios (happy path, edge cases, errors)
- Input → Expected output
- Required mocks

Format per test:
| ID | Description | Input | Expected | Mocks |
|----|-------------|-------|----------|-------|

### 3. Integration Tests Specification
For each integration flow:
- Components involved
- Required setup
- End-to-end scenario
- Assertions

### 4. Test Data Requirements
- Required fixtures
- Test data
- Database states

### 5. Mock Specifications
For each external service:
- What to mock
- Mock responses (success and error)
- When to use mock vs real

### 6. Test Cases per User Story
For each PRD user story:
- Test cases that verify acceptance criteria
- User Story → Test IDs mapping

## Output Format
- Structured markdown
- Tables for test cases
- Example test code where it helps
- Executable checklist
```

---

## Usage Example

**Input:**
```
## PRD
AI-Powered ToDo App

User Stories: US-01 to US-05 (CRUD + AI decompose)
Acceptance criteria defined for each story
[... rest of PRD content ...]

## TDD
Components: TaskService, AIService, TaskRepository
External: OpenAI API (needs mocking)
Coverage target: 70%
[... rest of TDD content ...]

## API Spec (optional)
CLI commands: add, list, show, complete, delete, decompose
[... or leave empty if not available ...]
```

**How to use:** Copy the Prompt section above, then replace `[PASTE PRD HERE]` with your PRD, `[PASTE TDD HERE]` with your TDD, and optionally `[PASTE API SPEC HERE]` if you have one.

**Expected output:** Test specification with 40+ test cases, fixtures, mock specifications, and user story to test mapping.

---

## Output Files

After executing this prompt:

| File | Location | Content |
|------|----------|---------|
| Test Spec | `docs/test-spec.md` | The generated test specification |
| Prompt used | `docs/prompts/05-to-test-spec.md` | This prompt with your input (without full docs) |

**Note:** In the saved prompt, replace full document content with `[See docs/PRD.md]` and `[See docs/TDD.md]` to avoid duplication.

---

## Tips

1. **Start with happy paths:** Ensure it works before looking for bugs
2. **One test = one thing:** Each test verifies a single behavior
3. **Descriptive names:** `test_create_task_with_valid_title_returns_task_with_id`
4. **Consider maintenance:** Fragile tests are worse than no tests
5. **Own the document:** If the generated spec doesn't match your testing approach, use `prompt-refinement.md` to adjust


