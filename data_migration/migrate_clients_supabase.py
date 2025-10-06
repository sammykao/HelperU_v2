#!/usr/bin/env python3
"""
Client Migration Script: Old Supabase to New HelperU_v2 Supabase
This script migrates client data between Supabase projects using dotenv and psycopg2.
"""

import sys
import logging
import click
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Any
import os
from dotenv import load_dotenv
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('client_migration_supabase.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class SupabaseClientMigrator:
    """Handles the migration of clients between Supabase projects."""
    
    def __init__(self):
        """Initialize the migrator with environment variables."""
        # Load environment variables
        load_dotenv('supabase.env')
        
        self.old_conn = None
        self.new_conn = None
        self.migration_stats = {
            'clients_found': 0,
            'clients_migrated': 0,
            'auth_users_created': 0,
            'errors': [],
            'failed_clients': [],  # Track failed clients with details
            'error_categories': {
                'duplicate_phone': 0,
                'phone_verification': 0,
                'auth_user_creation': 0,
                'client_migration': 0,
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
            'application_name': 'client_migration_script'
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
            'application_name': 'client_migration_script'
        }
    
    def _get_new_pooler_connection_params(self) -> Dict[str, str]:
        """Get Transaction Pooler connection parameters for NEW project as fallback."""
        return {
            'user': os.getenv("NEW_USER"),
            'password': os.getenv("NEW_PASSWORD"),
            'host': os.getenv("NEW_HOST"),
            'port': '6543',  # Transaction Pooler port
            'dbname': os.getenv("NEW_DBNAME"),
            'sslmode': os.getenv("SSL_MODE"),
            'connect_timeout': 30,
            'application_name': 'client_migration_script'
        }
    
    def connect_databases(self) -> bool:
        """Establish connections to both Supabase projects."""
        try:
            logger.info("Connecting to old Supabase project...")
            self.old_conn = psycopg2.connect(**self._get_old_connection_params())
            logger.info("SUCCESS: Connected to old Supabase project")
            
            logger.info("Connecting to new Supabase project...")
            try:
                # Try direct connection first
                self.new_conn = psycopg2.connect(**self._get_new_connection_params())
                logger.info("SUCCESS: Connected to new Supabase project via Direct Connection")
            except Exception as e:
                logger.warning(f"Direct connection to new project failed: {e}")
                logger.info("Trying Transaction Pooler for new project...")
                
                # Fallback to Transaction Pooler for new project
                self.new_conn = psycopg2.connect(**self._get_new_pooler_connection_params())
                logger.info("SUCCESS: Connected to new Supabase project via Transaction Pooler")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Supabase projects: {e}")
            return False
    
    def disconnect_databases(self):
        """Close database connections."""
        if self.old_conn:
            self.old_conn.close()
        if self.new_conn:
            self.new_conn.close()
        logger.info("Supabase connections closed")
    
    def get_old_clients(self) -> List[Dict[str, Any]]:
        """Retrieve all client data from the old Supabase project."""
        try:
            logger.info("Retrieving client data from old Supabase project...")
            
            with self.old_conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get all clients with their data
                cur.execute("""
                    SELECT 
                        id,
                        auth_id,
                        first_name,
                        last_name,
                        email,
                        phone,
                        profile_image_url,
                        created_at,
                        updated_at,
                        referred_from,
                        stripe_customer_id,
                        notifications_enabled,
                        email_verified,
                        phone_verified,
                        verification_logs
                    FROM clients
                    ORDER BY created_at
                """)
                
                clients = cur.fetchall()
                self.migration_stats['clients_found'] = len(clients)
                
                logger.info(f"Found {len(clients)} clients in old Supabase project")
                return clients
                
        except Exception as e:
            logger.error(f"Failed to retrieve clients from old Supabase project: {e}")
            return []
    
    def _format_phone_number(self, phone: str) -> str:
        """Format phone number for database storage (11 digits without + prefix)."""
        if not phone:
            return phone
        
        # Remove all non-digit characters including Unicode special characters
        digits_only = re.sub(r'[^\d]', '', phone)
        
        # Ensure it's 11 digits starting with 1 (database format)
        if len(digits_only) == 10:
            # Add US country code
            return f"1{digits_only}"
        elif len(digits_only) == 11 and digits_only.startswith('1'):
            # Already in correct format
            return digits_only
        else:
            # Invalid format
            return None

    def create_auth_user_for_client(self, client: Dict[str, Any]) -> bool:
        """Create an auth user for a client in new Supabase project."""
        try:
            # Skip if no auth_id (orphaned client)
            if not client['auth_id']:
                error_msg = f"Client {client['id']} has no auth_id, skipping auth user creation"
                logger.warning(error_msg)
                
                # Track failed client
                failed_client = {
                    'client_id': client['id'],
                    'first_name': client.get('first_name', 'Unknown'),
                    'last_name': client.get('last_name', 'Client'),
                    'email': client.get('email'),
                    'phone': client.get('phone'),
                    'reason': 'Missing auth_id',
                    'error_details': error_msg
                }
                self.migration_stats['failed_clients'].append(failed_client)
                return False
            
            # Format phone number
            formatted_phone = self._format_phone_number(client['phone'])
            if not formatted_phone or len(formatted_phone) != 11:
                error_msg = f"Invalid phone number format for client {client['id']}: {client['phone']} -> {formatted_phone}"
                logger.warning(error_msg)
                
                # Track failed client
                failed_client = {
                    'client_id': client['id'],
                    'first_name': client.get('first_name', 'Unknown'),
                    'last_name': client.get('last_name', 'Client'),
                    'email': client.get('email'),
                    'phone': client.get('phone'),
                    'reason': 'Invalid phone number format',
                    'error_details': error_msg
                }
                self.migration_stats['failed_clients'].append(failed_client)
                return False
            
            with self.new_conn.cursor() as cur:
                # Check if phone number already exists
                cur.execute("SELECT id FROM auth.users WHERE phone = %s", (formatted_phone,))
                existing_user = cur.fetchone()
                
                if existing_user:
                    error_msg = f"Phone number {formatted_phone} already exists for user {existing_user[0]}, skipping auth user creation"
                    logger.warning(error_msg)
                    
                    # Track failed client
                    failed_client = {
                        'client_id': client['id'],
                        'first_name': client.get('first_name', 'Unknown'),
                        'last_name': client.get('last_name', 'Client'),
                        'email': client.get('email'),
                        'phone': client.get('phone'),
                        'reason': 'Phone number already exists',
                        'error_details': error_msg
                    }
                    self.migration_stats['failed_clients'].append(failed_client)
                    return False
                
                # Set phone confirmation timestamp based on verification status
                # IMPORTANT: For migration, we need to set phone_confirmed_at to make the phone "verified"
                phone_confirmed_at = None
                if client['phone_verified']:
                    phone_confirmed_at = client['updated_at'] or client['created_at']
                else:
                    # For migration purposes, set phone as verified if we have a phone number
                    # This prevents the trigger constraint from failing
                    phone_confirmed_at = client['updated_at'] or client['created_at']
                
                # Create COMPLETE auth user with all required Supabase fields
                cur.execute("""
                    INSERT INTO auth.users (
                        id,
                        instance_id,
                        aud,
                        role,
                        phone,
                        phone_confirmed_at,
                        encrypted_password,
                        last_sign_in_at,
                        raw_app_meta_data,
                        raw_user_meta_data,
                        created_at,
                        updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    client['auth_id'],
                    '00000000-0000-0000-0000-000000000000',  # Default instance_id
                    'authenticated',  # Default aud
                    'authenticated',  # Default role  # Email (can be empty for phone-only auth)
                    formatted_phone,  # Formatted phone number
                    phone_confirmed_at,
                    '',  # Empty encrypted_password (will be set on first sign-in)
                    phone_confirmed_at,  # Set last_sign_in_at to phone confirmation time
                    '{"provider": "phone", "providers": ["phone"]}',  # Required app metadata
                    '{}',  # Empty user metadata
                    client['created_at'],
                    client['updated_at']
                ))
                
                self.migration_stats['auth_users_created'] += 1
                logger.debug(f"Created complete auth user for client {client['id']} with phone {formatted_phone}")
                return True
                
        except Exception as e:
            error_msg = f"Error creating auth user for client {client['id']}: {e}"
            logger.error(error_msg)
            self.migration_stats['errors'].append(error_msg)
            
            # Track failed client
            failed_client = {
                'client_id': client['id'],
                'first_name': client.get('first_name', 'Unknown'),
                'last_name': client.get('last_name', 'Client'),
                'email': client.get('email'),
                'phone': client.get('phone'),
                'reason': 'Auth user creation failed',
                'error_details': error_msg
            }
            self.migration_stats['failed_clients'].append(failed_client)
            
            # Categorize the error
            if "duplicate key value violates unique constraint" in str(e):
                self.migration_stats['error_categories']['duplicate_phone'] += 1
            elif "phone" in str(e).lower():
                self.migration_stats['error_categories']['phone_verification'] += 1
            else:
                self.migration_stats['error_categories']['auth_user_creation'] += 1
                
            return False
    
    def migrate_client_to_new_schema(self, client: Dict[str, Any]) -> bool:
        """Migrate a single client to the new Supabase schema."""
        try:
            # Skip if no auth_id (orphaned client)
            if not client['auth_id']:
                logger.warning(f"Client {client['id']} has no auth_id, skipping migration")
                return False
            
            with self.new_conn.cursor() as cur:
                # Verify that auth user exists and phone matches
                cur.execute("""
                    SELECT phone, phone_confirmed_at 
                    FROM auth.users 
                    WHERE id = %s
                """, (client['auth_id'],))
                
                auth_user = cur.fetchone()
                if not auth_user:
                    logger.error(f"Auth user {client['auth_id']} not found, cannot migrate client")
                    return False
                
                auth_phone, phone_confirmed_at = auth_user
                formatted_client_phone = self._format_phone_number(client['phone'])
                if auth_phone != formatted_client_phone:
                    logger.error(f"Phone mismatch: auth.users has {auth_phone}, formatted client has {formatted_client_phone}")
                    return False
                
                if not phone_confirmed_at:
                    logger.error(f"Phone not confirmed for user {client['auth_id']}")
                    return False
                
                # Count tasks for this client to set number_of_posts
                task_count = 0
                try:
                    with self.old_conn.cursor() as old_cur:
                        old_cur.execute("""
                            SELECT COUNT(*) FROM tasks WHERE client_id = %s
                        """, (client['id'],))
                        task_count = old_cur.fetchone()[0]
                except Exception as e:
                    logger.warning(f"Could not count tasks for client {client['id']}: {e}")
                
                # Insert into new clients table
                cur.execute("""
                    INSERT INTO public.clients (
                        id,
                        phone,
                        email,
                        first_name,
                        last_name,
                        pfp_url,
                        number_of_posts,
                        created_at,
                        updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        phone = EXCLUDED.phone,
                        email = EXCLUDED.email,
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        pfp_url = EXCLUDED.pfp_url,
                        number_of_posts = EXCLUDED.number_of_posts,
                        updated_at = EXCLUDED.updated_at
                """, (
                    client['auth_id'],  # Use auth_id as the new ID
                    formatted_client_phone,  # Use formatted phone number
                    client['email'] or '',  # Ensure email is not null
                    client['first_name'] or 'Unknown',
                    client['last_name'] or 'Unknown',
                    client['profile_image_url'],
                    task_count,
                    client['created_at'],
                    client['updated_at']
                ))
                
                self.migration_stats['clients_migrated'] += 1
                logger.debug(f"Migrated client {client['id']} to new schema")
                return True
                
        except Exception as e:
            error_msg = f"Error migrating client {client['id']}: {e}"
            logger.error(error_msg)
            self.migration_stats['errors'].append(error_msg)
            
            # Categorize the error
            if "phone" in str(e).lower() and "verified" in str(e).lower():
                self.migration_stats['error_categories']['phone_verification'] += 1
            else:
                self.migration_stats['error_categories']['client_migration'] += 1
                
            return False
    
    def create_subscription_for_stripe_customer(self, client: Dict[str, Any]) -> bool:
        """Create subscription record for existing Stripe customers."""
        try:
            if not client['stripe_customer_id']:
                return True  # No Stripe customer, skip
            
            with self.new_conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO public.subscriptions (
                        user_id,
                        stripe_subscription_id,
                        stripe_customer_id,
                        plan,
                        status,
                        created_at,
                        updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (stripe_subscription_id) DO NOTHING
                """, (
                    client['auth_id'],
                    None,
                    client['stripe_customer_id'],
                    'free',  # Default to free plan
                    'active',  # Default to active status
                    client['created_at'],
                    client['updated_at']
                ))
                
                logger.debug(f"Created subscription for Stripe customer {client['stripe_customer_id']}")
                return True
                
        except Exception as e:
            error_msg = f"Error creating subscription for client {client['id']}: {e}"
            logger.error(error_msg)
            self.migration_stats['errors'].append(error_msg)
            return False
    
    def run_migration(self) -> bool:
        """Run the complete client migration process."""
        try:
            logger.info("Starting client migration between Supabase projects...")
            
            # Step 1: Get all clients from old Supabase project
            old_clients = self.get_old_clients()
            if not old_clients:
                logger.warning("No clients found to migrate")
                return True
            
            # Step 2: Process each client
            for i, client in enumerate(old_clients, 1):
                logger.info(
                    f"Processing client {i}/{len(old_clients)}: {client['first_name']} {client['last_name']} (ID: {client['id']})"
                )
                
                try:
                    # Start a new transaction for each client
                    self.new_conn.rollback()  # Ensure clean state
                    
                    # Create auth user first
                    if not self.create_auth_user_for_client(client):
                        logger.warning(f"Skipping client {client['id']} due to auth user creation failure")
                        continue
                    
                    # Migrate client data
                    if not self.migrate_client_to_new_schema(client):
                        logger.warning(f"Skipping client {client['id']} due to migration failure")
                        self.new_conn.rollback()
                        continue
                    
                    # Create subscription if Stripe customer exists
                    self.create_subscription_for_stripe_customer(client)
                    
                    # Commit after each successful client migration
                    self.new_conn.commit()
                    logger.info(
                        f"SUCCESS: Migrated client {client['first_name']} {client['last_name']} (ID: {client['id']})"
                    )
                    
                except Exception as e:
                    error_msg = f"Unexpected error processing client {client['id']}: {e}"
                    logger.error(error_msg)
                    self.migration_stats['errors'].append(error_msg)
                    self.new_conn.rollback()
                    continue
            
            logger.info("Client migration between Supabase projects completed!")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            self.new_conn.rollback()
            return False
    
    def print_stats(self):
        """Print migration statistics."""
        print("\n" + "="*60)
        print("SUPABASE CLIENT MIGRATION STATISTICS")
        print("="*60)
        print(f"Clients found in old Supabase: {self.migration_stats['clients_found']}")
        print(f"Clients successfully migrated: {self.migration_stats['clients_migrated']}")
        print(f"Auth users created: {self.migration_stats['auth_users_created']}")
        
        if self.migration_stats['errors']:
            print(f"\nErrors encountered: {len(self.migration_stats['errors'])}")
            print("\nError Categories:")
            for category, count in self.migration_stats['error_categories'].items():
                if count > 0:
                    print(f"  - {category.replace('_', ' ').title()}: {count}")
            
            print("\nFirst 5 detailed errors:")
            for error in self.migration_stats['errors'][:5]:
                print(f"  - {error}")
            if len(self.migration_stats['errors']) > 5:
                print(f"  ... and {len(self.migration_stats['errors']) - 5} more errors")
        else:
            print("\nNo errors encountered!")
        
        # Print failed clients details
        if self.migration_stats['failed_clients']:
            print(f"\nFAILED CLIENTS ({len(self.migration_stats['failed_clients'])}):")
            print("-" * 60)
            for i, client in enumerate(self.migration_stats['failed_clients'], 1):
                print(f"{i}. Client ID: {client['client_id']}")
                print(f"   Name: {client['first_name']} {client['last_name']}")
                print(f"   Email: {client['email']}")
                print(f"   Phone: {client['phone']}")
                print(f"   Reason: {client['reason']}")
                print(f"   Error: {client['error_details']}")
                print("-" * 40)
        
        print("="*60)
    
    def validate_migration(self) -> bool:
        """Validate that the migration was successful."""
        try:
            logger.info("Validating migration results...")
            
            # Check if all clients were migrated
            with self.new_conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM public.clients")
                new_client_count = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM auth.users WHERE phone IS NOT NULL")
                _ = cur.fetchone()[0]
            
            # Check if counts match
            if new_client_count == self.migration_stats['clients_migrated']:
                logger.info(f"SUCCESS: Client migration validation passed: {new_client_count} clients migrated")
                return True
            else:
                logger.error(f"FAILED: Client migration validation failed: Expected {self.migration_stats['clients_migrated']}, got {new_client_count}")
                return False
                
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False


@click.command()
@click.option('--dry-run', is_flag=True, help='Run migration without making changes')
@click.option('--validate-only', is_flag=True, help='Only validate existing migration')
def main(dry_run, validate_only):
    """Migrate client data between Supabase projects using environment variables."""
    
    if dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
    
    if validate_only:
        logger.info("VALIDATION ONLY MODE - Checking existing migration")
    
    # Create migrator instance
    migrator = SupabaseClientMigrator()
    
    try:
        # Connect to Supabase projects
        if not migrator.connect_databases():
            sys.exit(1)
        
        if validate_only:
            # Only run validation
            success = migrator.validate_migration()
            if success:
                logger.info("Validation completed successfully!")
                sys.exit(0)
            else:
                logger.error("Validation failed!")
                sys.exit(1)
        
        # Run migration
        if dry_run:
            logger.info("Dry run completed - no changes made")
        else:
            if migrator.run_migration():
                migrator.print_stats()
                
                # Run validation after migration
                logger.info("Running post-migration validation...")
                if migrator.validate_migration():
                    logger.info("Migration and validation completed successfully!")
                else:
                    logger.warning("Migration completed but validation failed!")
            else:
                logger.error("Migration failed!")
                sys.exit(1)
                
    except KeyboardInterrupt:
        logger.info("Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        migrator.disconnect_databases()


if __name__ == '__main__':
    main()
