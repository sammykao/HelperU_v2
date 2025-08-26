# Helper Migration Script v2

This script migrates helper data from the old helper schema to the new HelperU_v2 schema with proper auth user management.

## 🎯 **What This Script Does:**

1. **Exports old helper data** from source database
2. **Creates/updates auth users** in new database with proper verification timestamps
3. **Migrates helper profiles** to new schema structure
4. **Handles duplicates** with upsert logic
5. **Sets verification timestamps** to current time for migrated users

## 📋 **Prerequisites:**

1. **Python 3.8+** installed
2. **Database access** to both old and new Supabase projects
3. **Environment variables** configured in `supabase.env`

## 🔧 **Setup:**

1. **Install dependencies:**
   ```bash
   cd data_migration
   pip install -r requirements_migration.txt
   ```

2. **Configure environment variables** in `supabase.env`:
   ```bash
   # OLD Supabase Project (source)
   OLD_USER=your_old_db_user
   OLD_PASSWORD=your_old_db_password
   OLD_HOST=your_old_db_host
   OLD_PORT=5432
   OLD_DBNAME=postgres
   
   # NEW Supabase Project (destination)
   NEW_USER=your_new_db_user
   NEW_PASSWORD=your_new_db_password
   NEW_HOST=your_new_db_host
   NEW_PORT=5432
   NEW_DBNAME=postgres
   
   # SSL Configuration
   SSL_MODE=require
   ```

## 🚀 **Usage:**

### **Dry Run (Recommended First):**
```bash
python migrate_helpers_v2.py --dry-run
```
This shows what would be migrated without making changes.

### **Actual Migration:**
```bash
python migrate_helpers_v2.py
```

### **Verbose Logging:**
```bash
python migrate_helpers_v2.py --verbose
```

## 📊 **Migration Process:**

### **Step 1: Data Extraction**
- Fetches all helper data from old `helpers` table
- Includes auth user verification status
- Handles JSON fields (education, availability, payout_methods)

### **Step 2: Auth User Management**
- **Creates new auth users** if they don't exist
- **Updates existing auth users** with verification timestamps
- Sets `email_confirmed_at` and `phone_confirmed_at` to current time
- Normalizes phone numbers to E.164 format

### **Step 3: Helper Data Migration**
- Maps old fields to new schema structure
- Handles missing required fields with sensible defaults
- Uses upsert logic to handle duplicates
- Preserves creation timestamps

## 🔄 **Schema Mapping:**

| Old Field | New Field | Notes |
|-----------|-----------|-------|
| `id` | `id` | Primary key (references auth.users) |
| `auth_id` | N/A | Used to create auth user |
| `first_name` | `first_name` | Required field |
| `last_name` | `last_name` | Required field |
| `email` | `email` | Required, must be unique |
| `phone` | `phone` | Required, must be unique, normalized to E.164 |
| `college` | `college` | Required field |
| `bio` | `bio` | Required field |
| `graduation_year` | `graduation_year` | Required, validated as integer |
| `zip_code` | `zip_code` | Required field |
| `profile_image_url` | `pfp_url` | Optional profile picture URL |
| `created_at` | `created_at` | Preserved from original |
| `updated_at` | `updated_at` | Set to current time |

## ⚠️ **Important Notes:**

1. **Verification Status**: All migrated users will have their email and phone marked as verified with current timestamps
2. **Phone Normalization**: Phone numbers are automatically converted to E.164 format (+1XXXXXXXXXX)
3. **Duplicate Handling**: Uses PostgreSQL's `ON CONFLICT` for upsert operations
4. **Required Fields**: Missing required fields get sensible defaults
5. **Auth User Creation**: Creates auth users with proper metadata for Supabase

## 📈 **Migration Statistics:**

The script provides detailed statistics:
- Total helpers found
- Successfully migrated helpers
- Auth users created/updated
- Error counts by category
- Detailed error logs

## 🚨 **Error Handling:**

- **Missing email/phone**: Helper skipped, logged as warning
- **Auth user creation failure**: Helper skipped, logged as error
- **Data migration failure**: Individual helper skipped, logged as error
- **Database connection issues**: Script exits with error code

## 🔍 **Troubleshooting:**

1. **Connection Issues**: Check environment variables and network access
2. **Permission Errors**: Ensure database user has INSERT/UPDATE permissions
3. **Schema Mismatches**: Verify new database has correct table structure
4. **Data Validation**: Check logs for specific field validation errors

## 📝 **Log Files:**

- **Console output**: Real-time migration progress
- **Log file**: `helper_migration_v2.log` with detailed information
- **Error tracking**: Categorized error counts and descriptions

## ✅ **Success Criteria:**

Migration is considered successful when:
- All valid helpers are processed
- Auth users are created/updated with verification timestamps
- Helper profiles are inserted into new schema
- No critical errors prevent the process from completing

## 🔄 **Rollback:**

If migration needs to be undone:
1. **Delete migrated helpers** from new database
2. **Delete created auth users** from new database
3. **Restore from backup** if necessary

## 📞 **Support:**

For issues or questions:
1. Check the log files for detailed error information
2. Verify environment variables and database connections
3. Ensure new database schema matches expected structure
4. Review error categories in migration statistics
