# Task Migration Script v2

This script migrates task data from the old task schema to the new HelperU_v2 schema with proper field mapping and transformations.

## 🎯 **What This Script Does:**

1. **Exports old task data** from source database
2. **Maps and transforms fields** according to new schema requirements
3. **Looks up client IDs** by email and phone in the new database
4. **Handles data transformations** for dates, descriptions, and other fields
5. **Sets appropriate defaults** for missing data

## 📋 **Prerequisites:**

1. **Python 3.8+** installed
2. **Database access** to both old and new Supabase projects
3. **Environment variables** configured in `supabase.env`
4. **Client migration completed** (tasks need valid client IDs)

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
python migrate_tasks_v2.py --dry-run
```
This shows what would be migrated without making changes.

### **Actual Migration:**
```bash
python migrate_tasks_v2.py
```

### **Verbose Logging:**
```bash
python migrate_tasks_v2.py --verbose
```

## 📊 **Migration Process:**

### **Step 1: Data Extraction**
- Fetches all task data from old `tasks` table
- Includes all fields for proper mapping

### **Step 2: Client ID Lookup**
- **Primary**: Looks up client ID by email in new `clients` table
- **Fallback**: If email fails, looks up by normalized phone number
- **Skip**: If neither lookup succeeds, task is skipped

### **Step 3: Field Transformations**
- Maps old fields to new schema structure
- Applies data transformations as specified
- Handles missing data with appropriate defaults

## 🔄 **Field Mapping:**

| Old Field | New Field | Transformation |
|-----------|-----------|----------------|
| `id` | `id` | Direct mapping |
| `title` | `title` | Direct mapping |
| `description` | `description` | Enhanced with duration and location info |
| `hourly_rate` | `hourly_rate` | Converted from cents to dollars (÷100) |
| `datetime` | `dates` | Parsed to JSON array with single date |
| `duration` | `description` | Appended as "Duration: {duration}" |
| `location_description` | `description` | Appended as "Location info: {location_desc}" |
| `tools_vehicle_required` + `tools_vehicle_description` | `tools_info` | Combined with newlines |
| `public_transportation_accessible` + `public_transportation_description` | `public_transport_info` | Combined with newlines |
| `location_type` | `location_type` | Direct mapping, set to 'remote' if no zip_code |
| `zip_code` | `zip_code` | Direct mapping, set to NULL if empty |
| `completed` | `completed_at` | Set to created_at timestamp if true, NULL if false |
| `created_at` | `created_at` | Direct mapping |
| N/A | `updated_at` | Set to current timestamp |
| N/A | `client_id` | Looked up from clients table by email/phone |

## ⚠️ **Important Notes:**

1. **Client Dependency**: Tasks require valid client IDs - run client migration first
2. **Email/Phone Lookup**: Tasks are matched to clients by email (primary) or phone (fallback)
3. **Location Logic**: If no zip_code, location_type is automatically set to 'remote'
4. **Rate Conversion**: Hourly rates are converted from cents to dollars
5. **Description Enhancement**: Additional info is appended to description field
6. **Date Parsing**: Datetime strings are parsed to ISO format in dates array

## 📈 **Migration Statistics:**

The script provides detailed statistics:
- Total tasks found
- Successfully migrated tasks
- Tasks skipped (client lookup failed)
- Client lookup failures
- Error counts by category
- Detailed error logs

## 🚨 **Error Handling:**

- **Client lookup failure**: Task skipped, logged as warning
- **Data validation errors**: Individual task skipped, logged as error
- **Database connection issues**: Script exits with error code
- **Transaction safety**: Each task migration is wrapped in a transaction

## 🔍 **Troubleshooting:**

1. **Client Lookup Issues**: Ensure client migration completed successfully
2. **Connection Issues**: Check environment variables and network access
3. **Permission Errors**: Ensure database user has INSERT/UPDATE permissions
4. **Schema Mismatches**: Verify new database has correct table structure
5. **Data Validation**: Check logs for specific field validation errors

## 📝 **Log Files:**

- **Console output**: Real-time migration progress
- **Log file**: `task_migration_v2.log` with detailed information
- **Error tracking**: Categorized error counts and descriptions

## ✅ **Success Criteria:**

Migration is considered successful when:
- All valid tasks are processed
- Client IDs are successfully looked up
- Task data is transformed and inserted into new schema
- No critical errors prevent the process from completing

## 🔄 **Rollback:**

If migration needs to be undone:
1. **Delete migrated tasks** from new database
2. **Restore from backup** if necessary

## 📞 **Support:**

For issues or questions:
1. Check the log files for detailed error information
2. Verify environment variables and database connections
3. Ensure client migration completed successfully
4. Review error categories in migration statistics

---

**Remember**: Always backup your data before running any migration! Run client migration first to ensure valid client IDs are available.
