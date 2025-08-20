BEGIN;

-- Add subscription plan types
CREATE TYPE subscription_plan AS ENUM ('free', 'premium');

-- Add subscription status types
CREATE TYPE subscription_status AS ENUM ('active', 'canceled', 'past_due', 'unpaid', 'trialing');

-- Create subscriptions table
CREATE TABLE IF NOT EXISTS public.subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  stripe_subscription_id TEXT UNIQUE,
  stripe_customer_id TEXT,
  plan subscription_plan NOT NULL DEFAULT 'free',
  status subscription_status NOT NULL DEFAULT 'active',
  current_period_start TIMESTAMPTZ,
  current_period_end TIMESTAMPTZ,
  cancel_at_period_end BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create subscription_events table for webhook tracking
CREATE TABLE IF NOT EXISTS public.subscription_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  stripe_event_id TEXT UNIQUE NOT NULL,
  event_type TEXT NOT NULL,
  subscription_id UUID REFERENCES public.subscriptions(id) ON DELETE CASCADE,
  data JSONB NOT NULL,
  processed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Add monthly post count tracking for free users
CREATE TABLE IF NOT EXISTS public.monthly_post_counts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  year_month TEXT NOT NULL, -- Format: '2024-01'
  post_count INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(user_id, year_month)
);

-- Add indexes for performance
CREATE INDEX idx_subscriptions_user_id ON public.subscriptions(user_id);
CREATE INDEX idx_subscriptions_stripe_subscription_id ON public.subscriptions(stripe_subscription_id);
CREATE INDEX idx_subscription_events_stripe_event_id ON public.subscription_events(stripe_event_id);
CREATE INDEX idx_monthly_post_counts_user_year_month ON public.monthly_post_counts(user_id, year_month);

-- Add updated_at trigger for subscriptions
DROP TRIGGER IF EXISTS set_subscriptions_updated_at ON public.subscriptions;
CREATE TRIGGER set_subscriptions_updated_at
BEFORE UPDATE ON public.subscriptions
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Add updated_at trigger for monthly_post_counts
DROP TRIGGER IF EXISTS set_monthly_post_counts_updated_at ON public.monthly_post_counts;
CREATE TRIGGER set_monthly_post_counts_updated_at
BEFORE UPDATE ON public.monthly_post_counts
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Function to get current user's post limit
CREATE OR REPLACE FUNCTION public.get_user_post_limit(user_uuid UUID)
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  user_plan subscription_plan;
  current_month TEXT;
  monthly_count INTEGER;
BEGIN
  -- Get current month in YYYY-MM format
  current_month := to_char(now(), 'YYYY-MM');
  
  -- Get user's subscription plan
  SELECT plan INTO user_plan
  FROM public.subscriptions
  WHERE user_id = user_uuid
    AND status = 'active'
  ORDER BY created_at DESC
  LIMIT 1;
  
  -- If no active subscription, default to free
  IF user_plan IS NULL THEN
    user_plan := 'free';
  END IF;
  
  -- Return appropriate limit based on plan
  IF user_plan = 'premium' THEN
    RETURN 999999; -- Unlimited for premium users
  ELSE
    -- For free users, get current month's count
    SELECT COALESCE(post_count, 0) INTO monthly_count
    FROM public.monthly_post_counts
    WHERE user_id = user_uuid AND year_month = current_month;
    
    -- Free users get 1 post per month
    RETURN GREATEST(1 - monthly_count, 0);
  END IF;
END
$$;

-- Function to increment monthly post count
CREATE OR REPLACE FUNCTION public.increment_monthly_post_count(user_uuid UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  current_month TEXT;
  current_count INTEGER;
BEGIN
  -- Get current month in YYYY-MM format
  current_month := to_char(now(), 'YYYY-MM');
  
  -- Get current count for this month
  SELECT COALESCE(post_count, 0) INTO current_count
  FROM public.monthly_post_counts
  WHERE user_id = user_uuid AND year_month = current_month;
  
  -- Insert or update the count
  INSERT INTO public.monthly_post_counts (user_id, year_month, post_count)
  VALUES (user_uuid, current_month, current_count + 1)
  ON CONFLICT (user_id, year_month)
  DO UPDATE SET post_count = current_count + 1;
  
  RETURN TRUE;
END
$$;

-- Enable RLS on new tables
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscription_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.monthly_post_counts ENABLE ROW LEVEL SECURITY;

-- RLS policies for subscriptions
CREATE POLICY subscriptions_self_select ON public.subscriptions
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY subscriptions_self_insert ON public.subscriptions
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY subscriptions_self_update ON public.subscriptions
  FOR UPDATE USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- RLS policies for monthly_post_counts
CREATE POLICY monthly_post_counts_self_select ON public.monthly_post_counts
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY monthly_post_counts_self_insert ON public.monthly_post_counts
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY monthly_post_counts_self_update ON public.monthly_post_counts
  FOR UPDATE USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- Allow service role to manage subscription_events (for webhooks)
CREATE POLICY subscription_events_service_role ON public.subscription_events
  FOR ALL USING (auth.role() = 'service_role');

COMMIT;
