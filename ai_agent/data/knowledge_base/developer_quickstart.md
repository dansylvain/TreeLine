# Developer Quickstart

## Get Started with TreeLine API in Minutes

This guide will have you making your first API calls to TreeLine in under 10 minutes.

## Prerequisites

Before you begin, make sure you have:
- A TreeLine account (sign up at www.treeline.com)
- Basic knowledge of REST APIs
- A development environment with your preferred programming language
- An HTTP client (curl, Postman, or similar)

## Step 1: Get Your API Key

### Generate API Key
1. Log into your TreeLine account
2. Go to Settings > API
3. Click "Generate New API Key"
4. Give your key a descriptive name (e.g., "Development Key")
5. Copy and securely store your API key

**Important**: Your API key is shown only once. Store it securely!

### Test Your Key
Verify your API key works:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.treeline.com/v1/users/me
```

Expected response:
```json
{
  "data": {
    "id": "user_123",
    "name": "Your Name",
    "email": "you@company.com"
  }
}
```

## Step 2: Make Your First API Call

### List Your Projects
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.treeline.com/v1/projects
```

### Create a New Project
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "My First API Project",
       "description": "Created via API"
     }' \
     https://api.treeline.com/v1/projects
```

## Step 3: Language-Specific Examples

### JavaScript/Node.js

#### Installation
```bash
npm install @treeline/api
```

#### Basic Usage
```javascript
const TreeLine = require('@treeline/api');

const client = new TreeLine({
  apiKey: 'your_api_key_here'
});

async function quickStart() {
  try {
    // Get current user
    const user = await client.users.me();
    console.log('Hello,', user.name);

    // List projects
    const projects = await client.projects.list();
    console.log('You have', projects.length, 'projects');

    // Create a new project
    const newProject = await client.projects.create({
      name: 'API Test Project',
      description: 'Testing the TreeLine API'
    });
    console.log('Created project:', newProject.id);

    // Create a task in the project
    const task = await client.tasks.create({
      project_id: newProject.id,
      title: 'My first API task',
      description: 'This task was created via API'
    });
    console.log('Created task:', task.id);

  } catch (error) {
    console.error('Error:', error.message);
  }
}

quickStart();
```

### Python

#### Installation
```bash
pip install treeline-api
```

#### Basic Usage
```python
from treeline import TreeLineClient

client = TreeLineClient(api_key='your_api_key_here')

def quick_start():
    try:
        # Get current user
        user = client.users.me()
        print(f"Hello, {user['name']}")

        # List projects
        projects = client.projects.list()
        print(f"You have {len(projects)} projects")

        # Create a new project
        new_project = client.projects.create({
            'name': 'API Test Project',
            'description': 'Testing the TreeLine API'
        })
        print(f"Created project: {new_project['id']}")

        # Create a task
        task = client.tasks.create({
            'project_id': new_project['id'],
            'title': 'My first API task',
            'description': 'This task was created via API'
        })
        print(f"Created task: {task['id']}")

    except Exception as error:
        print(f"Error: {error}")

if __name__ == "__main__":
    quick_start()
```

### PHP

#### Installation
```bash
composer require treeline/api
```

#### Basic Usage
```php
<?php
require_once 'vendor/autoload.php';

use TreeLine\Client;

$client = new Client([
    'api_key' => 'your_api_key_here'
]);

try {
    // Get current user
    $user = $client->users->me();
    echo "Hello, " . $user['name'] . "\n";

    // List projects
    $projects = $client->projects->list();
    echo "You have " . count($projects) . " projects\n";

    // Create a new project
    $newProject = $client->projects->create([
        'name' => 'API Test Project',
        'description' => 'Testing the TreeLine API'
    ]);
    echo "Created project: " . $newProject['id'] . "\n";

    // Create a task
    $task = $client->tasks->create([
        'project_id' => $newProject['id'],
        'title' => 'My first API task',
        'description' => 'This task was created via API'
    ]);
    echo "Created task: " . $task['id'] . "\n";

} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}
?>
```

### Ruby

#### Installation
```bash
gem install treeline-api
```

#### Basic Usage
```ruby
require 'treeline'

client = TreeLine::Client.new(api_key: 'your_api_key_here')

begin
  # Get current user
  user = client.users.me
  puts "Hello, #{user['name']}"

  # List projects
  projects = client.projects.list
  puts "You have #{projects.length} projects"

  # Create a new project
  new_project = client.projects.create(
    name: 'API Test Project',
    description: 'Testing the TreeLine API'
  )
  puts "Created project: #{new_project['id']}"

  # Create a task
  task = client.tasks.create(
    project_id: new_project['id'],
    title: 'My first API task',
    description: 'This task was created via API'
  )
  puts "Created task: #{task['id']}"

rescue TreeLine::Error => e
  puts "Error: #{e.message}"
end
```

## Step 4: Common Operations

### Working with Tasks

#### Get Tasks for a Project
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.treeline.com/v1/projects/PROJECT_ID/tasks
```

#### Update a Task
```bash
curl -X PUT \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "status": "completed",
       "priority": "high"
     }' \
     https://api.treeline.com/v1/tasks/TASK_ID
```

#### Add a Comment
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "content": "Great work on this task!"
     }' \
     https://api.treeline.com/v1/tasks/TASK_ID/comments
```

### Filtering and Searching

#### Get Active Tasks
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     "https://api.treeline.com/v1/tasks?status=active"
```

#### Get Tasks Assigned to You
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     "https://api.treeline.com/v1/tasks?assignee_id=YOUR_USER_ID"
```

#### Search Projects
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     "https://api.treeline.com/v1/projects?search=website"
```

## Step 5: Error Handling

### Common HTTP Status Codes
- `200`: Success
- `201`: Created successfully
- `400`: Bad request (check your data)
- `401`: Unauthorized (check your API key)
- `404`: Resource not found
- `422`: Validation error
- `429`: Rate limit exceeded

### Example Error Response
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

### Handling Errors in Code

#### JavaScript
```javascript
try {
  const project = await client.projects.create(data);
} catch (error) {
  if (error.status === 422) {
    console.log('Validation errors:', error.details);
  } else if (error.status === 429) {
    console.log('Rate limited. Retry after:', error.retryAfter);
  } else {
    console.log('Unexpected error:', error.message);
  }
}
```

#### Python
```python
try:
    project = client.projects.create(data)
except TreeLineValidationError as e:
    print(f"Validation errors: {e.details}")
except TreeLineRateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}")
except TreeLineError as e:
    print(f"API error: {e.message}")
```

## Step 6: Rate Limiting

### Understanding Limits
- **Standard**: 1,000 requests/hour
- **Professional**: 5,000 requests/hour
- **Enterprise**: 25,000 requests/hour

### Check Your Usage
```bash
curl -I -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.treeline.com/v1/projects
```

Look for these headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
```

### Best Practices
- Cache responses when possible
- Use pagination for large datasets
- Implement exponential backoff for retries
- Monitor your usage regularly

## Step 7: Webhooks Setup

### Create a Webhook
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://your-app.com/webhooks/treeline",
       "events": ["task.created", "task.completed"]
     }' \
     https://api.treeline.com/v1/webhooks
```

### Handle Webhook Events
```javascript
// Express.js example
app.post('/webhooks/treeline', (req, res) => {
  const event = req.body;
  
  switch (event.type) {
    case 'task.created':
      console.log('New task created:', event.data.task.title);
      break;
    case 'task.completed':
      console.log('Task completed:', event.data.task.title);
      break;
  }
  
  res.status(200).send('OK');
});
```

## Next Steps

### Explore More Features
- **Bulk Operations**: Update multiple resources at once
- **Advanced Filtering**: Complex queries with multiple parameters
- **File Attachments**: Upload and manage files
- **Custom Fields**: Work with custom project and task fields

### Best Practices
- **Environment Variables**: Store API keys securely
- **Error Logging**: Implement comprehensive error handling
- **Testing**: Use our sandbox environment for development
- **Documentation**: Keep your integration documented

### Resources
- **Full API Documentation**: api-docs.treeline.com
- **SDK Documentation**: docs.treeline.com/sdks
- **Developer Forum**: developers.treeline.com
- **Code Examples**: github.com/treeline/examples

### Getting Help
- **Support Email**: api-support@treeline.com
- **Live Chat**: Available during business hours
- **Community**: Join our developer Slack channel

## Quick Reference

### Base URL
```
https://api.treeline.com/v1/
```

### Authentication Header
```
Authorization: Bearer YOUR_API_KEY
```

### Content Type
```
Content-Type: application/json
```

### Essential Endpoints
- `GET /users/me` - Current user info
- `GET /projects` - List projects
- `POST /projects` - Create project
- `GET /projects/{id}/tasks` - List tasks
- `POST /projects/{id}/tasks` - Create task
- `PUT /tasks/{id}` - Update task

You're now ready to build amazing integrations with TreeLine! Start with these basics and gradually explore more advanced features as your needs grow.
