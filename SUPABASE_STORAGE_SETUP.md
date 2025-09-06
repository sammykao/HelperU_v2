# Supabase Storage Configuration Guide

This guide will help you set up Supabase Storage for secure file uploads in your HelperU application.

## 1. Create Storage Bucket

### Step 1: Access Supabase Dashboard
1. Go to [supabase.com](https://supabase.com) and sign in
2. Select your HelperU project
3. Navigate to **Storage** in the left sidebar

### Step 2: Create New Bucket
1. Click **"New bucket"**
2. Configure the bucket:
   - **Name**: `uploads`
   - **Public**: ✅ **YES** (for profile pictures)
   - **File size limit**: `5 MB` (or your preferred limit)
   - **Allowed MIME types**: `image/jpeg,image/png,image/gif,image/webp`

3. Click **"Create bucket"**

## 2. Configure Storage Policies

### Step 1: Access Storage Policies
1. In the Storage section, click on your `uploads` bucket
2. Go to the **"Policies"** tab

### Step 2: Create Upload Policy
Create a policy that allows authenticated users to upload files:

```sql
-- Policy name: "Allow authenticated users to upload files"
-- Operation: INSERT
-- Target roles: authenticated

(user_id() IS NOT NULL)
```

### Step 3: Create Read Policy
Create a policy that allows public read access to uploaded files:

```sql
-- Policy name: "Allow public read access"
-- Operation: SELECT
-- Target roles: anon, authenticated

true
```

### Step 4: Create Update Policy (Optional)
If you want users to be able to update their own files:

```sql
-- Policy name: "Allow users to update their own files"
-- Operation: UPDATE
-- Target roles: authenticated

(auth.uid()::text = (storage.foldername(name))[1])
```

### Step 5: Create Delete Policy (Optional)
If you want users to be able to delete their own files:

```sql
-- Policy name: "Allow users to delete their own files"
-- Operation: DELETE
-- Target roles: authenticated

(auth.uid()::text = (storage.foldername(name))[1])
```

## 3. Environment Variables

### Frontend (.env.local)
Add these variables to your frontend environment:

```env
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

### Backend (.env)
Add these variables to your backend environment:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

## 4. Security Best Practices

### File Validation
The FileUpload component already includes:
- ✅ File size validation (5MB limit)
- ✅ MIME type validation (images only)
- ✅ Unique filename generation
- ✅ Organized folder structure (`profile-pictures/`)

### Additional Security Measures

#### 1. Enable RLS (Row Level Security)
```sql
-- Enable RLS on storage.objects table
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;
```

#### 2. Create Custom Storage Function (Optional)
For additional security, create a custom function:

```sql
CREATE OR REPLACE FUNCTION upload_profile_picture(
  file_name text,
  file_data bytea,
  file_type text
)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  file_path text;
  file_url text;
BEGIN
  -- Validate file type
  IF file_type NOT IN ('image/jpeg', 'image/png', 'image/gif', 'image/webp') THEN
    RAISE EXCEPTION 'Invalid file type';
  END IF;
  
  -- Generate unique file path
  file_path := 'profile-pictures/' || auth.uid()::text || '/' || file_name;
  
  -- Insert file into storage
  INSERT INTO storage.objects (bucket_id, name, owner, metadata)
  VALUES ('uploads', file_path, auth.uid(), jsonb_build_object('size', octet_length(file_data), 'mimetype', file_type));
  
  -- Return public URL
  SELECT public_url INTO file_url
  FROM storage.objects
  WHERE name = file_path;
  
  RETURN file_url;
END;
$$;
```

#### 3. Set Up File Cleanup (Optional)
Create a function to clean up orphaned files:

```sql
CREATE OR REPLACE FUNCTION cleanup_orphaned_files()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  -- Delete files older than 30 days that aren't referenced in user profiles
  DELETE FROM storage.objects
  WHERE bucket_id = 'uploads'
    AND created_at < NOW() - INTERVAL '30 days'
    AND name NOT IN (
      SELECT pfp_url FROM auth.clients WHERE pfp_url IS NOT NULL
      UNION
      SELECT pfp_url FROM auth.helpers WHERE pfp_url IS NOT NULL
    );
END;
$$;
```

## 5. Testing Your Setup

### Test Upload
1. Start your frontend application
2. Navigate to client or helper signup
3. Try uploading a profile picture
4. Verify the file appears in your Supabase Storage dashboard

### Test Security
1. Try uploading a non-image file (should fail)
2. Try uploading a file larger than 5MB (should fail)
3. Verify files are accessible via public URLs

## 6. Monitoring and Maintenance

### Storage Usage
- Monitor your storage usage in the Supabase dashboard
- Set up alerts for storage limits
- Consider implementing file compression for large images

### Performance Optimization
- Use CDN for faster file delivery
- Implement image resizing/compression
- Consider using Supabase Edge Functions for image processing

## 7. Troubleshooting

### Common Issues

#### "Storage bucket not found"
- Ensure the bucket name is exactly `uploads`
- Check that the bucket is public

#### "Policy violation"
- Verify RLS policies are correctly configured
- Check that users are properly authenticated

#### "File upload fails"
- Check file size and type restrictions
- Verify Supabase credentials are correct
- Check browser console for detailed error messages

### Debug Mode
Enable debug logging in your FileUpload component:

```typescript
// Add this to your FileUpload component for debugging
console.log('Supabase URL:', supabaseUrl);
console.log('File details:', { name: file.name, size: file.size, type: file.type });
```

## 8. Production Considerations

### Domain Configuration
- Set up custom domain for your Supabase project
- Configure CORS settings if needed
- Set up SSL certificates

### Backup Strategy
- Regular backups of your storage bucket
- Consider cross-region replication for critical files
- Implement disaster recovery procedures

### Cost Optimization
- Monitor storage usage and costs
- Implement file lifecycle policies
- Consider archiving old files to cheaper storage

---

## Quick Setup Checklist

- [ ] Create `uploads` bucket in Supabase
- [ ] Set bucket to public
- [ ] Configure storage policies (upload, read, update, delete)
- [ ] Add environment variables to frontend and backend
- [ ] Test file upload functionality
- [ ] Verify security policies work correctly
- [ ] Set up monitoring and alerts
- [ ] Configure production settings

Your Supabase Storage is now ready for secure file uploads! 🚀
