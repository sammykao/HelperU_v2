ALTER TABLE auth.users
ADD COLUMN IF NOT EXISTS phone_change_token_new text,
ADD COLUMN IF NOT EXISTS phone_change_token_current text,
ADD COLUMN IF NOT EXISTS phone_change_sent_at timestamptz,
ADD COLUMN IF NOT EXISTS phone_change text;