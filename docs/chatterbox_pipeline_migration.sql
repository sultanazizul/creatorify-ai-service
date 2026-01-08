-- Migration to add pipeline tracking columns to chatterbox_projects
-- Run this in your Supabase SQL Editor

ALTER TABLE public.chatterbox_projects
ADD COLUMN IF NOT EXISTS metadata jsonb DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS current_stage text;

-- Create index for filtering by stage
CREATE INDEX IF NOT EXISTS idx_chatterbox_projects_stage ON public.chatterbox_projects(current_stage);
