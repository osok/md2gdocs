# Sample Document with Mermaid Diagrams

## Introduction

This is a sample markdown document that demonstrates the conversion of Mermaid diagrams to Google Docs.

## System Architecture

Our application follows a typical three-tier architecture:

```mermaid
graph TB
    subgraph "Presentation Layer"
        UI[Web UI]
        Mobile[Mobile App]
    end
    
    subgraph "Business Layer"
        API[REST API]
        BL[Business Logic]
        Auth[Authentication]
    end
    
    subgraph "Data Layer"
        DB[(Database)]
        Cache[(Redis Cache)]
        Files[File Storage]
    end
    
    UI --> API
    Mobile --> API
    API --> BL
    API --> Auth
    BL --> DB
    BL --> Cache
    BL --> Files
```

## User Flow

Here's how a typical user interaction works:

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Database
    
    User->>Frontend: Login Request
    Frontend->>API: POST /auth/login
    API->>Database: Verify Credentials
    Database-->>API: User Data
    API-->>Frontend: JWT Token
    Frontend-->>User: Dashboard View
    
    Note over User,Database: User is now authenticated
    
    User->>Frontend: Request Data
    Frontend->>API: GET /api/data
    API->>Database: Query Data
    Database-->>API: Results
    API-->>Frontend: JSON Response
    Frontend-->>User: Display Data
```

## Development Process

Our development workflow:

```mermaid
gitGraph
    commit
    commit
    branch feature
    checkout feature
    commit
    commit
    checkout main
    merge feature
    commit
    branch hotfix
    checkout hotfix
    commit
    checkout main
    merge hotfix
```

## State Machine Example

User account states:

```mermaid
stateDiagram-v2
    [*] --> Pending: User Registers
    Pending --> Active: Email Verified
    Pending --> Expired: Timeout
    Active --> Suspended: Policy Violation
    Active --> Deleted: User Request
    Suspended --> Active: Appeal Approved
    Suspended --> Deleted: Final Decision
    Deleted --> [*]
    Expired --> [*]
```

## Code Examples

### Python Example

```python
def fibonacci(n):
    """Generate Fibonacci sequence up to n terms."""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib_sequence = [0, 1]
    for i in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    
    return fib_sequence

# Example usage
print(fibonacci(10))
```

### JavaScript Example

```javascript
// Async function to fetch user data
async function fetchUserData(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching user data:', error);
        return null;
    }
}
```

## Project Timeline

```mermaid
gantt
    title Project Development Timeline
    dateFormat  YYYY-MM-DD
    section Phase 1
    Requirements Analysis    :done,    des1, 2024-01-01, 2024-01-15
    System Design           :done,    des2, 2024-01-15, 2024-01-30
    section Phase 2
    Backend Development     :active,  dev1, 2024-02-01, 2024-03-15
    Frontend Development    :active,  dev2, 2024-02-15, 2024-03-30
    section Phase 3
    Testing                 :         test1, 2024-03-20, 2024-04-10
    Deployment             :         deploy, 2024-04-10, 2024-04-20
```

## Pie Chart Example

Distribution of development time:

```mermaid
pie title Development Time Distribution
    "Backend" : 35
    "Frontend" : 30
    "Testing" : 20
    "Documentation" : 10
    "Deployment" : 5
```

## Table

**Structured Log Format Requirements:**

| Field | Type | Required | Example | Description |
|-------|------|----------|---------|-------------|
| level | string | Yes | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| event | string | Yes | `task_assigned` | Event type identifier |
| task_id | string | No | `task_001` | Task identifier (when applicable) |
| priority | integer | No | `85` | Task priority (for task events) |
| assignment_score | float | No | `0.92` | Assignment score (for assignment events) |
| message | string | Yes | `test` | Human-readable message |

## Conclusion

This document demonstrates various types of Mermaid diagrams that can be converted to Google Docs format with embedded images.

### Features Demonstrated

- Flowcharts and graphs
- Sequence diagrams
- Git graphs
- State diagrams
- Gantt charts
- Pie charts
- Code blocks with syntax highlighting
- Regular markdown formatting

All these elements will be properly converted to Google Docs format.

