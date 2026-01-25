# ChatGPT ToDo App

A ToDo app that runs inside ChatGPT, built with OpenAI Apps SDK and MCP (Model Context Protocol) in Python.

## Purpose

Learning project to understand:
- OpenAI Apps SDK patterns
- MCP server architecture
- Tool definitions and state management
- Conversational UI design

## Features

- Add, list, complete, and delete tasks conversationally
- AI-assisted task decomposition into subtasks
- Local persistence with SQLite
- Inline card UI components

## Project Structure

```
chatgpt-todo-app/
├── docs/
│   ├── prompts/          # Prompts used to generate docs
│   ├── ADRs/             # Architectural Decision Records
│   ├── PRD.md            # Product Requirements Document
│   └── TDD.md            # Technical Design Document
├── src/                  # Source code
├── tests/                # Tests
├── CLAUDE.md             # AI context for Claude Code
└── README.md
```

## Documentation

| Document | Description |
|----------|-------------|
| [PRD](docs/PRD.md) | Product requirements and user stories |
| TDD | Technical design (coming soon) |

## Tech Stack

- Python 3.10+
- OpenAI Apps SDK
- MCP (Model Context Protocol)
- SQLite

## Status

🚧 In development - Week 1 of 4

## License

MIT
