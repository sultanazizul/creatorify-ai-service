-- Add metadata and current_stage columns to projects table (for Video Generation)
ALTER TABLE public.projects
ADD COLUMN IF NOT EXISTS metadata jsonb DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS current_stage text;

CREATE INDEX IF NOT EXISTS idx_projects_stage ON public.projects(current_stage);
