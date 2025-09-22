-- Migration: Add distance calculation function for task search
BEGIN;

-- Add indexes for better search performance
CREATE INDEX IF NOT EXISTS idx_tasks_status_completed_at ON public.tasks(completed_at);
CREATE INDEX IF NOT EXISTS idx_tasks_location_type ON public.tasks(location_type);
CREATE INDEX IF NOT EXISTS idx_tasks_hourly_rate ON public.tasks(hourly_rate);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON public.tasks(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_zip_code ON public.tasks(zip_code);

-- Add indexes for helper search performance
CREATE INDEX IF NOT EXISTS idx_helpers_college ON public.helpers(college);
CREATE INDEX IF NOT EXISTS idx_helpers_graduation_year ON public.helpers(graduation_year);
CREATE INDEX IF NOT EXISTS idx_helpers_zip_code ON public.helpers(zip_code);
CREATE INDEX IF NOT EXISTS idx_helpers_created_at ON public.helpers(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_helpers_text_search ON public.helpers 
USING gin(to_tsvector('english', first_name || ' ' || last_name || ' ' || bio || ' ' || college));

-- Function to calculate distance between two points using Haversine formula
CREATE OR REPLACE FUNCTION public.calculate_distance(
    lat1 DECIMAL,
    lng1 DECIMAL,
    lat2 DECIMAL,
    lng2 DECIMAL
)
RETURNS DECIMAL
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    R DECIMAL := 3959; -- Earth's radius in miles
    dlat DECIMAL;
    dlng DECIMAL;
    a DECIMAL;
    c DECIMAL;
BEGIN
    -- Convert to radians
    dlat := radians(lat2 - lat1);
    dlng := radians(lng2 - lng1);
    
    -- Haversine formula
    a := sin(dlat/2) * sin(dlat/2) + 
         cos(radians(lat1)) * cos(radians(lat2)) * 
         sin(dlng/2) * sin(dlng/2);
    c := 2 * atan2(sqrt(a), sqrt(1-a));
    
    RETURN R * c;
END;
$$;

-- Function to count tasks matching search criteria (efficient)
CREATE OR REPLACE FUNCTION public.count_tasks_matching_criteria(
    search_zip_code TEXT,
    search_query TEXT DEFAULT NULL,
    search_location_type TEXT DEFAULT NULL,
    min_hourly_rate DECIMAL DEFAULT NULL,
    max_hourly_rate DECIMAL DEFAULT NULL
)
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    task_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO task_count
    FROM public.tasks t
    WHERE 
        -- Only return tasks that are not completed (completed_at IS NULL)
        t.completed_at IS NULL
        -- Query filter
        AND (
            search_query IS NULL 
            OR t.title ILIKE '%' || search_query || '%'
            OR t.description ILIKE '%' || search_query || '%'
        )
        -- Location type filter
        AND (
            search_location_type IS NULL 
            OR t.location_type = search_location_type
        )
        -- Hourly rate filter
        AND (
            min_hourly_rate IS NULL 
            OR t.hourly_rate >= min_hourly_rate
        )
        AND (
            max_hourly_rate IS NULL 
            OR t.hourly_rate <= max_hourly_rate
        );
    
    RETURN task_count;
END;
$$;

CREATE OR REPLACE FUNCTION public.get_tasks_with_distance(
    search_zip_code TEXT,
    search_query TEXT DEFAULT NULL,
    search_location_type TEXT DEFAULT NULL,
    min_hourly_rate DECIMAL DEFAULT NULL,
    max_hourly_rate DECIMAL DEFAULT NULL,
    search_limit INTEGER DEFAULT 20,
    search_offset INTEGER DEFAULT 0
)
RETURNS TABLE(
    id UUID,
    client_id UUID,
    hourly_rate REAL,
    title TEXT,
    dates JSONB,
    location_type TEXT,
    zip_code TEXT,
    description TEXT,
    tools_info TEXT,
    public_transport_info TEXT,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    distance DECIMAL,
    client JSON
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    search_lat DECIMAL;
    search_lng DECIMAL;
BEGIN
    -- Get coordinates for search zip code
    SELECT lat, lng INTO search_lat, search_lng
    FROM public.zip_codes as zc
    WHERE zc.zip_code = search_zip_code;

    RETURN QUERY
    SELECT 
        t.id,
        t.client_id,
        t.hourly_rate,
        t.title,
        t.dates,
        t.location_type,
        t.zip_code,
        t.description,
        t.tools_info,
        t.public_transport_info,
        t.completed_at,
        t.created_at,
        t.updated_at,
        CASE 
            WHEN search_lat IS NOT NULL AND search_lng IS NOT NULL 
                 AND zc.lat IS NOT NULL AND zc.lng IS NOT NULL
            THEN public.calculate_distance(search_lat, search_lng, zc.lat, zc.lng)
            ELSE NULL
        END AS distance,
        json_build_object(
            'id', c.id,
            'first_name', c.first_name,
            'last_name', c.last_name,
            'pfp_url', c.pfp_url
        ) as client
    FROM public.tasks t
    LEFT JOIN public.zip_codes zc ON t.zip_code = zc.zip_code
    JOIN public.clients c ON t.client_id = c.id
    WHERE 
        t.completed_at IS NULL
        AND (
            search_query IS NULL 
            OR t.title ILIKE '%' || search_query || '%'
            OR t.description ILIKE '%' || search_query || '%'
        )
        AND (
            search_location_type IS NULL 
            OR t.location_type = search_location_type
        )
        AND (
            min_hourly_rate IS NULL 
            OR t.hourly_rate >= min_hourly_rate
        )
        AND (
            max_hourly_rate IS NULL 
            OR t.hourly_rate <= max_hourly_rate
        )
    ORDER BY 
        -- Remote tasks first (no zip_code or explicit remote location_type)
        CASE WHEN t.location_type = 'remote' OR t.zip_code IS NULL THEN 0 ELSE 1 END,
        -- Among non-remote: tasks with computed distance first
        CASE 
            WHEN search_lat IS NOT NULL AND search_lng IS NOT NULL AND zc.lat IS NOT NULL AND zc.lng IS NOT NULL THEN 0
            ELSE 1
        END,
        -- Then nearest first where distance is available
        distance ASC NULLS LAST,
        -- Finally newest
        t.created_at DESC
    LIMIT search_limit
    OFFSET search_offset;
END;
$$;

-- Function to count helpers matching search criteria
CREATE OR REPLACE FUNCTION public.count_helpers_matching_criteria(
    search_query TEXT DEFAULT NULL,
    search_college TEXT DEFAULT NULL,
    search_graduation_year INTEGER DEFAULT NULL,
    search_zip_code TEXT DEFAULT NULL
)
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    helper_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO helper_count
    FROM public.helpers h
    WHERE 
        -- Text search in name, bio, and college
        (search_query IS NULL 
         OR to_tsvector('english', h.first_name || ' ' || h.last_name || ' ' || h.bio || ' ' || h.college) @@ plainto_tsquery('english', search_query))
        -- College filter
        AND (search_college IS NULL OR h.college ILIKE '%' || search_college || '%')
        -- Graduation year filter
        AND (search_graduation_year IS NULL OR h.graduation_year = search_graduation_year)
        -- Zip code filter
        AND (search_zip_code IS NULL OR h.zip_code = search_zip_code);
    
    RETURN helper_count;
END;
$$;

-- Function to get helpers matching search criteria
CREATE OR REPLACE FUNCTION public.get_helpers_matching_criteria(
    search_query TEXT DEFAULT NULL,
    search_college TEXT DEFAULT NULL,
    search_graduation_year INTEGER DEFAULT NULL,
    search_zip_code TEXT DEFAULT NULL,
    search_limit INTEGER DEFAULT 20,
    search_offset INTEGER DEFAULT 0
)
RETURNS TABLE(
    id UUID,
    email TEXT,
    phone TEXT,
    first_name TEXT,
    last_name TEXT,
    pfp_url TEXT,
    college TEXT,
    bio TEXT,
    graduation_year INTEGER,
    zip_code TEXT,
    number_of_applications INTEGER,
    invited_count INTEGER,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        h.id,
        h.email,
        h.phone,
        h.first_name,
        h.last_name,
        h.pfp_url,
        h.college,
        h.bio,
        h.graduation_year,
        h.zip_code,
        h.number_of_applications,
        h.invited_count,
        h.created_at,
        h.updated_at
    FROM public.helpers h
    WHERE 
        -- Text search in name, bio, and college
        (search_query IS NULL 
         OR to_tsvector('english', h.first_name || ' ' || h.last_name || ' ' || h.bio || ' ' || h.college) @@ plainto_tsquery('english', search_query))
        -- College filter
        AND (search_college IS NULL OR h.college ILIKE '%' || search_college || '%')
        -- Graduation year filter
        AND (search_graduation_year IS NULL OR h.graduation_year = search_graduation_year)
        -- Zip code filter
        AND (search_zip_code IS NULL OR h.zip_code = search_zip_code)
    ORDER BY 
        -- Order by relevance (text search rank) then by creation date
        CASE 
            WHEN search_query IS NOT NULL THEN 
                ts_rank(to_tsvector('english', h.first_name || ' ' || h.last_name || ' ' || h.bio || ' ' || h.college), plainto_tsquery('english', search_query))
            ELSE 0
        END DESC,
        h.created_at DESC
    LIMIT search_limit
    OFFSET search_offset;
END;
$$;

-- Function to increment helper application count
CREATE OR REPLACE FUNCTION public.increment_helper_application_count(helper_uuid UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    current_count INTEGER;
BEGIN
    -- Get current application count
    SELECT COALESCE(number_of_applications, 0) INTO current_count
    FROM public.helpers
    WHERE id = helper_uuid
    LIMIT 1;
    
    -- If helper not found, return false
    IF current_count IS NULL THEN
        RETURN FALSE;
    END IF;
    
    -- Update with new count
    UPDATE public.helpers
    SET 
        number_of_applications = current_count + 1,
        updated_at = now()
    WHERE id = helper_uuid;
    
    RETURN TRUE;
END;
$$;

COMMIT;
