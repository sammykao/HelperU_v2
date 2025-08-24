#!/usr/bin/env python3
"""
Database Cleanup Script for Supabase Migration
This script clears all migrated data to allow for a fresh migration attempt.
"""

import sys
import logging
import click
import psycopg2
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseCleaner:
    """Handles cleanup of migrated data from Supabase database."""
    
    def __init__(self):
        """Initialize the cleaner with environment variables."""
        # Load environment variables
        load_dotenv('supabase.env')
        
        self.conn = None
        self.cleanup_stats = {
            'clients_deleted': 0,
            'subscriptions_deleted': 0,
            'auth_users_deleted': 0,
            'errors': []
        }
    
    def _get_connection_params(self) -> Dict[str, str]:
        """Get connection parameters for NEW project from environment variables."""
        return {
            'user': os.getenv("NEW_USER"),
            'password': os.getenv("NEW_PASSWORD"),
            'host': os.getenv("NEW_HOST"),
            'port': os.getenv("NEW_PORT"),
            'dbname': os.getenv("NEW_DBNAME"),
            'sslmode': os.getenv("SSL_MODE"),
            'connect_timeout': 30,
            'application_name': 'database_cleanup_script'
        }
    
    def connect_database(self) -> bool:
        """Establish connection to the new Supabase project."""
        try:
            logger.info("Connecting to new Supabase project...")
            self.conn = psycopg2.connect(**self._get_connection_params())
            logger.info("SUCCESS: Connected to new Supabase project")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Supabase project: {e}")
            return False
    
    def disconnect_database(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
        logger.info("Supabase connection closed")
    
    def clear_migrated_data(self) -> bool:
        """Clear all migrated data from the database."""
        try:
            logger.info("Starting database cleanup...")
            
            with self.conn.cursor() as cur:
                # Clear subscriptions first (due to foreign key constraints)
                logger.info("Clearing subscriptions...")
                cur.execute("DELETE FROM public.subscriptions")
                self.cleanup_stats['subscriptions_deleted'] = cur.rowcount
                logger.info(f"Deleted {cur.rowcount} subscriptions")
                
                # Clear clients
                logger.info("Clearing clients...")
                cur.execute("DELETE FROM public.clients")
                self.cleanup_stats['clients_deleted'] = cur.rowcount
                logger.info(f"Deleted {cur.rowcount} clients")
                
                # Clear auth users (only those with phone numbers - migrated users)
                logger.info("Clearing migrated auth users...")
                cur.execute("DELETE FROM auth.users WHERE phone IS NOT NULL")
                self.cleanup_stats['auth_users_deleted'] = cur.rowcount
                logger.info(f"Deleted {cur.rowcount} auth users")
                
                # Commit the cleanup
                self.conn.commit()
                logger.info("Database cleanup completed successfully!")
                return True
                
        except Exception as e:
            error_msg = f"Cleanup failed: {e}"
            logger.error(error_msg)
            self.cleanup_stats['errors'].append(error_msg)
            self.conn.rollback()
            return False
    
    def print_stats(self):
        """Print cleanup statistics."""
        print("\n" + "="*60)
        print("DATABASE CLEANUP STATISTICS")
        print("="*60)
        print(f"Subscriptions deleted: {self.cleanup_stats['subscriptions_deleted']}")
        print(f"Clients deleted: {self.cleanup_stats['clients_deleted']}")
        print(f"Auth users deleted: {self.cleanup_stats['auth_users_deleted']}")
        
        if self.cleanup_stats['errors']:
            print(f"\nErrors encountered: {len(self.cleanup_stats['errors'])}")
            for error in self.cleanup_stats['errors']:
                print(f"  - {error}")
        else:
            print("\nNo errors encountered!")
        
        print("="*60)


@click.command()
@click.option('--dry-run', is_flag=True, help='Show what would be deleted without actually deleting')
def main(dry_run):
    """Clear all migrated data from Supabase database."""
    
    if dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
        logger.info("This would delete:")
        logger.info("  - All records from public.subscriptions")
        logger.info("  - All records from public.clients")
        logger.info("  - All auth.users with phone numbers (migrated users)")
        logger.info("Run without --dry-run to actually perform the cleanup")
        return
    
    # Create cleaner instance
    cleaner = DatabaseCleaner()
    
    try:
        # Connect to Supabase project
        if not cleaner.connect_database():
            sys.exit(1)
        
        # Perform cleanup
        if cleaner.clear_migrated_data():
            cleaner.print_stats()
            logger.info("Database cleanup completed successfully!")
        else:
            logger.error("Database cleanup failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Cleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        cleaner.disconnect_database()


if __name__ == '__main__':
    main()
