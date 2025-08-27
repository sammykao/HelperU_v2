-- SQL script to fill out missing fields in auth.users table
-- This updates existing users to have proper default values for all required fields

-- First, let's see what fields are currently NULL
SELECT 
    id,
    instance_id,
    aud,
    role,
    email,
    phone,
    email_confirmed_at,
    phone_confirmed_at,
    created_at,
    updated_at,
    raw_app_meta_data,
    raw_user_meta_data,
    is_super_admin,
    encrypted_password,
    email_change_confirm_status,
    banned_until,
    reauthentication_sent_at,
    last_sign_in_at,
    email_change,
    email_change_token_new,
    recovery_sent_at,
    phone_change,
    phone_change_token_new,
    phone_change_sent_at,
    email_change_sent_at,
    last_sign_in_with_password_change_at,
    confirmation_token,
    confirmation_sent_at,
    recovery_token,
    recovery_sent_at,
    email_change_token_current,
    reauthentication_token,
    is_sso_user,
    deleted_at,
    is_anonymous,
    invited_at,
    confirmed_at
FROM auth.users 
WHERE instance_id IS NULL 
   OR aud IS NULL 
   OR role IS NULL 
   OR raw_app_meta_data IS NULL 
   OR raw_user_meta_data IS NULL
LIMIT 5;

-- Update all users to fill missing required fields
UPDATE auth.users 
SET 
    -- Required fields that should never be NULL
    instance_id = COALESCE(instance_id, 'afcomoghfkzsahnrdrxs'),
    aud = COALESCE(aud, 'authenticated'),
    role = COALESCE(role, 'authenticated'),
    
    -- JSON metadata fields
    raw_app_meta_data = COALESCE(raw_app_meta_data, '{"provider": "email", "providers": ["email"]}'),
    raw_user_meta_data = COALESCE(raw_user_meta_data, '{"phone_verified": true, "verification_status": "verified"}'),
    
    -- Boolean fields
    is_super_admin = COALESCE(is_super_admin, false),
    is_sso_user = COALESCE(is_sso_user, false),
    is_anonymous = COALESCE(is_anonymous, false),
    
    -- String fields
    encrypted_password = COALESCE(encrypted_password, ''),
    email_change = COALESCE(email_change, ''),
    email_change_token_new = COALESCE(email_change_token_new, ''),
    recovery_token = COALESCE(recovery_token, ''),
    phone_change = COALESCE(phone_change, ''),
    phone_change_token_new = COALESCE(phone_change_token_new, ''),
    email_change_token_current = COALESCE(email_change_token_current, ''),
    reauthentication_token = COALESCE(reauthentication_token, ''),
    confirmation_token = COALESCE(confirmation_token, 'migrated_' || id),
    
    -- Integer fields
    email_change_confirm_status = COALESCE(email_change_confirm_status, 0),
    
    -- Timestamp fields - use created_at if available, otherwise current time
    created_at = COALESCE(created_at, NOW()),
    updated_at = COALESCE(updated_at, NOW()),
    email_confirmed_at = COALESCE(email_confirmed_at, created_at),
    phone_confirmed_at = COALESCE(phone_confirmed_at, created_at),
    confirmed_at = COALESCE(confirmed_at, created_at),
    
    -- Set confirmation_sent_at to created_at if NULL
    confirmation_sent_at = COALESCE(confirmation_sent_at, created_at),
    
    -- All other timestamp fields can remain NULL (they're optional)
    invited_at = invited_at,
    banned_until = banned_until,
    reauthentication_sent_at = reauthentication_sent_at,
    last_sign_in_at = last_sign_in_at,
    email_change_sent_at = email_change_sent_at,
    recovery_sent_at = recovery_sent_at,
    phone_change_sent_at = phone_change_sent_at,
    last_sign_in_with_password_change_at = last_sign_in_with_password_change_at,
    deleted_at = deleted_at

WHERE instance_id IS NULL 
   OR aud IS NULL 
   OR role IS NULL 
   OR raw_app_meta_data IS NULL 
   OR raw_user_meta_data IS NULL
   OR is_super_admin IS NULL
   OR is_sso_user IS NULL
   OR is_anonymous IS NULL
   OR encrypted_password IS NULL
   OR email_change IS NULL
   OR email_change_token_new IS NULL
   OR recovery_token IS NULL
   OR phone_change IS NULL
   OR phone_change_token_new IS NULL
   OR email_change_token_current IS NULL
   OR reauthentication_token IS NULL
   OR confirmation_token IS NULL
   OR email_change_confirm_status IS NULL
   OR created_at IS NULL
   OR updated_at IS NULL
   OR email_confirmed_at IS NULL
   OR phone_confirmed_at IS NULL
   OR confirmed_at IS NULL
   OR confirmation_sent_at IS NULL;

-- Verify the update worked
SELECT 
    id,
    instance_id,
    aud,
    role,
    email,
    phone,
    email_confirmed_at,
    phone_confirmed_at,
    created_at,
    updated_at,
    raw_app_meta_data,
    raw_user_meta_data,
    is_super_admin,
    encrypted_password,
    email_change_confirm_status,
    banned_until,
    reauthentication_sent_at,
    last_sign_in_at,
    email_change,
    email_change_token_new,
    recovery_sent_at,
    phone_change,
    phone_change_token_new,
    phone_change_sent_at,
    email_change_sent_at,
    last_sign_in_with_password_change_at,
    confirmation_token,
    confirmation_sent_at,
    recovery_token,
    recovery_sent_at,
    email_change_token_current,
    reauthentication_token,
    is_sso_user,
    deleted_at,
    is_anonymous,
    invited_at,
    confirmed_at
FROM auth.users 
LIMIT 3;
