# Migrated Account Test Script

This test script validates that your migrated account with phone number `+16108883335` is working correctly with your authentication and profile endpoints.

## Setup

1. **Install dependencies:**
   ```bash
   cd tests
   pip install -r requirements.txt
   ```

2. **Ensure your API is running:**
   - Default: `http://localhost:8000`
   - Override with `API_BASE_URL` environment variable

## Usage

### Test Complete Flow (Recommended)

This tests the entire authentication and profile flow:

```bash
python test_migrated_account.py test-flow
```

**What it does:**
1. Sends signin OTP to `+16108883335`
2. Prompts you to enter the OTP code from your phone
3. Verifies the OTP and gets authentication tokens
4. Retrieves the user profile using the access token

### Test Individual Endpoints

Test endpoints separately without full authentication flow:

```bash
python test_migrated_account.py test-endpoints
```

### Manual OTP Verification

If you already have an OTP code:

```bash
python test_migrated_account.py verify-otp YOUR_OTP_CODE
```

### Get Profile (After Authentication)

Get profile after you've already authenticated:

```bash
python test_migrated_account.py get-profile
```

## Expected Results

### Successful Migration Should Show:

1. **OTP Sent Successfully** - HTTP 200 response
2. **OTP Verification Success** - HTTP 200 with tokens
3. **Profile Retrieved** - HTTP 200 with user profile data

### What to Look For:

- ✅ **User ID**: Should match the migrated `auth_id`
- ✅ **Phone Number**: Should be `+16108883335` (normalized)
- ✅ **Profile Data**: Should show client profile information
- ✅ **Authentication**: Should work with phone-only auth

## Troubleshooting

### Common Issues:

1. **"Phone number not found"** - Migration may have failed
2. **"Invalid OTP"** - Check if phone number format matches
3. **"Unauthorized"** - Authentication tokens not working
4. **"Profile not found"** - Client record migration failed

### Debug Steps:

1. Check if the account exists in your new database:
   ```sql
   SELECT * FROM auth.users WHERE phone = '16108883335';
   SELECT * FROM public.clients WHERE phone = '16108883335';
   ```

2. Verify phone number format matches between tables
3. Check if `phone_confirmed_at` is set in `auth.users`

## Phone Number Format

The script uses `+16108883335` format, which should match:
- **Input format**: `+1 (610) 888-3335`
- **Database storage**: `16108883335` (11 digits)
- **API format**: `+16108883335` (E.164)

## Environment Variables

- `API_BASE_URL`: Override default API URL
- `TEST_PHONE`: Override default test phone number

## Example Output

```
🚀 Testing Complete Migrated Account Flow
==================================================

📋 Step 1: Send Signin OTP
📱 Sending signin OTP to +16108883335...
   URL: http://localhost:8000/api/v1/auth/client/signin
   Payload: {
     "phone": "+16108883335"
   }
   Response: HTTP 200
   Data: {
     "success": true,
     "message": "OTP sent successfully"
   }

📋 Step 2: Enter OTP Code
   Check your phone +16108883335 for the OTP code
   Enter OTP code: 123456

📋 Step 3: Verify OTP
🔐 Verifying OTP token 123456 for +16108883335...
   Response: HTTP 200
   Data: {
     "success": true,
     "user_id": "uuid-here",
     "access_token": "token-here",
     "refresh_token": "token-here",
     "message": "Client verified successfully"
   }
   ✅ Stored tokens - User ID: uuid-here

📋 Step 4: Get User Profile
👤 Getting profile for user uuid-here...
   Response: HTTP 200
   Data: {
     "success": true,
     "profile_status": {...},
     "profile": {...}
   }

🎉 Complete flow test successful!
   User ID: uuid-here
   Access Token: ✅
   Refresh Token: ✅
```
