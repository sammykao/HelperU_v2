#!/usr/bin/env python3
"""
Helper Migration Script v2: Migrate from old helper schema to new HelperU_v2 schema
This script handles the migration of helper data with proper auth user creation and verification.
"""

import sys
import logging
import click
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('helper_migration_v2.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class HelperV2Migrator:
    """Handles the migration of helpers from old schema to new HelperU_v2 schema."""
    
    def __init__(self):
        """Initialize the migrator with environment variables."""
        # Load environment variables
        load_dotenv('supabase.env')
        
        self.old_conn = None
        self.new_conn = None
        self.migration_stats = {
            'helpers_found': 0,
            'helpers_migrated': 0,
            'auth_users_created': 0,
            'auth_users_updated': 0,
            'errors': [],
            'error_categories': {
                'duplicate_phone': 0,
                'duplicate_email': 0,
                'auth_user_creation': 0,
                'helper_migration': 0,
                'verification_update': 0,
                'other': 0
            }
        }
    
    def _get_old_connection_params(self) -> Dict[str, str]:
        """Get connection parameters for OLD project from environment variables."""
        return {
            'user': os.getenv("OLD_USER"),
            'password': os.getenv("OLD_PASSWORD"),
            'host': os.getenv("OLD_HOST"),
            'port': os.getenv("OLD_PORT"),
            'dbname': os.getenv("OLD_DBNAME"),
            'sslmode': os.getenv("SSL_MODE"),
            'connect_timeout': 30,
            'application_name': 'helper_migration_v2_script'
        }
    
    def _get_new_connection_params(self) -> Dict[str, str]:
        """Get connection parameters for NEW project from environment variables."""
        return {
            'user': os.getenv("NEW_USER"),
            'password': os.getenv("NEW_PASSWORD"),
            'host': os.getenv("NEW_HOST"),
            'port': os.getenv("NEW_PORT"),
            'dbname': os.getenv("NEW_DBNAME"),
            'sslmode': os.getenv("SSL_MODE"),
            'connect_timeout': 30,
            'application_name': 'helper_migration_v2_script'
        }
    
    def connect_databases(self) -> bool:
        """Establish connections to both Supabase projects."""
        try:
            logger.info("Connecting to old Supabase project...")
            self.old_conn = psycopg2.connect(**self._get_old_connection_params())
            logger.info("SUCCESS: Connected to old Supabase project")
            
            logger.info("Connecting to new Supabase project...")
            self.new_conn = psycopg2.connect(**self._get_new_connection_params())
            logger.info("SUCCESS: Connected to new Supabase project")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to databases: {e}")
            return False
    
    def close_connections(self):
        """Close database connections."""
        if self.old_conn:
            self.old_conn.close()
        if self.new_conn:
            self.new_conn.close()
    
    def cleanup_existing_phone_numbers(self):
        """Clean up existing phone numbers in the new database to prevent conflicts."""
        try:
            logger.info("Cleaning up existing phone numbers...")
            
            with self.new_conn.cursor() as cursor:
                # Find all phone numbers that start with +
                cursor.execute("""
                    SELECT id, phone FROM auth.users 
                    WHERE phone LIKE '+%' AND LENGTH(phone) = 11
                """)
                plus_phones = cursor.fetchall()
                
                if plus_phones:
                    logger.info(f"Found {len(plus_phones)} phone numbers starting with +")
                    
                    for user_id, phone in plus_phones:
                        # Convert +XXXXXXXXXX to 1XXXXXXXXXX
                        new_phone = '1' + phone[1:]
                        
                        # Check if this new phone already exists
                        cursor.execute("SELECT id FROM auth.users WHERE phone = %s", (new_phone,))
                        if cursor.fetchone():
                            # Phone already exists, make it unique
                            counter = 1
                            while True:
                                unique_phone = f"{new_phone}_{counter}"
                                cursor.execute("SELECT id FROM auth.users WHERE phone = %s", (unique_phone,))
                                if not cursor.fetchone():
                                    new_phone = unique_phone
                                    break
                                counter += 1
                        
                        # Update the phone number
                        cursor.execute("""
                            UPDATE auth.users SET phone = %s WHERE id = %s
                        """, (new_phone, user_id))
                        
                        logger.info(f"Updated user {user_id}: {phone} → {new_phone}")
                    
                    self.new_conn.commit()
                    logger.info("Phone number cleanup completed")
                else:
                    logger.info("No phone numbers starting with + found")
                    
        except Exception as e:
            self.new_conn.rollback()
            logger.error(f"Failed to cleanup phone numbers: {e}")
            raise
    
    def get_old_helpers(self) -> List[Dict[str, Any]]:
        """Fetch all helper data from the old database."""
        try:
            with self.old_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                SELECT 
                    h.id,
                    h.auth_id,
                    h.first_name,
                    h.last_name,
                    h.email,
                    h.phone,
                    h.college,
                    h.education,
                    h.graduation_year,
                    h.college_email,
                    h.experience,
                    h.availability,
                    h.bio,
                    h.status,
                    h.date_of_birth,
                    h.terms_accepted,
                    h.profile_image_url,
                    h.created_at,
                    h.updated_at,
                    h.is_around_campus,
                    h.payout_methods,
                    h.zip_code,
                    h.referred_from,
                    u.email_confirmed_at,
                    u.phone_confirmed_at
                FROM helpers h
                LEFT JOIN auth.users u ON h.auth_id = u.id
                ORDER BY h.created_at
                """
                
                cursor.execute(query)
                helpers = cursor.fetchall()
                
                # Convert to regular dictionaries
                helpers_list = []
                for helper in helpers:
                    helper_dict = dict(helper)
                    # Handle None values for JSON fields
                    if helper_dict.get('education') is None:
                        helper_dict['education'] = {}
                    if helper_dict.get('availability') is None:
                        helper_dict['availability'] = {}
                    if helper_dict.get('payout_methods') is None:
                        helper_dict['payout_methods'] = {}
                    
                    helpers_list.append(helper_dict)
                
                logger.info(f"Found {len(helpers_list)} helpers in old database")
                return helpers_list
                
        except Exception as e:
            logger.error(f"Failed to fetch old helpers: {e}")
            return []
    
    def normalize_phone(self, phone: str) -> str:
        """Normalize phone number to standard format (1XXXXXXXXXX)."""
        if not phone:
            return ""
        
        # Remove all non-digit characters
        phone = re.sub(r'[^\d]', '', phone)
        
        # If it's 11 digits and starts with 1, return as is
        if len(phone) == 11 and phone.startswith('1'):
            return phone
        
        # If it's 10 digits, add 1 prefix
        elif len(phone) == 10:
            return '1' + phone
        
        # If it's 11 digits but doesn't start with 1, replace first digit with 1
        elif len(phone) == 11:
            return '1' + phone[1:]
        
        # For any other length, try to make it 11 digits starting with 1
        elif len(phone) > 0:
            # Take last 10 digits and add 1 prefix
            if len(phone) >= 10:
                return '1' + phone[-10:]
            else:
                # Pad with zeros to make 11 digits
                return '1' + phone.zfill(10)
        
        return phone
    
    def create_or_update_auth_user(self, helper_data: Dict[str, Any]) -> Optional[str]:
        """Create or update auth user in new database with proper transaction handling."""
        try:
            normalized_phone = self.normalize_phone(helper_data.get('phone', ''))
            email = helper_data.get('email', '')
            
            if not email or not normalized_phone:
                logger.warning(f"Missing email or phone for helper {helper_data.get('id')}")
                return None
            
            # Start a new transaction for this operation
            self.new_conn.rollback()  # Clear any previous failed transaction
            
            with self.new_conn.cursor() as cursor:
                try:
                    # Check if auth user already exists by phone or email
                    check_query = """
                    SELECT id, email, phone, email_confirmed_at, phone_confirmed_at
                    FROM auth.users 
                    WHERE phone = %s OR email = %s
                    """
                    cursor.execute(check_query, (normalized_phone, email))
                    existing_user = cursor.fetchone()
                    
                    # If phone conflict, try to find a unique phone number
                    if not existing_user:
                        # Check if normalized phone already exists
                        phone_check_query = """
                        SELECT id FROM auth.users WHERE phone = %s
                        """
                        cursor.execute(phone_check_query, (normalized_phone,))
                        phone_exists = cursor.fetchone()
                        
                        if phone_exists:
                            # Generate a unique phone by adding a suffix
                            base_phone = normalized_phone
                            counter = 1
                            while True:
                                unique_phone = f"{base_phone}_{counter}"
                                cursor.execute(phone_check_query, (unique_phone,))
                                if not cursor.fetchone():
                                    normalized_phone = unique_phone
                                    logger.warning(f"Phone {base_phone} already exists, using {unique_phone}")
                                    break
                                counter += 1
                    
                    current_time = datetime.utcnow()
                    user_id = helper_data.get('auth_id') or helper_data.get('id')
                    
                    if existing_user:
                        existing_user_id, existing_email, existing_phone, email_confirmed, phone_confirmed = existing_user
                        
                        # Update existing user with verification timestamps
                        update_query = """
                        UPDATE auth.users 
                        SET 
                            email = %s,
                            phone = %s,
                            email_confirmed_at = %s,
                            phone_confirmed_at = %s,
                            updated_at = %s
                        WHERE id = %s
                        """
                        cursor.execute(update_query, (
                            email,
                            normalized_phone,
                            current_time,
                            current_time,
                            current_time,
                            existing_user_id
                        ))
                        
                        self.new_conn.commit()
                        self.migration_stats['auth_users_updated'] += 1
                        logger.info(f"Updated existing auth user {existing_user_id} with verification timestamps")
                        return existing_user_id
                        
                    else:
                        # Create new auth user with ONLY actual Supabase fields
                        insert_query = """
                        INSERT INTO auth.users (
                            id, email, phone, email_confirmed_at, phone_confirmed_at
                        ) VALUES (
                            %s, %s, %s, %s, %s
                        )
                        """
                        
                        # Set default values for required auth fields
                        raw_app_meta_data = json.dumps({"provider": "email", "providers": ["email"]})
                        raw_user_meta_data = json.dumps({})
                        
                        cursor.execute(insert_query, (
                            user_id, email, normalized_phone, current_time, current_time
                        ))
                        
                        self.new_conn.commit()
                        self.migration_stats['auth_users_created'] += 1
                        logger.info(f"Created new auth user {user_id}")
                        return user_id
                        
                except Exception as e:
                    self.new_conn.rollback()
                    logger.error(f"Database operation failed for helper {helper_data.get('id')}: {e}")
                    self.migration_stats['error_categories']['auth_user_creation'] += 1
                    return None
                    
        except Exception as e:
            self.new_conn.rollback()
            logger.error(f"Failed to create/update auth user for helper {helper_data.get('id')}: {e}")
            self.migration_stats['error_categories']['auth_user_creation'] += 1
            return None
    
    def migrate_helper_data(self, helper_data: Dict[str, Any], auth_user_id: str) -> bool:
        """Migrate helper data to new schema with proper transaction handling."""
        try:
            # Start fresh transaction
            self.new_conn.rollback()
            
            with self.new_conn.cursor() as cursor:
                try:
                    # Prepare data for new helpers table
                    insert_query = """
                    INSERT INTO public.helpers (
                        id, email, phone, first_name, last_name, pfp_url, college, bio,
                        graduation_year, zip_code, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        email = EXCLUDED.email,
                        phone = EXCLUDED.phone,
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        pfp_url = EXCLUDED.pfp_url,
                        college = EXCLUDED.college,
                        bio = EXCLUDED.bio,
                        graduation_year = EXCLUDED.graduation_year,
                        zip_code = EXCLUDED.zip_code,
                        updated_at = EXCLUDED.updated_at
                    """
                    
                    # Handle missing required fields with defaults
                    first_name = helper_data.get('first_name', 'Unknown')
                    last_name = helper_data.get('last_name', 'Helper')
                    college = helper_data.get('college', 'Unknown College')
                    bio = helper_data.get('bio', 'Helper profile migrated from old system')
                    graduation_year = helper_data.get('graduation_year', 2025)
                    zip_code = helper_data.get('zip_code', '00000')
                    pfp_url = helper_data.get('profile_image_url')
                    
                    # Validate graduation year
                    try:
                        graduation_year = int(graduation_year)
                        if graduation_year < 1900 or graduation_year > 2100:
                            graduation_year = 2025
                    except (ValueError, TypeError):
                        graduation_year = 2025
                    
                    cursor.execute(insert_query, (
                        auth_user_id,
                        helper_data.get('email'),
                        self.normalize_phone(helper_data.get('phone', '')),
                        first_name,
                        last_name,
                        pfp_url,
                        college,
                        bio,
                        graduation_year,
                        zip_code,
                        helper_data.get('created_at') or datetime.utcnow(),
                        datetime.utcnow()
                    ))
                    
                    self.new_conn.commit()
                    logger.info(f"Successfully migrated helper {auth_user_id}")
                    return True
                    
                except Exception as e:
                    self.new_conn.rollback()
                    logger.error(f"Database operation failed for helper {helper_data.get('id')}: {e}")
                    self.migration_stats['error_categories']['helper_migration'] += 1
                    return False
                
        except Exception as e:
            self.new_conn.rollback()
            logger.error(f"Failed to migrate helper data for {helper_data.get('id')}: {e}")
            self.migration_stats['error_categories']['helper_migration'] += 1
            return False
    
    def run_migration(self) -> bool:
        """Run the complete migration process."""
        try:
            logger.info("Starting helper migration from old schema to new HelperU_v2 schema...")
            
            # Clean up existing phone numbers to prevent conflicts
            self.cleanup_existing_phone_numbers()
            
            # Get all helpers from old database
            old_helpers = self.get_old_helpers()
            if not old_helpers:
                logger.warning("No helpers found in old database")
                return True
            
            self.migration_stats['helpers_found'] = len(old_helpers)
            
            # Process each helper
            for helper_data in old_helpers:
                try:
                    logger.info(f"Processing helper: {helper_data.get('first_name')} {helper_data.get('last_name')} ({helper_data.get('email')})")
                    
                    # Create or update auth user
                    auth_user_id = self.create_or_update_auth_user(helper_data)
                    if not auth_user_id:
                        logger.warning(f"Skipping helper {helper_data.get('id')} due to auth user creation failure")
                        continue
                    
                    # Migrate helper data
                    if self.migrate_helper_data(helper_data, auth_user_id):
                        self.migration_stats['helpers_migrated'] += 1
                    
                except Exception as e:
                    error_msg = f"Failed to process helper {helper_data.get('id')}: {e}"
                    logger.error(error_msg)
                    self.migration_stats['errors'].append(error_msg)
                    self.migration_stats['error_categories']['other'] += 1
            
            # Log migration summary
            self.log_migration_summary()
            
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def log_migration_summary(self):
        """Log a summary of the migration results."""
        logger.info("=" * 60)
        logger.info("MIGRATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total helpers found: {self.migration_stats['helpers_found']}")
        logger.info(f"Helpers successfully migrated: {self.migration_stats['helpers_migrated']}")
        logger.info(f"Auth users created: {self.migration_stats['auth_users_created']}")
        logger.info(f"Auth users updated: {self.migration_stats['auth_users_updated']}")
        logger.info(f"Total errors: {len(self.migration_stats['errors'])}")
        
        if self.migration_stats['errors']:
            logger.info("\nError Categories:")
            for category, count in self.migration_stats['error_categories'].items():
                if count > 0:
                    logger.info(f"  {category}: {count}")
        
        logger.info("=" * 60)


@click.command()
@click.option('--dry-run', is_flag=True, help='Run migration without making changes')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def main(dry_run: bool, verbose: bool):
    """Migrate helper data from old schema to new HelperU_v2 schema."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    migrator = HelperV2Migrator()
    
    try:
        # Connect to databases
        if not migrator.connect_databases():
            logger.error("Failed to connect to databases")
            sys.exit(1)
        
        if dry_run:
            logger.info("DRY RUN MODE: No changes will be made")
            # In dry run mode, just fetch and display what would be migrated
            old_helpers = migrator.get_old_helpers()
            logger.info(f"Would migrate {len(old_helpers)} helpers")
            for helper in old_helpers[:5]:  # Show first 5 as sample
                logger.info(f"Sample: {helper.get('first_name')} {helper.get('last_name')} - {helper.get('email')}")
        else:
            # Run actual migration
            success = migrator.run_migration()
            if not success:
                logger.error("Migration failed")
                sys.exit(1)
            logger.info("Migration completed successfully")
    
    except KeyboardInterrupt:
        logger.info("Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        migrator.close_connections()


if __name__ == "__main__":
    main()
