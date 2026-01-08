-- Add metadata and current_stage columns to tts_projects table
ALTER TABLE public.tts_projects
ADD COLUMN IF NOT EXISTS metadata jsonb DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS current_stage text;

CREATE INDEX IF NOT EXISTS idx_tts_projects_stage ON public.tts_projects(current_stage);
