Modify ONLY the specified sections of this document. Keep everything else EXACTLY as is, including all other sections, formatting, tables, and content.

IMPORTANT: This is a new conversation. Do not use any context from previous chats. Only use the information explicitly provided in this prompt.

## Document Type
TDD

## Current Document
[See docs/TDD.md]

## Sections to Modify

### 1. Section 2.2.3 Database Layer
After "Dependencies:", add this explanation:

**Why aiosqlite?**
The MCP server uses async/await (uvicorn, async handlers). Standard SQLite is synchronous—it blocks the event loop during queries, preventing the server from handling other requests. `aiosqlite` wraps SQLite to work with async/await, allowing non-blocking database operations.

### 2. Section 3.2 Storage Strategy → Indexing Strategy
After the indexing table, add this explanation:

**Why indexes matter:**
Without an index, SQLite scans ALL rows to find matches (slow with many records). An index creates a fast lookup structure—like a book index. We create indexes on columns frequently used in `WHERE` clauses (`completed`, `parent_id`).

### 3. Section 4.1 MCP Tool Definitions
At the beginning of section 4.1, before the first tool, add this explanation:

**Why Input Schemas?**
MCP requires each tool to define a JSON Schema for its inputs. This schema acts as a contract between ChatGPT and your tool. ChatGPT uses it to:
- Know what parameters to send
- Validate inputs before invoking
- Provide clear error messages if something is missing

Without schemas, ChatGPT wouldn't know how to call your tools correctly.

## Output
Return the COMPLETE document with ONLY these three additions. Do not change anything else.
