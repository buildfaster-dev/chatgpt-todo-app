# C4 Model Diagrams: ChatGPT ToDo App

## Overview

This document contains C4 Model diagrams for the ChatGPT ToDo App with AI Task Decomposition. The system implements a ChatGPT-integrated task management application using the OpenAI Apps SDK with MCP (Model Context Protocol).

---

## C1 - System Context Diagram

This diagram shows the ToDo App system in context, illustrating how it interacts with users and external systems.

```mermaid
flowchart TB
    classDef person fill:#08427B,stroke:#073B6F,color:#FFFFFF
    classDef system fill:#1168BD,stroke:#0E5AA7,color:#FFFFFF
    classDef external fill:#999999,stroke:#8A8A8A,color:#FFFFFF
    classDef legendBox fill:#FFFFFF,stroke:#CCCCCC,color:#000000

    subgraph Legend[" "]
        direction LR
        L1["👤 Person"]
        L2["🔷 Software System"]
        L3["⬜ External System"]
    end

    User["👤 User
    ―――――――――――
    Manages tasks through
    natural conversation"]
    
    TodoSystem["ChatGPT ToDo App
    ―――――――――――――――――
    MCP server that enables
    task management via
    conversational AI
    ―――――――――――――――――
    Software System"]
    
    ChatGPT["ChatGPT
    ―――――――――――
    Conversational AI that
    invokes MCP tools on
    behalf of users
    ―――――――――――
    External System"]

    User -->|"Sends natural language
    requests via chat"| ChatGPT
    ChatGPT -->|"Invokes tools via
    MCP Protocol
    [Streamable HTTP]"| TodoSystem
    ChatGPT -->|"Returns task confirmations
    and inline UI cards"| User

    class User person
    class TodoSystem system
    class ChatGPT external
    class L1 person
    class L2 system
    class L3 external
    class Legend legendBox
```

**Description:** The System Context diagram shows that users interact with the ChatGPT ToDo App indirectly through ChatGPT. Users send natural language requests (like "Add task: Buy groceries") to ChatGPT, which translates these into MCP tool calls. The ToDo App processes these requests and returns both structured data (for ChatGPT's reasoning) and HTML inline cards (for user display).

**Design Decision:** ChatGPT acts as the primary interface, meaning users never interact with the ToDo App directly. This enables a fully conversational UX where task management feels like a natural chat.

---

## C2 - Container Diagram

This diagram shows the high-level technical building blocks of the system and how they communicate.

```mermaid
flowchart TB
    classDef person fill:#08427B,stroke:#073B6F,color:#FFFFFF
    classDef external fill:#999999,stroke:#8A8A8A,color:#FFFFFF
    classDef container fill:#438DD5,stroke:#3A7BBE,color:#FFFFFF
    classDef database fill:#438DD5,stroke:#3A7BBE,color:#FFFFFF
    classDef legendBox fill:#FFFFFF,stroke:#CCCCCC,color:#000000

    subgraph Legend[" "]
        direction LR
        L1["👤 Person"]
        L2["📦 Container"]
        L3["🗄️ Database"]
        L4["⬜ External"]
    end

    User["👤 User"]
    
    subgraph ExtBoundary["External Systems"]
        WebApp["ChatGPT Web/Mobile
        ―――――――――――
        User interface for
        chat interactions
        ―――――――――――
        Web Application"]
    end

    subgraph SystemBoundary["ChatGPT ToDo App"]
        MCPServer["MCP Server
        ―――――――――――――
        Handles MCP protocol,
        registers tools, processes
        tool invocations
        ―――――――――――――
        Python / uvicorn / MCP SDK"]
        
        SQLite[("SQLite Database
        ―――――――――――
        Stores tasks with
        parent-child hierarchy
        ―――――――――――
        SQLite / tasks.db")]
    end

    User -->|"Uses"| WebApp
    WebApp -->|"MCP Protocol
    [Streamable HTTP]"| MCPServer
    MCPServer -->|"Reads/Writes
    [aiosqlite]"| SQLite
    MCPServer -->|"JSON-RPC response
    + HTML cards"| WebApp

    class User person
    class WebApp external
    class MCPServer container
    class SQLite database
    class L1 person
    class L2 container
    class L3 database
    class L4 external
    class Legend legendBox
```

**Description:** The Container diagram reveals two main containers within the ToDo App boundary: the MCP Server (Python application) and SQLite Database. The MCP Server receives tool invocations from ChatGPT via Streamable HTTP transport, processes them asynchronously, and persists data to SQLite using the aiosqlite library for non-blocking database operations.

**Key Technical Choices:**
- **Streamable HTTP:** Chosen over stdio/SSE as recommended by Apps SDK; enables bidirectional streaming
- **SQLite:** Zero-configuration persistence ideal for single-user learning project
- **aiosqlite:** Enables async database operations without blocking the event loop

---

## C3 - Component Diagram: MCP Server

This diagram zooms into the MCP Server container to show its internal components and their responsibilities.

```mermaid
flowchart TB
    classDef external fill:#999999,stroke:#8A8A8A,color:#FFFFFF
    classDef component fill:#85BBF0,stroke:#78A8D8,color:#000000
    classDef database fill:#438DD5,stroke:#3A7BBE,color:#FFFFFF
    classDef legendBox fill:#FFFFFF,stroke:#CCCCCC,color:#000000

    subgraph Legend[" "]
        direction LR
        L1["🧩 Component"]
        L2["🗄️ Database"]
        L3["⬜ External"]
    end

    ChatGPT["ChatGPT Client
    ―――――――――――
    External System"]

    subgraph MCPServer["MCP Server Container"]
        direction TB
        
        ServerEntry["Server Entry Point
        ―――――――――――――――
        server.py
        ―――――――――――――――
        Initializes MCP server,
        registers tools, manages
        HTTP transport layer
        ―――――――――――――――
        mcp SDK / uvicorn"]
        
        ToolsLayer["Tools Layer
        ―――――――――――――――
        task_tools.py
        ―――――――――――――――
        Defines tool schemas,
        implements handlers,
        coordinates responses
        ―――――――――――――――
        Pydantic"]
        
        DBLayer["Database Layer
        ―――――――――――――――
        models.py
        ―――――――――――――――
        TaskRepository with CRUD,
        connection management,
        typed query results
        ―――――――――――――――
        aiosqlite"]
        
        UIComponents["UI Components
        ―――――――――――――――
        components.py
        ―――――――――――――――
        Generates HTML for
        inline cards per
        Apps SDK guidelines
        ―――――――――――――――
        Pure Functions"]
    end

    SQLite[("SQLite
    ―――――――――
    tasks.db")]

    ChatGPT -->|"POST /mcp
    list_tools, call_tool"| ServerEntry
    ServerEntry -->|"Routes tool calls"| ToolsLayer
    ToolsLayer -->|"CRUD operations"| DBLayer
    ToolsLayer -->|"Request card HTML"| UIComponents
    DBLayer -->|"Parameterized SQL"| SQLite
    ServerEntry -->|"JSON-RPC + UI"| ChatGPT

    class ChatGPT external
    class ServerEntry component
    class ToolsLayer component
    class DBLayer component
    class UIComponents component
    class SQLite database
    class L1 component
    class L2 database
    class L3 external
    class Legend legendBox
```

**Description:** The Component diagram shows four distinct components within the MCP Server, following a layered architecture pattern. The Server Entry Point handles protocol concerns, the Tools Layer implements business logic for the five MCP tools (add_task, list_tasks, complete_task, delete_task, decompose_task), the Database Layer encapsulates SQLite operations, and UI Components generate HTML cards.

**Component Responsibilities:**

| Component | File | Primary Responsibility |
|-----------|------|----------------------|
| Server Entry Point | server.py | MCP protocol handling, tool registration, HTTP transport |
| Tools Layer | task_tools.py | Tool schemas (Pydantic), business logic, input validation |
| Database Layer | models.py | TaskRepository with async CRUD, connection pooling |
| UI Components | components.py | HTML generation for inline cards (pure functions) |

---

## C3 - Component Diagram: Tools Layer Detail

This diagram provides additional detail on the Tools Layer, showing the individual MCP tools and their interactions.

```mermaid
flowchart TB
    classDef addTool fill:#4CAF50,stroke:#388E3C,color:#FFFFFF
    classDef listTool fill:#2196F3,stroke:#1976D2,color:#FFFFFF
    classDef completeTool fill:#FF9800,stroke:#F57C00,color:#FFFFFF
    classDef deleteTool fill:#f44336,stroke:#D32F2F,color:#FFFFFF
    classDef decomposeTool fill:#9C27B0,stroke:#7B1FA2,color:#FFFFFF
    classDef schema fill:#ECEFF1,stroke:#B0BEC5,color:#000000
    classDef layer fill:#85BBF0,stroke:#78A8D8,color:#000000
    classDef legendBox fill:#FFFFFF,stroke:#CCCCCC,color:#000000

    subgraph Legend[" "]
        direction LR
        LA["➕ add"]
        LL["📋 list"]
        LC["✅ complete"]
        LD["🗑️ delete"]
        LX["🔀 decompose"]
    end

    subgraph ToolsLayer["Tools Layer - task_tools.py"]
        direction TB
        
        AddTask["add_task
        ―――――――――
        Creates new task
        or subtask
        ―――――――――
        title: str
        parent_id?: int"]
        
        ListTasks["list_tasks
        ―――――――――
        Retrieves tasks
        with filtering
        ―――――――――
        filter?: enum
        parent_id?: int"]
        
        CompleteTask["complete_task
        ―――――――――
        Marks task as
        completed
        ―――――――――
        task_id: int"]
        
        DeleteTask["delete_task
        ―――――――――
        Removes task +
        cascades subtasks
        ―――――――――
        task_id: int"]
        
        DecomposeTask["decompose_task
        ―――――――――
        Creates subtasks
        from AI-generated
        titles
        ―――――――――
        task_id: int
        subtask_titles: str[]"]
    end

    subgraph Schemas["Pydantic Schemas - schemas.py"]
        TaskBase["TaskBase
        ―――――――
        title: str"]
        TaskCreate["TaskCreate
        ―――――――
        extends TaskBase
        parent_id?: int"]
        Task["Task
        ―――――――
        id: int
        completed: bool
        created_at: datetime
        subtasks: Task[]"]
    end

    DBLayer["Database Layer
    models.py"]
    UIComp["UI Components
    components.py"]

    AddTask --> DBLayer
    ListTasks --> DBLayer
    CompleteTask --> DBLayer
    DeleteTask --> DBLayer
    DecomposeTask --> DBLayer

    AddTask --> UIComp
    ListTasks --> UIComp
    CompleteTask --> UIComp
    DeleteTask --> UIComp
    DecomposeTask --> UIComp

    Schemas -.->|"validates"| ToolsLayer

    class AddTask addTool
    class ListTasks listTool
    class CompleteTask completeTool
    class DeleteTask deleteTool
    class DecomposeTask decomposeTool
    class TaskBase schema
    class TaskCreate schema
    class Task schema
    class DBLayer layer
    class UIComp layer
    class LA addTool
    class LL listTool
    class LC completeTool
    class LD deleteTool
    class LX decomposeTool
    class Legend legendBox
```

**Description:** This detailed view of the Tools Layer shows the five MCP tools exposed to ChatGPT. Each tool has a defined input schema (validated by Pydantic), interacts with both the Database Layer for persistence and UI Components for generating response cards. The decompose_task tool is unique in that ChatGPT generates the subtask titles externally—the tool only persists them.

**Design Decision:** Task decomposition leverages ChatGPT's reasoning rather than implementing AI in the MCP server. This keeps the server simple and takes advantage of the existing ChatGPT session context.

---

## Data Flow Diagram

This sequence diagram shows the complete flow for adding and decomposing a task.

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant C as 🤖 ChatGPT
    participant S as 🐍 MCP Server
    participant D as 💾 SQLite

    rect rgb(232, 245, 233)
        Note over U,D: Task Creation Flow
        U->>C: "Add task: Plan birthday party"
        C->>S: call_tool(add_task, {title: "Plan birthday party"})
        S->>D: INSERT INTO tasks (title) VALUES (?)
        D-->>S: {id: 1, title: "Plan birthday party", ...}
        S-->>C: {task: {...}, ui: "<inline-card>..."}
        C-->>U: Display task confirmation card
    end

    rect rgb(227, 242, 253)
        Note over U,D: Task Decomposition Flow
        U->>C: "Break this down into subtasks"
        Note right of C: ChatGPT reasons about<br/>appropriate subtasks
        C->>S: call_tool(decompose_task, {<br/>  task_id: 1,<br/>  subtask_titles: [<br/>    "Choose venue",<br/>    "Create guest list",<br/>    "Order cake"<br/>  ]<br/>})
        S->>D: INSERT INTO tasks (title, parent_id)<br/>VALUES (?, 1) × 3
        D-->>S: [{id: 2, ...}, {id: 3, ...}, {id: 4, ...}]
        S-->>C: {parent_task: {...}, subtasks: [...], ui: "..."}
        C-->>U: Display hierarchy card with subtasks
    end
```

**Description:** This sequence diagram illustrates two key flows: basic task creation and AI-assisted decomposition. Note that in the decomposition flow, ChatGPT generates the subtask titles based on its understanding of the parent task—the MCP server simply persists whatever titles ChatGPT provides.

---

## Entity Relationship Diagram

```mermaid
erDiagram
    TASK {
        int id PK "Auto-increment primary key"
        string title "Task description, 1-500 chars"
        boolean completed "Default: false"
        timestamp created_at "Auto-set on creation"
        int parent_id FK "Self-reference, nullable"
    }
    
    TASK ||--o{ TASK : "has subtasks"
```

**Description:** The Task entity uses a self-referential relationship to support hierarchical subtasks. The `parent_id` foreign key references `tasks.id`, with `ON DELETE CASCADE` ensuring subtasks are automatically removed when their parent is deleted.

---

## Summary

| Diagram Level | Purpose | Key Insights |
|--------------|---------|--------------|
| **C1 - Context** | System boundaries and actors | Users interact indirectly via ChatGPT |
| **C2 - Container** | Technical building blocks | Python MCP Server + SQLite, Streamable HTTP |
| **C3 - Component** | Internal structure | Layered architecture with 4 components |
| **C3 - Tools Detail** | Tool breakdown | 5 MCP tools with Pydantic validation |

---

## Color Reference

| Element Type | Color | Hex Code | Usage |
|-------------|-------|----------|-------|
| Person/User | Dark Blue | `#08427B` | Human actors |
| Main System | Blue | `#1168BD` | The system being documented |
| External System | Gray | `#999999` | Systems outside scope |
| Container | Light Blue | `#438DD5` | Deployable units |
| Component | Very Light Blue | `#85BBF0` | Internal modules |
| Database | Light Blue (cylinder) | `#438DD5` | Data stores |

---

## Architecture Characteristics

- **Simplicity:** Layered architecture ideal for learning
- **Async-first:** uvicorn + aiosqlite for non-blocking I/O
- **Type-safe:** Pydantic schemas ensure validation and generate JSON Schema
- **Conversational UI:** Inline cards render within chat flow
- **Single Responsibility:** Each component has clear, focused duties
