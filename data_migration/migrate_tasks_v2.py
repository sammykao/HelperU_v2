#!/usr/bin/env python3
"""
Task Migration Script v2: Migrate from old tasks schema to new HelperU_v2 schema
This script handles the migration of task data with proper field mapping and transformations.
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
import csv
from dotenv import load_dotenv
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('task_migration_v2.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class TaskV2Migrator:
    """Handles the migration of tasks from old schema to new HelperU_v2 schema."""
    
    def __init__(self):
        """Initialize the migrator with environment variables."""
        # Load environment variables
        load_dotenv('supabase.env')
        
        self.old_conn = None
        self.new_conn = None
        self.migration_stats = {
            'tasks_found': 0,
            'tasks_migrated': 0,
            'tasks_skipped': 0,
            'client_lookups_failed': 0,
            'errors': [],
            'failed_tasks': [],  # Track failed tasks with details
            'error_categories': {
                'client_lookup_email': 0,
                'client_lookup_phone': 0,
                'task_migration': 0,
                'data_validation': 0,
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
            'application_name': 'task_migration_v2_script'
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
            'application_name': 'task_migration_v2_script'
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
    
    def get_old_tasks(self) -> List[Dict[str, Any]]:
        """Fetch all task data from the old database."""
        try:
            with self.old_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                SELECT 
                    id,
                    created_at,
                    title,
                    description,
                    datetime,
                    duration,
                    hourly_rate,
                    email,
                    access_token,
                    first_name,
                    last_name,
                    phone,
                    school,
                    location_type,
                    client_id,
                    zip_code,
                    location_description,
                    completed,
                    special_perks,
                    tools_vehicle_required,
                    tools_vehicle_description,
                    public_transportation_accessible,
                    public_transportation_description,
                    task_images
                FROM tasks
                ORDER BY created_at
                """
                
                cursor.execute(query)
                tasks = cursor.fetchall()
                
                # Convert to regular dictionaries
                tasks_list = []
                for task in tasks:
                    task_dict = dict(task)
                    tasks_list.append(task_dict)
                
                logger.info(f"Found {len(tasks_list)} tasks in old database")
                return tasks_list
                
        except Exception as e:
            logger.error(f"Failed to fetch old tasks: {e}")
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
    
    def find_client_id_by_email(self, email: str) -> Optional[str]:
        """Find client ID by email in the new database."""
        try:
            if not email:
                return None
                
            with self.new_conn.cursor() as cursor:
                cursor.execute("SELECT id FROM public.clients WHERE email = %s", (email,))
                result = cursor.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            logger.error(f"Error looking up client by email {email}: {e}")
            return None
    
    def find_client_id_by_phone(self, phone: str) -> Optional[str]:
        """Find client ID by phone in the new database."""
        try:
            if not phone:
                return None
                
            normalized_phone = self.normalize_phone(phone)
            if not normalized_phone:
                return None
                
            with self.new_conn.cursor() as cursor:
                cursor.execute("SELECT id FROM public.clients WHERE phone = %s", (normalized_phone,))
                result = cursor.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            logger.error(f"Error looking up client by phone {phone}: {e}")
            return None
    
    def parse_datetime_to_dates_array(self, datetime_str: str) -> List[str]:
        """Parse datetime string and return as dates array."""
        if not datetime_str:
            return []
        
        try:
            # Try to parse the datetime string
            # This is a simplified parser - you may need to adjust based on your datetime format
            parsed_date = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return [parsed_date.isoformat()]
        except Exception as e:
            logger.warning(f"Could not parse datetime '{datetime_str}': {e}")
            # Return current date as fallback
            return [datetime.utcnow().isoformat()]
    
    def build_description(self, original_description: str, duration: str, location_description: str) -> str:
        """Build the new description field with additional information."""
        description_parts = []
        
        # Add original description if it exists
        if original_description:
            description_parts.append(original_description.strip())
        
        # Add duration if it exists
        if duration:
            description_parts.append(f"Duration: {duration}")
        
        # Add location description if it exists
        if location_description:
            description_parts.append(f"Location info: {location_description}")
        
        return "\n".join(description_parts)
    
    def build_tools_info(self, tools_required: str, tools_description: str) -> Optional[str]:
        """Build tools_info field from tools_vehicle_required and tools_vehicle_description."""
        tools_parts = []
        
        if tools_required:
            tools_parts.append(tools_required.strip())
        
        if tools_description:
            tools_parts.append(tools_description.strip())
        
        return "\n".join(tools_parts) if tools_parts else None
    
    def build_public_transport_info(self, transport_accessible: str, transport_description: str) -> Optional[str]:
        """Build public_transport_info field from transportation fields."""
        transport_parts = []
        
        if transport_accessible:
            transport_parts.append(transport_accessible.strip())
        
        if transport_description:
            transport_parts.append(transport_description.strip())
        
        return "\n".join(transport_parts) if transport_parts else None
    
    def migrate_task_data(self, task_data: Dict[str, Any]) -> bool:
        """Migrate a single task to the new schema."""
        try:
            # Start fresh transaction
            self.new_conn.rollback()
            
            with self.new_conn.cursor() as cursor:
                try:
                    # Find client ID by email first, then by phone
                    client_id = self.find_client_id_by_email(task_data.get('email'))
                    if not client_id:
                        client_id = self.find_client_id_by_phone(task_data.get('phone'))
                    
                    if not client_id:
                        error_msg = f"Could not find client for task {task_data.get('id')} - email: {task_data.get('email')}, phone: {task_data.get('phone')}"
                        logger.warning(error_msg)
                        self.migration_stats['client_lookups_failed'] += 1
                        self.migration_stats['tasks_skipped'] += 1
                        
                        # Track failed task details
                        failed_task = {
                            'task_id': task_data.get('id'),
                            'title': task_data.get('title', 'Untitled'),
                            'email': task_data.get('email'),
                            'phone': task_data.get('phone'),
                            'reason': 'Client lookup failed',
                            'error_details': error_msg
                        }
                        self.migration_stats['failed_tasks'].append(failed_task)
                        return False
                    
                    # Convert hourly rate from cents to dollars
                    hourly_rate_cents = task_data.get('hourly_rate', 0)
                    hourly_rate_dollars = float(hourly_rate_cents) / 100.0 if hourly_rate_cents else 0.0
                    
                    # Parse datetime to dates array
                    dates_array = self.parse_datetime_to_dates_array(task_data.get('datetime'))
                    
                    # Build description with additional info
                    new_description = self.build_description(
                        task_data.get('description', ''),
                        task_data.get('duration', ''),
                        task_data.get('location_description', '')
                    )
                    
                    # Build tools info
                    tools_info = self.build_tools_info(
                        task_data.get('tools_vehicle_required', ''),
                        task_data.get('tools_vehicle_description', '')
                    )
                    
                    # Build public transport info
                    public_transport_info = self.build_public_transport_info(
                        task_data.get('public_transportation_accessible', ''),
                        task_data.get('public_transportation_description', '')
                    )
                    
                    # Handle location type and zip code
                    location_type = task_data.get('location_type', 'remote')
                    zip_code = task_data.get('zip_code')
                    
                    # If no zip code, set location type to remote
                    if not zip_code:
                        location_type = 'remote'
                        zip_code = None
                    
                    # Set completed_at if task is completed
                    completed_at = None
                    if task_data.get('completed'):
                        completed_at = task_data.get('created_at')  # Use created_at as completion time
                    
                    # Insert into new tasks table
                    insert_query = """
                    INSERT INTO public.tasks (
                        id, client_id, title, dates, location_type, zip_code, description,
                        tools_info, public_transport_info, completed_at, created_at, updated_at, hourly_rate
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        client_id = EXCLUDED.client_id,
                        title = EXCLUDED.title,
                        dates = EXCLUDED.dates,
                        location_type = EXCLUDED.location_type,
                        zip_code = EXCLUDED.zip_code,
                        description = EXCLUDED.description,
                        tools_info = EXCLUDED.tools_info,
                        public_transport_info = EXCLUDED.public_transport_info,
                        completed_at = EXCLUDED.completed_at,
                        updated_at = EXCLUDED.updated_at,
                        hourly_rate = EXCLUDED.hourly_rate
                    """
                    
                    cursor.execute(insert_query, (
                        task_data.get('id'),
                        client_id,
                        task_data.get('title', 'Untitled Task'),
                        json.dumps(dates_array),
                        location_type,
                        zip_code,
                        new_description,
                        tools_info,
                        public_transport_info,
                        completed_at,
                        task_data.get('created_at'),
                        datetime.utcnow(),
                        hourly_rate_dollars
                    ))
                    
                    self.new_conn.commit()
                    logger.info(f"Successfully migrated task {task_data.get('id')}")
                    return True
                    
                except Exception as e:
                    self.new_conn.rollback()
                    error_msg = f"Database operation failed for task {task_data.get('id')}: {e}"
                    logger.error(error_msg)
                    self.migration_stats['error_categories']['task_migration'] += 1
                    
                    # Track failed task details
                    failed_task = {
                        'task_id': task_data.get('id'),
                        'title': task_data.get('title', 'Untitled'),
                        'email': task_data.get('email'),
                        'phone': task_data.get('phone'),
                        'reason': 'Database operation failed',
                        'error_details': error_msg
                    }
                    self.migration_stats['failed_tasks'].append(failed_task)
                    return False
                
        except Exception as e:
            self.new_conn.rollback()
            error_msg = f"Failed to migrate task data for {task_data.get('id')}: {e}"
            logger.error(error_msg)
            self.migration_stats['error_categories']['task_migration'] += 1
            
            # Track failed task details
            failed_task = {
                'task_id': task_data.get('id'),
                'title': task_data.get('title', 'Untitled'),
                'email': task_data.get('email'),
                'phone': task_data.get('phone'),
                'reason': 'Migration failed',
                'error_details': error_msg
            }
            self.migration_stats['failed_tasks'].append(failed_task)
            return False
    
    def run_migration(self) -> bool:
        """Run the complete migration process."""
        try:
            logger.info("Starting task migration from old schema to new HelperU_v2 schema...")
            
            # Get all tasks from old database
            old_tasks = self.get_old_tasks()
            if not old_tasks:
                logger.warning("No tasks found in old database")
                return True
            
            self.migration_stats['tasks_found'] = len(old_tasks)
            
            # Process each task
            for task_data in old_tasks:
                try:
                    logger.info(f"Processing task: {task_data.get('title', 'Untitled')} (ID: {task_data.get('id')})")
                    
                    # Migrate task data
                    if self.migrate_task_data(task_data):
                        self.migration_stats['tasks_migrated'] += 1
                    else:
                        self.migration_stats['tasks_skipped'] += 1
                    
                except Exception as e:
                    error_msg = f"Failed to process task {task_data.get('id')}: {e}"
                    logger.error(error_msg)
                    self.migration_stats['errors'].append(error_msg)
                    self.migration_stats['error_categories']['other'] += 1
                    
                    # Track failed task details
                    failed_task = {
                        'task_id': task_data.get('id'),
                        'title': task_data.get('title', 'Untitled'),
                        'email': task_data.get('email'),
                        'phone': task_data.get('phone'),
                        'reason': 'Processing failed',
                        'error_details': error_msg
                    }
                    self.migration_stats['failed_tasks'].append(failed_task)
            
            # Log migration summary
            self.log_migration_summary()
            
            # Save failed tasks to CSV
            self.save_failed_tasks_to_csv()
            
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def log_migration_summary(self):
        """Log a summary of the migration results."""
        logger.info("=" * 60)
        logger.info("TASK MIGRATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total tasks found: {self.migration_stats['tasks_found']}")
        logger.info(f"Tasks successfully migrated: {self.migration_stats['tasks_migrated']}")
        logger.info(f"Tasks skipped: {self.migration_stats['tasks_skipped']}")
        logger.info(f"Client lookups failed: {self.migration_stats['client_lookups_failed']}")
        logger.info(f"Total errors: {len(self.migration_stats['errors'])}")
        
        if self.migration_stats['errors']:
            logger.info("\nError Categories:")
            for category, count in self.migration_stats['error_categories'].items():
                if count > 0:
                    logger.info(f"  {category}: {count}")
        
        # Print failed tasks details
        if self.migration_stats['failed_tasks']:
            logger.info(f"\nFAILED TASKS ({len(self.migration_stats['failed_tasks'])}):")
            logger.info("-" * 60)
            for i, task in enumerate(self.migration_stats['failed_tasks'], 1):
                logger.info(f"{i}. Task ID: {task['task_id']}")
                logger.info(f"   Title: {task['title']}")
                logger.info(f"   Email: {task['email']}")
                logger.info(f"   Phone: {task['phone']}")
                logger.info(f"   Reason: {task['reason']}")
                logger.info(f"   Error: {task['error_details']}")
                logger.info("-" * 40)
        
        logger.info("=" * 60)
    
    def save_failed_tasks_to_csv(self, filename: str = "failed_tasks.csv"):
        """Save failed tasks to a CSV file for analysis."""
        if not self.migration_stats['failed_tasks']:
            logger.info("No failed tasks to save to CSV")
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['task_id', 'title', 'email', 'phone', 'reason', 'error_details']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for task in self.migration_stats['failed_tasks']:
                    writer.writerow(task)
            
            logger.info(f"Failed tasks saved to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save failed tasks to CSV: {e}")


@click.command()
@click.option('--dry-run', is_flag=True, help='Run migration without making changes')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def main(dry_run: bool, verbose: bool):
    """Migrate task data from old schema to new HelperU_v2 schema."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    migrator = TaskV2Migrator()
    
    try:
        # Connect to databases
        if not migrator.connect_databases():
            logger.error("Failed to connect to databases")
            sys.exit(1)
        
        if dry_run:
            logger.info("DRY RUN MODE: No changes will be made")
            # In dry run mode, just fetch and display what would be migrated
            old_tasks = migrator.get_old_tasks()
            logger.info(f"Would migrate {len(old_tasks)} tasks")
            for task in old_tasks[:5]:  # Show first 5 as sample
                logger.info(f"Sample: {task.get('title', 'Untitled')} - {task.get('email', 'No email')}")
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
