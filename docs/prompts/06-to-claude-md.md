Act as an expert in AI Native Development and Claude Code. Generate an optimized CLAUDE.md file to serve as the project's main context.

IMPORTANT: This is a new conversation. Do not use any context from previous chats. Only use the information explicitly provided in this prompt.

## Project Documentation

### PRD
[PASTE PRD HERE]

### TDD
[PASTE TDD HERE]

### Test Spec (optional)
[PASTE TEST SPEC HERE OR REMOVE THIS SECTION]

### API Spec (optional, if separate from TDD)
[PASTE API SPEC HERE OR REMOVE THIS SECTION]

## Instructions

The CLAUDE.md should be **concise but complete**. Claude Code will read it at the start of each session to understand the project.

### Required Structure

#### 1. Project Overview (3-5 lines)
- What the project is
- Main stack
- Current status (MVP, in development, etc.)

#### 2. Architecture Summary
- Simple ASCII diagram of components
- Main data flow
- External services

#### 3. Directory Structure
- Directory tree with description of each folder
- Key files and their purpose

#### 4. Key Files
- List of most important files
- What each contains
- When to modify them

#### 5. Development Commands
- How to run the project
- How to run tests
- How to lint/format

#### 6. Code Conventions
- Naming conventions
- Patterns used
- Things to avoid

#### 7. Current Tasks / TODOs
- What's in progress
- Next steps
- Known blockers

#### 8. Common Patterns
- Code examples for common tasks
- How to add a new command
- How to add a new test

### Writing Principles

1. **Brevity:** Claude has context limits. Every word must add value.
2. **Actionable:** Information that helps write code, not theory.
3. **Up-to-date:** Must reflect the actual state of the code.
4. **Examples > Explanations:** Showing code is better than describing it.

### Output Format
- Markdown
- Maximum 500 lines (ideal: 200-300)
- Inline code for short examples
- File references for long examples
