# API Overview

## TreeLine Public API

The TreeLine API provides programmatic access to your projects, tasks, and team data, enabling custom integrations and automated workflows.

## API Basics

### Base URL
All API requests are made to:
```
https://api.treeline.com/v1/
```

### Authentication
TreeLine API uses API keys for authentication:
- Include your API key in the `Authorization` header
- Format: `Authorization: Bearer YOUR_API_KEY`
- API keys are available in Settings > API

### Request Format
- **Content-Type**: `application/json`
- **Method**: RESTful HTTP methods (GET, POST, PUT, DELETE)
- **Encoding**: UTF-8

### Response Format
All responses are returned in JSON format:
```json
{
  "data": {...},
  "meta": {
    "status": "success",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Core Resources

### Projects
Manage your TreeLine projects programmatically.

**Endpoints:**
- `GET /projects` - List all projects
- `GET /projects/{id}` - Get specific project
- `POST /projects` - Create new project
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

**Project Object:**
```json
{
  "id": "proj_123456",
  "name": "Website Redesign",
  "description": "Complete overhaul of company website",
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "owner_id": "user_789",
  "team_members": ["user_789", "user_456"],
  "tags": ["web", "design", "priority-high"]
}
```

### Tasks
Create and manage tasks within projects.

**Endpoints:**
- `GET /projects/{project_id}/tasks` - List project tasks
- `GET /tasks/{id}` - Get specific task
- `POST /projects/{project_id}/tasks` - Create new task
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task

**Task Object:**
```json
{
  "id": "task_789123",
  "title": "Design homepage mockup",
  "description": "Create initial design concepts",
  "status": "in_progress",
  "priority": "high",
  "assignee_id": "user_456",
  "project_id": "proj_123456",
  "due_date": "2024-01-20T23:59:59Z",
  "created_at": "2024-01-10T09:00:00Z",
  "updated_at": "2024-01-15T14:30:00Z",
  "tags": ["design", "frontend"]
}
```

### Users
Access team member information and permissions.

**Endpoints:**
- `GET /users` - List team members
- `GET /users/{id}` - Get specific user
- `GET /users/me` - Get current user info

**User Object:**
```json
{
  "id": "user_456",
  "email": "john@company.com",
  "name": "John Smith",
  "role": "member",
  "avatar_url": "https://cdn.treeline.com/avatars/user_456.jpg",
  "created_at": "2023-12-01T00:00:00Z",
  "last_active": "2024-01-15T16:45:00Z"
}
```

### Comments
Manage task and project comments.

**Endpoints:**
- `GET /tasks/{task_id}/comments` - List task comments
- `POST /tasks/{task_id}/comments` - Add comment
- `PUT /comments/{id}` - Update comment
- `DELETE /comments/{id}` - Delete comment

## API Capabilities

### Data Retrieval
- **List Resources**: Get paginated lists of projects, tasks, users
- **Filter & Search**: Use query parameters to filter results
- **Sorting**: Sort results by various fields
- **Relationships**: Include related data in responses

### Data Modification
- **Create**: Add new projects, tasks, and comments
- **Update**: Modify existing resources
- **Delete**: Remove resources (with proper permissions)
- **Bulk Operations**: Perform actions on multiple items

### Real-time Updates
- **Webhooks**: Receive notifications when data changes
- **Event Streaming**: Subscribe to real-time events
- **Change Tracking**: Monitor resource modifications

## Query Parameters

### Pagination
Control result pagination:
```
GET /projects?page=2&per_page=50
```

Parameters:
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 25, max: 100)

### Filtering
Filter results by various criteria:
```
GET /tasks?status=active&assignee_id=user_456&priority=high
```

Common filters:
- `status`: Filter by status
- `assignee_id`: Filter by assigned user
- `created_after`: Filter by creation date
- `updated_since`: Filter by modification date

### Sorting
Sort results by field:
```
GET /projects?sort=created_at&order=desc
```

Parameters:
- `sort`: Field to sort by
- `order`: `asc` or `desc` (default: asc)

### Including Related Data
Include related resources:
```
GET /projects?include=tasks,team_members
```

Available includes:
- `tasks`: Include project tasks
- `team_members`: Include team member details
- `comments`: Include recent comments

## Rate Limiting

### Limits
- **Standard Plan**: 1,000 requests per hour
- **Professional Plan**: 5,000 requests per hour
- **Enterprise Plan**: 25,000 requests per hour

### Rate Limit Headers
Response headers indicate current usage:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
```

### Handling Rate Limits
When rate limited (HTTP 429):
```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "API rate limit exceeded",
    "retry_after": 3600
  }
}
```

## Error Handling

### HTTP Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `429`: Rate Limited
- `500`: Server Error

### Error Response Format
```json
{
  "error": {
    "code": "validation_failed",
    "message": "The request data is invalid",
    "details": {
      "name": ["Name is required"],
      "email": ["Email format is invalid"]
    }
  }
}
```

## Security

### API Key Management
- **Generation**: Create API keys in Settings > API
- **Scoping**: Limit API key permissions
- **Rotation**: Regularly rotate API keys
- **Revocation**: Immediately revoke compromised keys

### Permissions
API access respects user permissions:
- **Read**: View projects and tasks you have access to
- **Write**: Modify resources you can edit
- **Admin**: Full access to organization data

### Best Practices
- **HTTPS Only**: All API calls must use HTTPS
- **Key Storage**: Store API keys securely
- **Minimal Scope**: Use least-privilege principle
- **Monitoring**: Monitor API usage for anomalies

## Webhooks

### Setting Up Webhooks
1. Go to Settings > API > Webhooks
2. Add webhook URL
3. Select events to monitor
4. Configure authentication (optional)
5. Test webhook delivery

### Webhook Events
Available events:
- `project.created`
- `project.updated`
- `project.deleted`
- `task.created`
- `task.updated`
- `task.completed`
- `user.added`
- `user.removed`

### Webhook Payload
```json
{
  "event": "task.completed",
  "timestamp": "2024-01-15T16:30:00Z",
  "data": {
    "task": {
      "id": "task_789123",
      "title": "Design homepage mockup",
      "status": "completed"
    }
  }
}
```

## SDKs and Libraries

### Official SDKs
- **JavaScript/Node.js**: `npm install @treeline/api`
- **Python**: `pip install treeline-api`
- **PHP**: `composer require treeline/api`
- **Ruby**: `gem install treeline-api`

### Community Libraries
- **Go**: github.com/community/treeline-go
- **Java**: Available on Maven Central
- **C#**: NuGet package available

### Example Usage (JavaScript)
```javascript
const TreeLine = require('@treeline/api');

const client = new TreeLine({
  apiKey: 'your_api_key_here'
});

// Get all projects
const projects = await client.projects.list();

// Create a new task
const task = await client.tasks.create({
  project_id: 'proj_123456',
  title: 'New task',
  assignee_id: 'user_789'
});
```

## API Versioning

### Current Version
- **Version**: v1
- **Status**: Stable
- **Support**: Long-term support guaranteed

### Version Strategy
- **Backward Compatibility**: Maintained within major versions
- **Deprecation Notice**: 6 months advance notice
- **Migration Support**: Comprehensive migration guides

### Version Headers
Specify API version:
```
Accept: application/vnd.treeline.v1+json
```

## Getting Started

### Quick Start
1. **Get API Key**: Generate in Settings > API
2. **Test Connection**: Make a simple GET request
3. **Explore Endpoints**: Use API documentation
4. **Build Integration**: Start with basic operations

### Testing
Use our API explorer:
- **Interactive Docs**: api-docs.treeline.com
- **Postman Collection**: Available for download
- **Sandbox Environment**: Test without affecting live data

### Support
- **Documentation**: api-docs.treeline.com
- **Support Email**: api-support@treeline.com
- **Developer Forum**: developers.treeline.com
- **Status Page**: status.treeline.com

Ready to build with TreeLine? Start exploring our comprehensive API documentation and join our developer community.
