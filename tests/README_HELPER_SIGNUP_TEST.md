# Helper Signup Flow Test Script

This test script validates the complete helper signup and verification flow in your HelperU backend.

## 🎯 **What It Tests:**

### **Complete Flow Test (`test-flow`):**
1. **Helper Signup** - Creates helper account with email + phone
2. **OTP Send** - Sends verification code to phone
3. **OTP Verification** - Verifies the code and gets auth tokens
4. **Profile Status Check** - Checks verification and profile completion status
5. **Profile Completion** - Completes helper profile with all required fields

### **Individual Endpoint Test (`test-endpoints`):**
- Tests each endpoint separately for debugging
- Allows you to skip certain steps

## 🚀 **Setup:**

1. **Install dependencies:**
   ```bash
   cd tests
   pip install -r requirements.txt
   ```

2. **Ensure your API server is running:**
   - Default: `http://localhost:8000`
   - Override with `API_BASE_URL` environment variable

3. **Update test credentials** in the script:
   ```python
   TEST_HELPER_EMAIL = "your.test@tufts.edu"  # Change this
   TEST_HELPER_PHONE = "+16108883335"          # Change this
   ```

## 📱 **Usage:**

### **Test Complete Flow (Recommended):**
```bash
python test_helper_signup_flow.py test-flow
```

**What happens:**
1. Creates helper account
2. Sends OTP to your phone
3. Prompts you to enter the OTP code
4. Verifies OTP and gets tokens
5. Checks profile status
6. Completes profile (if needed)

### **Test Individual Endpoints:**
```bash
python test_helper_signup_flow.py test-endpoints
```

**What happens:**
1. Tests each endpoint separately
2. Allows you to control the flow
3. Good for debugging specific issues

### **Custom Credentials:**
```bash
python test_helper_signup_flow.py test-flow --email "custom@harvard.edu" --phone "+15551234567"
```

## 🔍 **Expected Flow:**

### **Step 1: Helper Signup**
- **Endpoint**: `POST /api/v1/auth/helper/signup`
- **Payload**: `{"email": "...", "phone": "..."}`
- **Expected**: HTTP 200, user created in `auth.users`, OTP automatically sent to phone

### **Step 2: OTP Verification**
- **Endpoint**: `POST /api/v1/auth/helper/verify-otp`
- **Payload**: `{"phone": "...", "token": "..."}`
- **Expected**: HTTP 200, phone verified, tokens returned

### **Step 3: Profile Status**
- **Endpoint**: `GET /api/v1/auth/profile-status`
- **Headers**: `Authorization: Bearer {token}`
- **Expected**: HTTP 200, verification status returned

### **Step 4: Profile Completion**
- **Endpoint**: `POST /api/v1/auth/helper/complete-profile`
- **Headers**: `Authorization: Bearer {token}`
- **Expected**: HTTP 200, profile created in `public.helpers`

## 🚨 **Important Notes:**

### **Email Verification Required:**
- Helper signup creates account but **email is NOT verified**
- **Profile completion will FAIL** until email is verified
- Email verification happens via **Supabase email link** (not in this test)

### **Database Constraints:**
- **Phone verification** required for OTP flow
- **Email verification** required for profile completion
- **Both verifications** required before helper can complete profile

### **Test Data:**
- Uses sample profile data for testing
- Modify `profile_data` in the script for different test scenarios
- Ensure ZIP code exists in your `public.zip_codes` table

## 🧪 **Debugging:**

### **Common Issues:**
1. **"Email and phone must both be verified"** - Email not verified yet
2. **"Phone is not verified"** - OTP verification failed
3. **"Invalid or expired token"** - Token validation issue
4. **"ZIP code not found"** - ZIP code doesn't exist in database

### **Check Database:**
```sql
-- Check if helper exists
SELECT * FROM auth.users WHERE email = 'your.test@tufts.edu';

-- Check verification status
SELECT email_confirmed_at, phone_confirmed_at FROM auth.users WHERE email = 'your.test@tufts.edu';

-- Check if profile exists
SELECT * FROM public.helpers WHERE email = 'your.test@tufts.edu';
```

## 🎉 **Success Indicators:**

- ✅ **Helper signup**: HTTP 200, user_id returned, OTP automatically sent
- ✅ **OTP verification**: HTTP 200, user_id returned
- ✅ **Profile status**: HTTP 200, verification status shown
- ✅ **Profile completion**: HTTP 200, profile created

**The test will guide you through each step and show exactly what's happening at each endpoint!**
