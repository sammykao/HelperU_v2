# Supabase-to-Supabase Client Migration Guide

This guide explains how to migrate client data between two Supabase projects using the provided migration script.

## 🎯 **What You Need**

### **From Your Old Supabase Project:**
1. **Project URL** (e.g., `https://abc123.supabase.co`)
2. **Service Role Key** (not the anon key!)

### **From Your New HelperU_v2 Supabase Project:**
1. **Project URL** (e.g., `https://xyz789.supabase.co`)
2. **Service Role Key** (not the anon key!)

## 🔑 **Getting Your Supabase Credentials**

### **Step 1: Get Project URLs**
1. Go to your Supabase dashboard
2. Select your project
3. Copy the URL from the address bar or from Project Settings → General

### **Step 2: Get Service Role Keys**
1. In your Supabase dashboard, go to **Settings** → **API**
2. Look for **Project API keys** section
3. Copy the **`service_role`** key (NOT the `anon` key!)
4. The service role key looks like: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

⚠️ **Important**: Use the `service_role` key, not the `anon` key. The service role key has admin privileges needed for migration.

## 🚀 **Running the Migration**

### **Install Dependencies**
```bash
cd data_migration
pip install -r requirements.txt
```

### **Basic Migration Command**
```bash
python migrate_clients_supabase.py \
  --old-project-url "https://abc123.supabase.co" \
  --old-service-key "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  --new-project-url "https://xyz789.supabase.co" \
  --new-service-key "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### **Dry Run (Test Mode)**
```bash
python migrate_clients_supabase.py \
  --old-project-url "https://abc123.supabase.co" \
  --old-service-key "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  --new-project-url "https://xyz789.supabase.co" \
  --new-service-key "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  --dry-run
```

### **Validation Only**
```bash
python migrate_clients_supabase.py \
  --old-project-url "https://abc123.supabase.co" \
  --old-service-key "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  --new-project-url "https://xyz789.supabase.co" \
  --new-service-key "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  --validate-only
```

## 🔧 **How It Works**

### **1. Connection Setup**
The script automatically converts your Supabase URLs to PostgreSQL connection strings:
- `https://abc123.supabase.co` → `postgresql://postgres:[service_key]@abc123.supabase.co:5432/postgres`

### **2. SSL Connection**
- Automatically enables SSL (`sslmode=require`) as required by Supabase
- Uses your service role key as the password

### **3. Data Migration**
- Connects to both Supabase projects simultaneously
- Migrates client data from old to new
- Creates auth users in the new project
- Preserves all timestamps and relationships

## 📊 **What Gets Migrated**

| Data Type | Source | Destination | Notes |
|-----------|--------|-------------|-------|
| **Client Profiles** | `public.clients` (old) | `public.clients` (new) | All profile data |
| **Auth Users** | `auth.users` (old) | `auth.users` (new) | Phone verification status |
| **Task Counts** | `public.tasks` (old) | `number_of_posts` (new) | Calculated from existing tasks |
| **Stripe Data** | `stripe_customer_id` (old) | `public.subscriptions` (new) | Free plan by default |
| **Timestamps** | All tables (old) | All tables (new) | Preserved exactly |

## 🛡️ **Safety Features**

### **Transaction Safety**
- Each client migration is wrapped in a transaction
- Rollback on any failure
- Individual client failures don't stop the entire migration

### **Conflict Handling**
- Uses `ON CONFLICT DO NOTHING` for auth users
- Uses `ON CONFLICT DO UPDATE` for client data
- Safe to run multiple times

### **Validation**
- Counts migrated records vs. expected
- Verifies auth user creation
- Reports detailed statistics

## 📝 **Migration Process**

### **Step 1: Data Retrieval**
```
✅ Connecting to old Supabase project...
✅ Connecting to new Supabase project...
✅ Found 150 clients in old Supabase project
```

### **Step 2: Client Processing**
```
Processing client 1/150: 550e8400-e29b-41d4-a716-446655440000
Processing client 2/150: 6ba7b810-9dad-11d1-80b4-00c04fd430c8
...
```

### **Step 3: Final Statistics**
```
============================================================
SUPABASE CLIENT MIGRATION STATISTICS
============================================================
Clients found in old Supabase: 150
Clients successfully migrated: 148
Auth users created: 148

No errors encountered! ✅
============================================================
```

## 🔍 **Troubleshooting**

### **Common Issues**

#### **1. Connection Errors**
```
Failed to connect to Supabase projects: connection to server at "abc123.supabase.co" failed
```
**Solution**: Verify your project URLs and service role keys

#### **2. Permission Errors**
```
permission denied for table clients
```
**Solution**: Ensure you're using the `service_role` key, not `anon` key

#### **3. SSL Errors**
```
SSL connection has been closed unexpectedly
```
**Solution**: The script automatically handles SSL - check your network/firewall

### **Debug Mode**
Set logging level to DEBUG for more detailed information:
```python
# In the script, change:
logging.basicConfig(level=logging.INFO, ...)
# To:
logging.basicConfig(level=logging.DEBUG, ...)
```

## 📋 **Pre-Migration Checklist**

- [ ] **Backup your old database** (Supabase has automatic backups, but verify)
- [ ] **Verify new database schema** is ready (run your migrations first)
- [ ] **Test with dry run** before actual migration
- [ ] **Check service role keys** have proper permissions
- [ ] **Verify network access** to both Supabase projects

## 🧪 **Testing the Migration**

### **1. Dry Run First**
```bash
python migrate_clients_supabase.py \
  --old-project-url "https://abc123.supabase.co" \
  --old-service-key "your_old_key" \
  --new-project-url "https://xyz789.supabase.co" \
  --new-service-key "your_new_key" \
  --dry-run
```

### **2. Validate Existing Migration**
```bash
python migrate_clients_supabase.py \
  --old-project-url "https://abc123.supabase.co" \
  --old-service-key "your_old_key" \
  --new-project-url "https://xyz789.supabase.co" \
  --new-service-key "your_new_key" \
  --validate-only
```

## 🔄 **Post-Migration Steps**

### **1. Verify Data**
- Check client counts match
- Verify auth users were created
- Test login with migrated accounts

### **2. Update Application**
- Point your app to the new Supabase project
- Test all functionality
- Monitor for any issues

### **3. Clean Up (Optional)**
- Keep old project for backup
- Or delete after confirming everything works

## 💡 **Pro Tips**

1. **Run during low-traffic hours** to minimize impact
2. **Use dry-run first** to catch any issues
3. **Monitor the logs** during migration
4. **Keep both projects** until you're 100% confident
5. **Test with a few users** before full migration

## 🆘 **Getting Help**

If you encounter issues:

1. **Check the logs** in `client_migration_supabase.log`
2. **Verify credentials** are correct
3. **Ensure both projects** are accessible
4. **Check Supabase status** at https://status.supabase.com
5. **Review error messages** for specific issues

---

**Remember**: Always backup your data before running any migration! Supabase makes this easy with automatic backups, but it's good practice to verify.
