Act as a senior Product Manager. Transform the following idea into a structured PRD (Product Requirements Document).
IMPORTANT: This is a new conversation. Do not use any context from previous chats. Only use the information explicitly provided in this prompt.
## Idea
A ToDo App that runs inside ChatGPT as a custom app, built using OpenAI's Apps SDK with MCP (Model Context Protocol) in Python.
The app allows users to manage tasks directly within ChatGPT conversations. Users can add tasks, list them, mark them as complete, and ask ChatGPT to help decompose complex tasks into smaller subtasks.
## Additional Context
- Target user: Developers learning to build ChatGPT apps with the OpenAI Apps SDK
- Preferred tech stack: Python, OpenAI Apps SDK, MCP Server, SQLite for local persistence
- Estimated timeline: 4 weeks
- Constraints: 
  - Learning project, not production
  - Must run as a ChatGPT app (not standalone CLI)
  - Follow OpenAI's App Developer Guidelines
  - Use MCP server architecture as per Apps SDK documentation
## Reference Documentation
- Apps SDK: https://developers.openai.com/apps-sdk/
- MCP Server: https://developers.openai.com/apps-sdk/concepts/mcp-server
- Design Guidelines: https://developers.openai.com/apps-sdk/concepts/design-guidelines
## Instructions
Generate a PRD with the following sections:
### 1. Overview
- Problem Statement: The specific problem we're solving
- Proposed Solution: High-level description of the solution
- Goals & Success Metrics: Measurable success metrics
### 2. User Personas
- Primary persona with characteristics, pain points, and goals
- Main jobs-to-be-done (JTBD)
### 3. User Stories
Format: "As a [persona], I want [action] so that [benefit]"
- Include acceptance criteria for each story
- Prioritize with MoSCoW (Must/Should/Could/Won't)
### 4. Functional Requirements
- Core features (MVP)
- Future features (post-MVP)
- Explicit out of scope
### 5. Non-Functional Requirements
- Performance expectations
- Security requirements
- Scalability considerations
### 6. Assumptions & Dependencies
- Assumptions we're making
- External dependencies
### 7. Open Questions
- Unresolved questions that need decision
## Output Format
- Structured markdown
- User stories in table format
- Priorities clearly marked
