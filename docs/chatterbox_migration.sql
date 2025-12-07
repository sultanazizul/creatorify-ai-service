-- Chatterbox Database Schema Migration
-- Run this in your Supabase SQL Editor

-- 1. Create voice_samples table
create table if not exists public.voice_samples (
  id uuid not null default gen_random_uuid(),
  created_at timestamp with time zone not null default now(),
  user_id text not null,
  name text not null,
  description text,
  audio_url text not null,
  duration_seconds float,
  sample_rate integer default 24000,
  language_hint text,
  is_public boolean default false,
  metadata jsonb,
  constraint voice_samples_pkey primary key (id)
);

-- Create indexes for voice_samples
create index if not exists idx_voice_samples_user_id on public.voice_samples(user_id);
create index if not exists idx_voice_samples_is_public on public.voice_samples(is_public);

-- 2. Create chatterbox_projects table
create table if not exists public.chatterbox_projects (
  id uuid not null default gen_random_uuid(),
  created_at timestamp with time zone not null default now(),
  user_id text not null default 'anonymous',
  
  -- Project type
  project_type text not null,
  
  -- Input parameters
  text text,
  language_id text,
  voice_sample_id uuid,
  source_audio_url text,
  
  -- Generation parameters
  exaggeration float default 0.5,
  temperature float default 0.8,
  cfg_weight float default 0.5,
  repetition_penalty float default 1.2,
  min_p float default 0.05,
  top_p float default 1.0,
  
  -- Output
  audio_url text,
  duration_seconds float,
  
  -- Status tracking
  status text not null default 'pending',
  progress integer default 0,
  error_message text,
  
  constraint chatterbox_projects_pkey primary key (id),
  constraint fk_voice_sample foreign key (voice_sample_id) 
    references voice_samples(id) on delete set null
);

-- Create indexes for chatterbox_projects
create index if not exists idx_chatterbox_projects_user_id on public.chatterbox_projects(user_id);
create index if not exists idx_chatterbox_projects_type on public.chatterbox_projects(project_type);
create index if not exists idx_chatterbox_projects_status on public.chatterbox_projects(status);
create index if not exists idx_chatterbox_created_at on public.chatterbox_projects(created_at desc);

-- Add RLS (Row Level Security) policies if needed
-- alter table public.voice_samples enable row level security;
-- alter table public.chatterbox_projects enable row level security;

-- Grant permissions (adjust as needed)
-- grant all on public.voice_samples to authenticated;
-- grant all on public.chatterbox_projects to authenticated;
