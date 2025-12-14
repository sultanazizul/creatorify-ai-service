-- Run this script in the Supabase SQL Editor

-- 1. Add the is_public column with default FALSE
ALTER TABLE avatars 
ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT FALSE;

-- 2. Update all existing avatars to be public (TRUE) as requested
UPDATE avatars 
SET is_public = TRUE;

-- 3. (Optional) Verify the changes
-- SELECT * FROM avatars;
