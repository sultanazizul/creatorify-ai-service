# Deployment Instructions

## Prerequisites

1.  **Modal Account**: Ensure you are logged in (`modal token new`).
2.  **Supabase Project**:
    *   Create a project.
    *   Run the SQL to create the `projects` table (see below).
    *   Get `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`.
3.  **Cloudinary Account**:
    *   Get `Cloud Name`, `API Key`, `API Secret`.

## Database Setup (SQL)

Run this in your Supabase SQL Editor:

```sql
create table public.projects (
  id uuid default gen_random_uuid() primary key,
  user_id text,
  title text,
  description text,
  image_url text,
  audio_url text,
  prompt text,
  call_id text,
  status text default 'queued',
  progress int default 0,
  video_url text,
  error_message text,
  parameters jsonb,
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now())
);
```

## Secrets Setup

Create the secrets in Modal:

```bash
modal secret create supabase-secrets \
    SUPABASE_URL="https://your-project.supabase.co" \
    SUPABASE_SERVICE_ROLE="your-service-role-key"

modal secret create cloudinary-secrets \
    CLOUDINARY_CLOUD_NAME="your-cloud-name" \
    CLOUDINARY_API_KEY="your-api-key" \
    CLOUDINARY_API_SECRET="your-api-secret"

modal secret create api-key-secret \
    API_KEY="your-super-secret-key"
```

## Deployment

To deploy the application:

```bash
modal deploy app.py
```

This will output the base URL for your API, e.g., `https://your-workspace--infinitetalk-api-fastapi-app.modal.run`.

## Testing

Use the Postman collection to test the endpoints.
