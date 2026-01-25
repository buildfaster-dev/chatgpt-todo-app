Act as a Software Architect specialized in visual documentation. Generate C4 Model diagrams based on the following Technical Design Document.

IMPORTANT: This is a new conversation. Do not use any context from previous chats. Only use the information explicitly provided in this prompt.

## TDD
[PASTE COMPLETE TDD HERE]

## Required Levels
- [x] C1 - System Context
- [x] C2 - Container
- [x] C3 - Component (for: [SPECIFY CONTAINERS])
- [ ] C4 - Code (optional)

## Instructions

### For each level, generate:

#### C1 - System Context Diagram
- Main system in the center
- External actors (users, systems)
- High-level relationships
- Format: Mermaid flowchart

#### C2 - Container Diagram
- System containers (applications, databases, etc.)
- Technology of each container
- Communication between containers
- Format: Mermaid flowchart

#### C3 - Component Diagram
- Components within each specified container
- Responsibilities
- Dependencies between components
- Format: Mermaid flowchart

### C4 Conventions
- Use consistent colors with explicit Mermaid styling:
  - People: #08427B (dark blue), white text
  - Main system: #1168BD (blue), white text
  - External systems: #999999 (gray), white text
  - Containers: #438DD5 (light blue)
  - Components: #85BBF0 (very light blue)
  - Databases: #438DD5 with cylinder shape

**IMPORTANT: Apply styles using classDef and class in Mermaid. Example:**

    flowchart TB
        classDef person fill:#08427B,stroke:#073B6F,color:#FFFFFF
        classDef system fill:#1168BD,stroke:#0E5AA7,color:#FFFFFF
        classDef external fill:#999999,stroke:#8A8A8A,color:#FFFFFF
        classDef container fill:#438DD5,stroke:#3A7BBE,color:#FFFFFF
        classDef component fill:#85BBF0,stroke:#78A8D8,color:#000000
        classDef database fill:#438DD5,stroke:#3A7BBE,color:#FFFFFF

        User[User]
        System[My System]
        External[External System]
        
        class User person
        class System system
        class External external

**Legend must be visually distinguishable** - each element type must look different in the rendered diagram.

### For each diagram include:
1. Descriptive title
2. Legend if there are many elements
3. 2-3 line text description explaining the diagram

## Output Format
- Diagrams in Mermaid syntax
- Text description per diagram
- Notes on representation decisions
