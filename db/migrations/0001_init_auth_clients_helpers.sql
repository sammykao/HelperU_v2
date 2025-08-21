BEGIN;

CREATE TABLE IF NOT EXISTS public.clients (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  phone TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL UNIQUE, 
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  pfp_url TEXT,
  number_of_posts INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.helpers (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL UNIQUE,
  phone TEXT NOT NULL UNIQUE,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  pfp_url TEXT,
  college TEXT NOT NULL,
  bio TEXT NOT NULL,
  graduation_year INTEGER NOT NULL,
  zip_code TEXT NOT NULL public.zip_codes(zip_code) ON DELETE CASCADE,
  number_of_applications INTEGER NOT NULL DEFAULT 0,
  invited_count INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.zip_codes (
  zip_code TEXT PRIMARY KEY,
  state TEXT NOT NULL,
  city TEXT NOT NULL,
  lat DECIMAL NOT NULL,
  lng DECIMAL NOT NULL
);

CREATE TABLE IF NOT EXISTS public.tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID NOT NULL REFERENCES public.clients(id) ON DELETE CASCADE,
  hourly_rate FLOAT NOT NULL,
  title TEXT NOT NULL,
  dates JSONB NOT NULL,
  location_type TEXT NOT NULL,
  zip_code TEXT REFERENCES public.zip_codes(zip_code) ON DELETE CASCADE,
  description TEXT NOT NULL,
  tools_info TEXT,
  public_transport_info TEXT,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);


CREATE TABLE IF NOT EXISTS public.applications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id UUID NOT NULL REFERENCES public.tasks(id) ON DELETE CASCADE,
  helper_id UUID NOT NULL REFERENCES public.helpers(id) ON DELETE CASCADE,
  introduction_message TEXT NOT NULL,
  supplements_url TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.invitations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id UUID NOT NULL REFERENCES public.tasks(id) ON DELETE CASCADE,
  helper_id UUID NOT NULL REFERENCES public.helpers(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE public.chats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  users JSONB(UUID) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE public.chat_users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  chat_id UUID NOT NULL REFERENCES public.chats(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE public.messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  chat_id UUID NOT NULL REFERENCES public.chats(id) ON DELETE CASCADE,
  sender_id UUID NOT NULL REFERENCES public.chat_users(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  read_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);


CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END
$$;

DROP TRIGGER IF EXISTS set_clients_updated_at ON public.clients;
CREATE TRIGGER set_clients_updated_at
BEFORE UPDATE ON public.clients
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS set_helpers_updated_at ON public.helpers;
CREATE TRIGGER set_helpers_updated_at
BEFORE UPDATE ON public.helpers
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE TRIGGER set_tasks_updated_at
BEFORE UPDATE ON public.tasks
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Ensure client phone is verified and matches auth.users
CREATE OR REPLACE FUNCTION public.ensure_client_phone_verified()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  ok BOOLEAN;
BEGIN
  SELECT (u.phone = NEW.phone) AND (u.phone_confirmed_at IS NOT NULL)
    INTO ok
  FROM auth.users u
  WHERE u.id = NEW.id
  LIMIT 1;

  IF NOT COALESCE(ok, FALSE) THEN
    RAISE EXCEPTION 'Phone is not verified for this user or does not match';
  END IF;

  RETURN NEW;
END
$$;

DROP TRIGGER IF EXISTS trg_clients_verify ON public.clients;
CREATE TRIGGER trg_clients_verify
BEFORE INSERT OR UPDATE ON public.clients
FOR EACH ROW EXECUTE FUNCTION public.ensure_client_phone_verified();

-- Ensure helper email and phone are verified and match auth.users
CREATE OR REPLACE FUNCTION public.ensure_helper_verified()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  ok BOOLEAN;
BEGIN
  SELECT (u.email = NEW.email) AND (u.email_confirmed_at IS NOT NULL)
      AND (u.phone = NEW.phone) AND (u.phone_confirmed_at IS NOT NULL)
    INTO ok
  FROM auth.users u
  WHERE u.id = NEW.id
  LIMIT 1;

  IF NOT COALESCE(ok, FALSE) THEN
    RAISE EXCEPTION 'Email and phone must both be verified and match auth.users';
  END IF;

  RETURN NEW;
END
$$;

DROP TRIGGER IF EXISTS trg_helpers_verify ON public.helpers;
CREATE TRIGGER trg_helpers_verify
BEFORE INSERT OR UPDATE ON public.helpers
FOR EACH ROW EXECUTE FUNCTION public.ensure_helper_verified();

-- RLS
ALTER TABLE public.clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.helpers ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS clients_self_select ON public.clients;
CREATE POLICY clients_self_select ON public.clients
  FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS clients_self_insert ON public.clients;
CREATE POLICY clients_self_insert ON public.clients
  FOR INSERT WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS clients_self_update ON public.clients;
CREATE POLICY clients_self_update ON public.clients
  FOR UPDATE USING (auth.uid() = id) WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS helpers_self_select ON public.helpers;
CREATE POLICY helpers_self_select ON public.helpers
  FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS helpers_self_insert ON public.helpers;
CREATE POLICY helpers_self_insert ON public.helpers
  FOR INSERT WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS helpers_self_update ON public.helpers;
CREATE POLICY helpers_self_update ON public.helpers
  FOR UPDATE USING (auth.uid() = id) WITH CHECK (auth.uid() = id);


CREATE OR REPLACE FUNCTION increment_post_count(user_uuid UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE public.clients 
    SET number_of_posts = number_of_posts + 1
    WHERE id = user_uuid;
    
    RETURN FOUND;
END;
$$;

COMMIT;
