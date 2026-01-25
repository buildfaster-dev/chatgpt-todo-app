Modify ONLY the specified section of this document. Keep everything else EXACTLY as is, including all other sections, formatting, tables, and content.

IMPORTANT: This is a new conversation. Do not use any context from previous chats. Only use the information explicitly provided in this prompt.

## Document Type
PRD

## Current Document
# Product Requirements Document (PRD)

## ChatGPT ToDo App with AI Task Decomposition

|**Document Version**|1.0|
|---|---|
|**Last Updated**|January 2026|
|**Project Timeline**|4 Weeks|
|**Status**|Draft|
|**Project Type**|Learning Project|

---

## 1. Overview

### 1.1 Problem Statement

Developers learning to build ChatGPT apps with the OpenAI Apps SDK lack practical, well-documented example projects that demonstrate core SDK patterns. Existing documentation provides conceptual guidance but doesn't offer a complete, end-to-end learning project that developers can build incrementally while learning MCP server architecture, tool definitions, state management, and conversational UI patterns.

Additionally, task management within conversational interfaces presents a unique UX challenge: users want to manage tasks without leaving their conversation flow, and complex tasks often benefit from AI-assisted decomposition—something traditional todo apps cannot provide.

### 1.2 Proposed Solution

Build a ChatGPT-integrated ToDo application using the OpenAI Apps SDK with MCP (Model Context Protocol) in Python. The app enables users to:

- **Manage tasks conversationally**: Add, list, complete, and delete tasks directly within ChatGPT
- **Leverage AI for task decomposition**: Ask ChatGPT to break down complex tasks into actionable subtasks
- **Persist data locally**: Store tasks in SQLite for session persistence
- **Learn SDK patterns**: Serve as a reference implementation for developers learning the Apps SDK

The solution follows the MCP server architecture, implementing tools that ChatGPT can invoke, with inline card components for task visualization.

### 1.3 Goals & Success Metrics

|**Goal**|**Success Metric**|**Target**|
|---|---|---|
|Complete SDK learning objectives|All core MCP patterns implemented|100% coverage of: tools, state management, UI components|
|Functional task management|Core CRUD operations working|All 4 operations (create, read, update, delete) functional|
|AI-assisted decomposition|Task breakdown feature works|Complex tasks decomposable into 3-10 subtasks|
|Code quality|Clean, documented codebase|Each module documented; passes linting|
|Learning documentation|README with setup instructions|New developer can run app in <15 minutes|

---

## 2. User Personas

### 2.1 Primary Persona: Learning Developer

|**Attribute**|**Description**|
|---|---|
|**Name**|Alex Chen|
|**Role**|Junior/Mid-level Python Developer|
|**Experience**|2-4 years Python; familiar with REST APIs; new to ChatGPT app development|
|**Goals**|Learn OpenAI Apps SDK; build portfolio project; understand MCP architecture|
|**Frustrations**|Documentation is theoretical; lacks complete working examples; unclear how pieces connect|
|**Technical Environment**|macOS/Linux; VS Code; Python 3.10+; SQLite experience|

**Characteristics:**

- Learns best by building and modifying working code
- Values clear code comments and documentation
- Wants to understand "why" not just "how"
- Plans to build more complex ChatGPT apps after mastering basics

**Pain Points:**

- SDK quickstart is too minimal for real-world patterns
- Unclear how to structure a multi-tool MCP server
- Uncertain about best practices for state management
- Doesn't know how to design conversational UX for apps

### 2.2 Secondary Persona: End User

|**Attribute**|**Description**|
|---|---|
|**Name**|Jordan Lee|
|**Role**|Knowledge Worker / ChatGPT Power User|
|**Goals**|Manage tasks without leaving ChatGPT; get AI help breaking down complex work|
|**Context**|Already uses ChatGPT daily; wants integrated productivity tools|

### 2.3 Jobs To Be Done (JTBD)

|**JTBD**|**Persona**|**Priority**|
|---|---|---|
|When I'm learning a new SDK, I want a complete working example so I can understand how all the pieces fit together|Learning Developer|Primary|
|When I have a complex task, I want AI to help me break it into smaller steps so I can make progress without feeling overwhelmed|End User|Primary|
|When I'm in a ChatGPT conversation, I want to quickly capture tasks so I don't lose ideas while chatting|End User|Secondary|
|When I want to build my own ChatGPT app, I want reference code I can adapt so I don't start from scratch|Learning Developer|Secondary|

---

## 3. User Stories

### 3.1 Must Have (P0)

|**ID**|**User Story**|**Acceptance Criteria**|**Priority**|
|---|---|---|---|
|US-01|As a user, I want to add a task by typing naturally in ChatGPT so that task capture feels conversational|1. User can say "Add task: Buy groceries" or "Remind me to call Mom"<br>2. Task is created with title extracted from message<br>3. Confirmation shown via inline card<br>4. Task persists in SQLite|**Must**|
|US-02|As a user, I want to view all my tasks so that I can see what I need to do|1. User can say "Show my tasks" or "What's on my list?"<br>2. Tasks displayed in inline card/carousel format<br>3. Shows task title and completion status<br>4. Empty state handled gracefully|**Must**|
|US-03|As a user, I want to mark a task as complete so that I can track my progress|1. User can say "Complete task 1" or "Mark 'Buy groceries' as done"<br>2. Task status updates to complete<br>3. Visual confirmation shown<br>4. Database updated|**Must**|
|US-04|As a user, I want to delete a task so that I can remove items I no longer need|1. User can say "Delete task 2" or "Remove 'Buy groceries'"<br>2. Task removed from database<br>3. Confirmation shown<br>4. Task list updates|**Must**|
|US-05|As a developer, I want the MCP server to expose well-defined tools so that ChatGPT can invoke task operations|1. Tools registered: `add_task`, `list_tasks`, `complete_task`, `delete_task`<br>2. Each tool has JSON Schema for inputs/outputs<br>3. Tool metadata includes descriptions for model discovery<br>4. Server responds to MCP `list_tools` and `call_tool`|**Must**|
|US-06|As a developer, I want tasks stored in SQLite so that data persists across sessions|1. SQLite database created on first run<br>2. Schema includes: id, title, completed, created_at, parent_id<br>3. CRUD operations work correctly<br>4. Database location configurable|**Must**|

### 3.2 Should Have (P1)

|**ID**|**User Story**|**Acceptance Criteria**|**Priority**|
|---|---|---|---|
|US-07|As a user, I want ChatGPT to decompose a complex task into subtasks so that I can tackle it step by step|1. User can say "Break down 'Plan birthday party' into subtasks"<br>2. ChatGPT generates 3-10 contextual subtasks<br>3. Subtasks saved with parent_id reference<br>4. Subtasks displayed hierarchically|**Should**|
|US-08|As a user, I want to see tasks displayed as inline cards so that the UI feels native to ChatGPT|1. Task list renders as inline card component<br>2. Individual tasks show title, status, actions<br>3. Cards follow Apps SDK UI guidelines<br>4. Responsive on web and mobile|**Should**|
|US-09|As a developer, I want clear code documentation so that I can understand each component's purpose|1. README with architecture overview<br>2. Inline comments explaining SDK patterns<br>3. Docstrings on all public functions<br>4. Example commands documented|**Should**|
|US-10|As a user, I want to filter tasks by status so that I can focus on incomplete items|1. User can say "Show incomplete tasks" or "Show completed tasks"<br>2. Filter applied to list_tasks tool<br>3. Results display filtered subset|**Should**|

### 3.3 Could Have (P2)

|**ID**|**User Story**|**Acceptance Criteria**|**Priority**|
|---|---|---|---|
|US-11|As a user, I want to set due dates on tasks so that I can track deadlines|1. User can add due date when creating task<br>2. Due date displayed in task card<br>3. Database schema supports due_date field|**Could**|
|US-12|As a user, I want to edit a task's title so that I can fix mistakes|1. User can say "Rename task 1 to 'Buy organic groceries'"<br>2. Title updates in database<br>3. Confirmation shown|**Could**|
|US-13|As a developer, I want unit tests for the MCP server so that I can verify functionality|1. Test coverage for all tool handlers<br>2. Database operations tested<br>3. Tests runnable via pytest|**Could**|
|US-14|As a user, I want tasks displayed in a carousel when there are many so that I can scroll through them|1. List view switches to carousel at 5+ tasks<br>2. Carousel follows SDK design guidelines<br>3. Smooth horizontal scrolling|**Could**|

### 3.4 Won't Have (Out of Scope for MVP)

|**ID**|**User Story**|**Reason for Exclusion**|
|---|---|---|
|US-15|As a user, I want to sync tasks across devices|Requires user authentication and cloud storage—beyond learning scope|
|US-16|As a user, I want to share tasks with others|Multi-user functionality adds complexity inappropriate for learning project|
|US-17|As a user, I want recurring tasks|Scheduler complexity beyond MVP; can be added post-learning|
|US-18|As a user, I want push notifications for due dates|Requires notification infrastructure outside ChatGPT|

---

## 4. Functional Requirements

### 4.1 Core Features (MVP)

#### FR-01: MCP Server Implementation

- Implement MCP server using Python SDK (`mcp` package)
- Support Streamable HTTP transport (recommended by Apps SDK)
- Handle `list_tools` requests returning tool metadata
- Handle `call_tool` requests with parameter validation
- Return structured JSON responses with embedded UI resources

#### FR-02: Task Management Tools

|**Tool Name**|**Parameters**|**Returns**|**Description**|
|---|---|---|---|
|`add_task`|`title: string`, `parent_id?: int`|`{id, title, created_at}`|Creates new task or subtask|
|`list_tasks`|`filter?: "all" \| "complete" \| "incomplete"`, `parent_id?: int`|`{tasks: [{id, title, completed, subtasks}]}`|Returns task list with hierarchy|
|`complete_task`|`task_id: int`|`{id, title, completed: true}`|Marks task complete|
|`delete_task`|`task_id: int`|`{deleted: true, id}`|Removes task and subtasks|

#### FR-03: Data Persistence

- SQLite database for local storage
- Schema:
    
    ```sql
    CREATE TABLE tasks (  id INTEGER PRIMARY KEY AUTOINCREMENT,  title TEXT NOT NULL,  completed BOOLEAN DEFAULT FALSE,  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  parent_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE);
    ```
    
- Connection pooling for concurrent requests
- Graceful handling of database errors

#### FR-04: UI Components

- Inline card for single task confirmation
- Inline card/list for task overview
- Task card shows: title, status indicator, action buttons (complete, delete)
- Follow Apps SDK UI guidelines (system colors, typography, spacing)
- Support both light and dark mode

#### FR-05: AI Task Decomposition

- `decompose_task` tool accepts complex task description
- Returns model-generated subtasks (ChatGPT handles generation)
- Subtasks automatically linked to parent via `parent_id`
- Limit: 3-10 subtasks per decomposition

### 4.2 Future Features (Post-MVP)

|**Feature**|**Description**|**Complexity**|
|---|---|---|
|Due dates & reminders|Add temporal tracking to tasks|Medium|
|Priority levels|High/Medium/Low task prioritization|Low|
|Categories/tags|Organize tasks by project or context|Medium|
|Fullscreen view|Expanded task management interface|Medium|
|Task search|Find tasks by keyword|Low|
|Export functionality|Export tasks to markdown/JSON|Low|

### 4.3 Explicit Out of Scope

- User authentication (OAuth flows)
- Multi-user support
- Cloud synchronization
- Push notifications
- Mobile-specific native features
- Production deployment optimization
- Rate limiting / abuse prevention
- Analytics or telemetry

---

## 5. Non-Functional Requirements

### 5.1 Performance

|**Requirement**|**Target**|**Measurement**|
|---|---|---|
|Tool response time|< 500ms for CRUD operations|Time from `call_tool` to response|
|Database query time|< 100ms for list queries|SQLite query execution|
|Startup time|< 3 seconds|Server ready to accept connections|
|Memory footprint|< 100MB during normal operation|Process memory usage|

### 5.2 Security

|**Requirement**|**Implementation**|
|---|---|
|Input validation|Validate all tool parameters against JSON Schema|
|SQL injection prevention|Use parameterized queries exclusively|
|Data isolation|SQLite file permissions restricted to owner|
|No sensitive data logging|Task content not logged at INFO level|

### 5.3 Reliability

|**Requirement**|**Implementation**|
|---|---|
|Graceful error handling|All tools return structured error responses|
|Database integrity|Use transactions for multi-step operations|
|Connection recovery|Auto-reconnect on database connection loss|

### 5.4 Maintainability

|**Requirement**|**Implementation**|
|---|---|
|Code organization|Separate modules: server, tools, database, models|
|Documentation|README, inline comments, docstrings|
|Dependency management|requirements.txt with pinned versions|
|Code style|PEP 8 compliance, black formatting|

### 5.5 Compatibility

|**Requirement**|**Target**|
|---|---|
|Python version|3.10+|
|Operating systems|macOS, Linux, Windows (WSL)|
|ChatGPT clients|Web, iOS, Android (via Apps SDK)|

---

## 6. Technical Architecture

### 6.1 System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        ChatGPT Client                           │
│                    (Web / Mobile App)                           │
└─────────────────────────┬───────────────────────────────────────┘
                          │ MCP Protocol (Streamable HTTP)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MCP Server (Python)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Tools     │  │   State     │  │   UI Components         │  │
│  │  Handler    │  │  Manager    │  │   (HTML Templates)      │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────────────────┬─┘  │
│         │                │                                 │    │
│         └────────────────┼─────────────────────────────────┘    │
│                          ▼                                      │
│                   ┌─────────────┐                                │
│                   │  SQLite DB  │                                │
│                   │  (tasks.db) │                                │
│                   └─────────────┘                                │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Project Structure

```
chatgpt-todo-app/
├── README.md
├── requirements.txt
├── pyproject.toml
├── src/
│   ├── __init__.py
│   ├── server.py          # MCP server entry point
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── task_tools.py  # Tool definitions & handlers
│   │   └── schemas.py     # JSON Schema definitions
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py  # SQLite connection management
│   │   └── models.py      # Task model & queries
│   └── ui/
│       ├── __init__.py
│       └── components.py  # Inline card HTML generators
├── tests/
│   ├── __init__.py
│   ├── test_tools.py
│   └── test_database.py
└── docs/
    └── architecture.md
```

---

## 7. Assumptions & Dependencies

### 7.1 Assumptions

|**Assumption**|**Impact if Invalid**|
|---|---|
|OpenAI Apps SDK remains in preview with current API|May require code updates if SDK changes|
|Python MCP SDK (`mcp` package) is stable|Core server implementation depends on this|
|SQLite is sufficient for single-user local persistence|Would need migration path to PostgreSQL for multi-user|
|Developer has Python 3.10+ installed|Setup instructions assume this|
|ChatGPT app connection works via localhost during development|Testing requires this to function|
|Inline cards are sufficient for MVP UX|May need fullscreen view for complex task lists|

### 7.2 External Dependencies

|**Dependency**|**Version**|**Purpose**|
|---|---|---|
|Python|3.10+|Runtime environment|
|mcp (Python SDK)|Latest|MCP protocol implementation|
|sqlite3|Built-in|Database persistence|
|pydantic|2.x|Data validation & serialization|
|uvicorn|0.27+|ASGI server for HTTP transport|
|pytest|8.x|Testing framework (dev dependency)|

### 7.3 Documentation Dependencies

|**Resource**|**URL**|**Purpose**|
|---|---|---|
|Apps SDK Documentation|https://developers.openai.com/apps-sdk/|Primary reference|
|MCP Specification|https://modelcontextprotocol.io/specification|Protocol details|
|Python MCP SDK|https://github.com/modelcontextprotocol/python-sdk|Implementation reference|
|Apps SDK UI Design System|https://openai.github.io/apps-sdk-ui/|UI component styling|

---

## 8. Open Questions

|**ID**|**Question**|**Owner**|**Status**|**Decision**|
|---|---|---|---|---|
|OQ-01|How should the app handle ChatGPT connection during local development? Does the SDK provide a local testing mode?|Developer|Open|Need to verify with quickstart guide|
|OQ-02|What is the maximum number of tasks that can be displayed in an inline carousel before UX degrades?|Developer|Open|Will test during implementation; likely 8-10|
|OQ-03|Should subtasks be independently completable, or does completing a parent auto-complete children?|Developer|Open|Recommend: independent completion|
|OQ-04|How should the app behave when SQLite file is locked by another process?|Developer|Open|Implement retry logic with exponential backoff|
|OQ-05|Is there a recommended approach for versioning the SQLite schema for future migrations?|Developer|Open|Consider using alembic or manual migrations|
|OQ-06|Should the decompose_task tool allow user to customize the number of subtasks generated?|Developer|Open|Default to 5, allow override via parameter|

---

## 9. Milestones & Timeline

|**Week**|**Milestone**|**Deliverables**|
|---|---|---|
|Week 1|Foundation|MCP server skeleton; SQLite setup; `add_task` & `list_tasks` tools working|
|Week 2|Core CRUD|`complete_task` & `delete_task` tools; basic inline card UI|
|Week 3|AI Features|`decompose_task` tool; subtask hierarchy; improved UI components|
|Week 4|Polish|Documentation; error handling; code cleanup; testing|

---

## 10. Appendix

### A. Glossary

|**Term**|**Definition**|
|---|---|
|MCP|Model Context Protocol—open specification for connecting LLM clients to external tools|
|Apps SDK|OpenAI's framework for building ChatGPT-integrated applications|
|Tool|A function exposed by an MCP server that ChatGPT can invoke|
|Inline Card|A lightweight UI component displayed within the ChatGPT conversation|
|Streamable HTTP|Recommended MCP transport protocol for Apps SDK|

### B. Reference Links

- [OpenAI Apps SDK](https://developers.openai.com/apps-sdk/)
- [MCP Server Concepts](https://developers.openai.com/apps-sdk/concepts/mcp-server)
- [UI Design Guidelines](https://developers.openai.com/apps-sdk/concepts/ui-guidelines)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification)
- [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)

---

_Document prepared for learning purposes. Not intended for production deployment._

## Section to Modify
6.2 Project Structure

## Required Changes

Update to this structure: 
```
chatgpt-todo-app/
├── docs/
│   ├── prompts/
│   │   ├── 01-idea-to-prd.md
│   │   └── 02-prd-to-tdd.md
│   ├── ADRs/
│   │   └── ADR-001-xxx.md
│   ├── PRD.md
│   ├── TDD.md
│   └── C4-diagrams.md
├── src/
│   └── ... (keep existing)
├── tests/
├── CLAUDE.md
├── README.md
├── requirements.txt
└── pyproject.toml
```

## Output
Return the COMPLETE document with ONLY the specified section modified. Do not change anything else.
