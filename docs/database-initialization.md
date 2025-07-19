# Database Initialization Solutions for TreeLine AI Customer Support Agent

## Problem Solved

The PostgreSQL initialization script (`config/docker/postgres/init.sql`) was failing to mount properly in Docker Compose, causing the error:
```
error mounting "/path/to/init.sql" to rootfs: not a directory: unknown: Are you trying to mount a directory onto a file (or vice-versa)?
```

## Solution Implemented

### Primary Solution: Fixed File Mount with Read-Only Flag

**File:** `docker-compose.yml`
```yaml
postgres:
  image: postgres:15
  volumes:
    - postgres_data:/var/lib/postgresql/data
    - ./config/docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
```

**Key Changes:**
1. Added `:ro` (read-only) flag to the volume mount
2. Ensured proper file path resolution

**Why This Works:**
- The `:ro` flag prevents Docker from trying to create a directory
- PostgreSQL's official Docker image automatically executes any `.sql` files in `/docker-entrypoint-initdb.d/` during first-time initialization
- The script only runs when the database is created for the first time (empty data directory)

## Verification Steps

1. **Check Mount Configuration:**
   ```bash
   docker-compose config
   ```

2. **Verify Database Initialization:**
   ```bash
   # Remove existing volumes to trigger fresh initialization
   docker-compose down -v
   
   # Start PostgreSQL service
   docker-compose up postgres -d
   
   # Check logs for initialization
   docker-compose logs postgres
   ```

3. **Verify Schema Creation:**
   ```bash
   # List tables
   docker-compose exec postgres psql -U treeline_user -d treeline -c "\dt"
   
   # Check table structure
   docker-compose exec postgres psql -U treeline_user -d treeline -c "\d conversations"
   ```

## Alternative Solutions

### Solution 2: Directory Mount Approach

Instead of mounting a single file, mount the entire directory:

```yaml
postgres:
  volumes:
    - postgres_data:/var/lib/postgresql/data
    - ./config/docker/postgres:/docker-entrypoint-initdb.d
```

**Pros:**
- More flexible for multiple initialization scripts
- Avoids file-specific mounting issues

**Cons:**
- Mounts entire directory, potentially including unwanted files
- Requires careful directory structure management

### Solution 3: Multi-Stage Docker Build

Create a custom PostgreSQL image with the initialization script baked in:

```dockerfile
# config/docker/postgres/Dockerfile
FROM postgres:15

COPY init.sql /docker-entrypoint-initdb.d/
```

**docker-compose.yml:**
```yaml
postgres:
  build:
    context: ./config/docker/postgres
    dockerfile: Dockerfile
```

**Pros:**
- No mounting issues
- Initialization script is part of the image

**Cons:**
- Requires rebuilding image for script changes
- More complex deployment

### Solution 4: Init Container Pattern

Use an init container to set up the database:

```yaml
services:
  postgres-init:
    image: postgres:15
    depends_on:
      - postgres
    volumes:
      - ./config/docker/postgres/init.sql:/init.sql
    command: >
      bash -c "
        until pg_isready -h postgres -U treeline_user; do
          echo 'Waiting for postgres...'
          sleep 2
        done
        psql -h postgres -U treeline_user -d treeline -f /init.sql
      "
    environment:
      PGPASSWORD: treeline_password
```

**Pros:**
- Can run initialization scripts at any time
- More control over initialization timing

**Cons:**
- More complex setup
- Requires additional container

## Best Practices

### 1. Database Initialization Scripts

- **Use idempotent SQL:** Always use `CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`, etc.
- **Order matters:** Name scripts with prefixes (01-schema.sql, 02-data.sql) for execution order
- **Keep scripts focused:** Separate schema creation, data insertion, and configuration

### 2. Volume Management

- **Use named volumes:** For persistent data storage
- **Clean initialization:** Use `docker-compose down -v` to reset database for testing
- **Backup considerations:** Named volumes can be backed up separately

### 3. Environment Configuration

```yaml
environment:
  POSTGRES_DB: treeline
  POSTGRES_USER: treeline_user
  POSTGRES_PASSWORD: treeline_password
  # Optional: Skip initialization if data exists
  POSTGRES_INITDB_SKIP_LOCALHOST_CHECK: "true"
```

### 4. Health Checks

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U treeline_user -d treeline"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### 5. Security Considerations

- Use environment variables for sensitive data
- Consider using Docker secrets for production
- Limit database user permissions
- Use read-only mounts where possible

## Troubleshooting

### Common Issues

1. **"Database already exists" - Scripts not running:**
   - Solution: Remove volumes with `docker-compose down -v`
   - Reason: Init scripts only run on first database creation

2. **Permission denied errors:**
   - Solution: Check file permissions on host
   - Command: `chmod 644 config/docker/postgres/init.sql`

3. **Mount path issues:**
   - Solution: Use absolute paths or ensure correct working directory
   - Verify: `docker-compose config` shows correct resolved paths

4. **SQL syntax errors:**
   - Solution: Test SQL scripts manually
   - Command: `psql -U treeline_user -d treeline -f init.sql`

### Debugging Commands

```bash
# Check container logs
docker-compose logs postgres

# Execute commands in running container
docker-compose exec postgres bash

# Check mounted files
docker-compose exec postgres ls -la /docker-entrypoint-initdb.d/

# Test database connection
docker-compose exec postgres psql -U treeline_user -d treeline -c "SELECT version();"
```

## Current Implementation Status

✅ **RESOLVED:** PostgreSQL initialization script now runs successfully
✅ **VERIFIED:** Database schema created with proper tables and indexes
✅ **TESTED:** Full stack deployment working (PostgreSQL, FastAPI, AI Agent, Streamlit)

The TreeLine AI Customer Support Agent project now has a robust database initialization system that properly creates the required schema when containers start up.
