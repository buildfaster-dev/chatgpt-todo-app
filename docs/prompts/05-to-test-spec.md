Act as a senior QA Engineer / SDET. Generate a practical test specification based on the following documents.

IMPORTANT: This is a new conversation. Do not use any context from previous chats. Only use the information explicitly provided in this prompt.

## PRD
[PASTE PRD HERE]

## TDD
[PASTE TDD HERE]

## Project Scope
- Type: [Learning project | MVP | Production]
- Timeline: [INDICATE]
- Team size: [INDICATE]

## Instructions

Generate a CONCISE test specification. Focus on practical tests that can be implemented within the project timeline. Avoid over-engineering.

### 1. Test Strategy Overview
- Testing pyramid (unit > integration > e2e)
- Coverage target (single number, e.g., "70%")
- Tools and frameworks (only essential ones)

### 2. Unit Tests Specification
For each main component, list 3-5 critical test cases:
- 1-2 happy path
- 1-2 error cases
- 1 edge case (if relevant)

Format:
| ID | Description | Input | Expected |
|----|-------------|-------|----------|

### 3. Integration Tests Specification
List 5-10 integration tests covering the main flows. Focus on happy paths.

### 4. Fixtures
Simple fixtures needed for tests. No factory libraries for learning projects.

### 5. Test Cases per User Story
For each P0 user story: 2-3 test cases that verify acceptance criteria.

## Output Guidelines
- Keep document under 300 lines
- Prefer tables over prose
- Include 1-2 code examples for reference
- Skip E2E tests for learning projects
- Skip CI/CD configuration
