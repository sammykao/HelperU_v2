#!/usr/bin/env python3
"""
Client Migration Script: Old Database to HelperU_v2
This script migrates client data and creates corresponding auth users.
"""

import sys
import logging
import click
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('client_migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ClientMigrator:
    """Handles the migration of clients from old database to new HelperU_v2 schema."""
    
    def __init__(self, old_db_config: Dict[str, str], new_db_config: Dict[str, str]):
        """
        Initialize the migrator with database configurations.
        
        Args:
            old_db_config: Configuration for the old database
            new_db_config: Configuration for the new database
        """
        self.old_db_config = old_db_config
        self.new_db_config = new_db_config
        self.old_conn = None
        self.new_conn = None
        self.migration_stats = {
            'clients_found': 0,
            'clients_migrated': 0,
            'auth_users_created': 0,
            'errors': []
        }
    
    def connect_databases(self) -> bool:
        """Establish connections to both databases."""
        try:
            logger.info("Connecting to old database...")
            self.old_conn = psycopg2.connect(**self.old_db_config)
            
            logger.info("Connecting to new database...")
            self.new_conn = psycopg2.connect(**self.new_db_config)
            
            logger.info("Database connections established successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to databases: {e}")
            return False
    
    def disconnect_databases(self):
        """Close database connections."""
        if self.old_conn:
            self.old_conn.close()
        if self.new_conn:
            self.new_conn.close()
        logger.info("Database connections closed")
    
    def get_old_clients(self) -> List[Dict[str, Any]]:
        """Retrieve all client data from the old database."""
        try:
            logger.info("Retrieving client data from old database...")
            
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
                
                logger.info(f"Found {len(clients)} clients in old database")
                return clients
                
        except Exception as e:
            logger.error(f"Failed to retrieve clients from old database: {e}")
            return []
    
    def create_auth_user_for_client(self, client: Dict[str, Any]) -> bool:
        """Create an auth user for a client."""
        try:
            # Skip if no auth_id (orphaned client)
            if not client['auth_id']:
                logger.warning(f"Client {client['id']} has no auth_id, skipping auth user creation")
                return False
            
            with self.new_conn.cursor() as cur:
                # Set phone confirmation timestamp based on verification status
                phone_confirmed_at = None
                if client['phone_verified']:
                    phone_confirmed_at = client['updated_at'] or client['created_at']
                
                # Create basic auth user without metadata
                cur.execute("""
                    INSERT INTO auth.users (
                        id,
                        phone,
                        phone_confirmed_at,
                        created_at,
                        updated_at
                    ) VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    client['auth_id'],
                    client['phone'],
                    phone_confirmed_at,
                    client['created_at'],
                    client['updated_at']
                ))
                
                self.migration_stats['auth_users_created'] += 1
                logger.debug(f"Created auth user for client {client['id']}")
                return True
                
        except Exception as e:
            error_msg = f"Error creating auth user for client {client['id']}: {e}"
            logger.error(error_msg)
            self.migration_stats['errors'].append(error_msg)
            return False
    
    def migrate_client_to_new_schema(self, client: Dict[str, Any]) -> bool:
        """Migrate a single client to the new schema."""
        try:
            # Skip if no auth_id (orphaned client)
            if not client['auth_id']:
                logger.warning(f"Client {client['id']} has no auth_id, skipping migration")
                return False
            
            with self.new_conn.cursor() as cur:
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
                        first_name = EXCLUDED.last_name,
                        last_name = EXCLUDED.last_name,
                        pfp_url = EXCLUDED.pfp_url,
                        number_of_posts = EXCLUDED.number_of_posts,
                        updated_at = EXCLUDED.updated_at
                """, (
                    client['auth_id'],  # Use auth_id as the new ID
                    client['phone'],
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
                        stripe_customer_id,
                        plan,
                        status,
                        created_at,
                        updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO NOTHING
                """, (
                    client['auth_id'],
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
            logger.info("Starting client migration...")
            
            # Step 1: Get all clients from old database
            old_clients = self.get_old_clients()
            if not old_clients:
                logger.warning("No clients found to migrate")
                return True
            
            # Step 2: Process each client
            for i, client in enumerate(old_clients, 1):
                logger.info(f"Processing client {i}/{len(old_clients)}: {client['id']}")
                
                try:
                    # Create auth user first
                    if not self.create_auth_user_for_client(client):
                        logger.warning(f"Skipping client {client['id']} due to auth user creation failure")
                        continue
                    
                    # Migrate client data
                    if not self.migrate_client_to_new_schema(client):
                        logger.warning(f"Skipping client {client['id']} due to migration failure")
                        continue
                    
                    # Create subscription if Stripe customer exists
                    self.create_subscription_for_stripe_customer(client)
                    
                    # Commit after each successful client migration
                    self.new_conn.commit()
                    
                except Exception as e:
                    error_msg = f"Unexpected error processing client {client['id']}: {e}"
                    logger.error(error_msg)
                    self.migration_stats['errors'].append(error_msg)
                    self.new_conn.rollback()
                    continue
            
            logger.info("Client migration completed!")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            self.new_conn.rollback()
            return False
    
    def print_stats(self):
        """Print migration statistics."""
        print("\n" + "="*60)
        print("CLIENT MIGRATION STATISTICS")
        print("="*60)
        print(f"Clients found in old database: {self.migration_stats['clients_found']}")
        print(f"Clients successfully migrated: {self.migration_stats['clients_migrated']}")
        print(f"Auth users created: {self.migration_stats['auth_users_created']}")
        
        if self.migration_stats['errors']:
            print(f"\nErrors encountered: {len(self.migration_stats['errors'])}")
            for error in self.migration_stats['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(self.migration_stats['errors']) > 5:
                print(f"  ... and {len(self.migration_stats['errors']) - 5} more errors")
        else:
            print("\nNo errors encountered! ✅")
        
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
                logger.info(f"✅ Client migration validation passed: {new_client_count} clients migrated")
                return True
            else:
                logger.error(f"❌ Client migration validation failed: Expected {self.migration_stats['clients_migrated']}, got {new_client_count}")
                return False
                
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False


@click.command()
@click.option('--old-host', default='localhost', help='Old database host')
@click.option('--old-port', default=5432, help='Old database port')
@click.option('--old-database', required=True, help='Old database name')
@click.option('--old-username', required=True, help='Old database username')
@click.option('--old-password', required=True, help='Old database password')
@click.option('--new-host', default='localhost', help='New database host')
@click.option('--new-port', default=5432, help='New database port')
@click.option('--new-database', required=True, help='New database name')
@click.option('--new-username', required=True, help='New database username')
@click.option('--new-password', required=True, help='New database password')
@click.option('--dry-run', is_flag=True, help='Run migration without making changes')
@click.option('--validate-only', is_flag=True, help='Only validate existing migration')
def main(old_host, old_port, old_database, old_username, old_password,
         new_host, new_port, new_database, new_username, new_password, 
         dry_run, validate_only):
    """Migrate client data from old database to new HelperU_v2 schema."""
    
    # Database configurations
    old_db_config = {
        'host': old_host,
        'port': old_port,
        'database': old_database,
        'user': old_username,
        'password': old_password
    }
    
    new_db_config = {
        'host': new_host,
        'port': new_port,
        'database': new_database,
        'user': new_username,
        'password': new_password
    }
    
    if dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
    
    if validate_only:
        logger.info("VALIDATION ONLY MODE - Checking existing migration")
    
    # Create migrator instance
    migrator = ClientMigrator(old_db_config, new_db_config)
    
    try:
        # Connect to databases
        if not migrator.connect_databases():
            sys.exit(1)
        
        if validate_only:
            # Only run validation
            success = migrator.validate_migration()
            if success:
                logger.info("Validation completed successfully! ✅")
                sys.exit(0)
            else:
                logger.error("Validation failed! ❌")
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
                    logger.info("Migration and validation completed successfully! ✅")
                else:
                    logger.warning("Migration completed but validation failed! ⚠️")
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
