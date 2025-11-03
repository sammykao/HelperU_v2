from supabase import create_client, Client

SUPABASE_URL = "https://afcomoghfkzsahnrdrxs.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFmY29tb2doZmt6c2FobnJkcnhzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ4NDY1ODQsImV4cCI6MjA3MDQyMjU4NH0.LWNgEmO3_MrVpq3p-6Abu8ZlIgk4LU22lba9Zw4vEb0"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

response = supabase.auth.sign_in_with_otp({"phone": "+17038687914 "})
print(response)
