"""Task tools for AI agents

This module provides comprehensive tools for AI agents to interact with the task management system.
It includes functions for creating, reading, updating, deleting, and searching tasks, as well as
managing task completion status. All functions are designed to work with LangChain's tool system
and return serializable JSON responses.
"""

from typing import Optional, List
from fastapi import HTTPException
from app.deps.supabase import get_task_service, get_stripe_service

from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskSearchRequest,
    TaskResponse,
    TaskSearchResponse,
    TaskListResponse
)
from langchain.tools import tool

# Global service instances
task_service = get_task_service()
stripe_service = get_stripe_service()

# For tool decorator in langchain tools, the name is inferred from the function name,
# but can be overridden with the name parameter. Description is inferred from the docstring.
# The return type is inferred from the return type of the function.
# The arguments are inferred from the function arguments.
# The function must be a coroutine function.
# The function must return a value that can be serialized to JSON.

@tool
async def create_task(client_id: str, 
    title: str, 
    description: str, 
    dates: List[str], 
    location_type: str, 
    zip_code: Optional[str], 
    hourly_rate: float, 
    tools_info: Optional[str],
    public_transport_info: Optional[str]
) -> TaskResponse:
    """Create a new task in the system.
    
    This function allows AI agents to create new tasks on behalf of clients.
    The task will be stored in the database and made available for helpers to
    discover and apply for. Only open tasks (not completed) are searchable.
    
    Args:
        client_id (str): The unique identifier of the client creating the task.
                        Must be a valid UUID string.
        title (str): A concise, descriptive title for the task that clearly
                    indicates what needs to be done. Should be 3-100 characters.
        description (str): A detailed description of the task requirements,
                            including specific instructions, expectations, and
                            any important details helpers should know.
        dates (List[str]): A list of date strings when the task needs to be
                            completed. Format should be ISO 8601 (YYYY-MM-DD).
                            Multiple dates indicate flexibility in scheduling.
        location_type (str): The type of location where the task will be
                            performed. Options include: 'remote', 'on_site',
                            'hybrid', or other location-specific categories.
        zip_code (Optional[str]): The ZIP code where the task will be performed.
                                    Required for on-site tasks, optional for remote.
                                    Must be a valid US ZIP code format.
        hourly_rate (float): The hourly rate in dollars that the client is
                            willing to pay for this task. Must be a positive
                            number representing the compensation per hour.
        tools_info (Optional[str]): Information about tools or equipment that
                                    will be provided or required for the task.
                                    Can include tool lists, specifications, or
                                    availability details.
        public_transport_info (Optional[str]): Information about public
                                                transportation options near the
                                                task location. Useful for helpers
                                                planning their commute.
    
    Returns:
        TaskResponse: A complete task object containing all the created task
                        details including the generated UUID, timestamps, and
                        formatted data. The response includes id, client_id,
                        hourly_rate, title, dates (as JSONB), location_type,
                        zip_code, description, tools_info, public_transport_info,
                        completed_at (null for new tasks), created_at, and updated_at.
    
    Raises:
        HTTPException: Returns a 500 status code with error details if the
                        task creation fails due to validation errors, database
                        issues, or other system problems.
    
    Example:
        >>> result = await create_task(
        ...     client_id="123e4567-e89b-12d3-a456-426614174000",
        ...     title="Help with moving furniture",
        ...     description="Need help moving heavy furniture from living room to garage",
        ...     dates=["2024-01-15", "2024-01-16"],
        ...     location_type="on_site",
        ...     zip_code="12345",
        ...     hourly_rate=25.0,
        ...     tools_info="Moving blankets and dollies provided",
        ...     public_transport_info="Bus route 15 stops 2 blocks away"
        ... )
    """
    try:
        request = TaskCreate(
            title=title,
            description=description,
            dates=dates,
            location_type=location_type,
            zip_code=zip_code,
            hourly_rate=hourly_rate,
            tools_info=tools_info,
            public_transport_info=public_transport_info
        )
        result = await task_service.create_task(client_id, request)
        if not result:
            return HTTPException(status_code=500, detail="Failed to create task")
        return result
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@tool
async def get_task(task_id: str) -> TaskResponse:
    """Retrieve a single task by its unique identifier.
    
    This function fetches the complete details of a specific task from the
    database. It's useful for AI agents that need to examine task details,
    verify task information, or retrieve task data for helpers or further processing.
    
    Args:
        task_id (str): The unique identifier of the task to retrieve.
                        Must be a valid UUID string that exists in the system.
    
    Returns:
        TaskResponse: A complete task object containing all task details
                        including id, client_id, hourly_rate, title, dates,
                        location_type, zip_code, description, tools_info,
                        public_transport_info, completed_at, created_at, and updated_at.
                        If the task is completed, completed_at will contain a timestamp.
    
    Raises:
        HTTPException: Returns a 404 status code if the task_id doesn't exist
                        in the system, or a 500 status code for other errors
                        like database connection issues or validation problems.
    
    Example:
        >>> task = await get_task("123e4567-e89b-12d3-a456-426614174000")
        >>> print(f"Task: {task.title} - Rate: ${task.hourly_rate}/hr")
    """
    try:
        result = await task_service.get_task(task_id)
        if not result:
            return HTTPException(status_code=404, detail="Task not found")
        
        return TaskResponse(**result)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
    
@tool
async def update_task(
    task_id: str, 
    user_id: str,
    title: Optional[str], 
    description: Optional[str], 
    dates: Optional[List[str]], 
    location_type: Optional[str], 
    zip_code: Optional[str], 
    hourly_rate: Optional[float], 
    tools_info: Optional[str],
    public_transport_info: Optional[str]) -> TaskResponse:
    """Update an existing task with new information.
    
    This function allows AI agents to modify task details on behalf of authorized client users.
    Only the fields that need to be updated should be provided - omitted fields will retain their current values. This is useful
    provided - omitted fields will retain their current values. This is useful
    for correcting errors, updating requirements, or adjusting task parameters.
    
    Args:
        task_id (str): The unique identifier of the task to update.
                        Must be a valid UUID string that exists in the system.
        user_id (str): The unique identifier of the user requesting the update.
                        Must have permission to modify this specific task.
                        Usually the client who created the task or an admin.
        title (Optional[str]): New title for the task. If provided, must be
                                3-100 characters and clearly describe the task.
        description (Optional[str]): Updated description of the task requirements.
                                    Can include new instructions, clarifications,
                                    or additional details.
        dates (Optional[List[str]]): New list of dates when the task needs to
                                    be completed. Format should be ISO 8601
                                    (YYYY-MM-DD). Useful for rescheduling.
        location_type (Optional[str]): New location type for the task.
                                        Options include: 'remote', 'on_site',
                                        'hybrid', or other location categories.
        zip_code (Optional[str]): New ZIP code for the task location.
                                    Required for on-site tasks, optional for remote.
                                    Must be a valid US ZIP code format.
        hourly_rate (Optional[float]): New hourly rate in dollars for the task.
                                        Must be a positive number representing
                                        the updated compensation per hour.
        tools_info (Optional[str]): Updated information about tools or equipment
                                    for the task. Can include new tool requirements
                                    or availability changes.
        public_transport_info (Optional[str]): Updated public transportation
                                                information for the task location.
                                                Useful if the location has changed.
    
    Returns:
        TaskResponse: The updated task object containing all current task details
                        including the modified fields and updated timestamps.
                        The response includes id, client_id, hourly_rate, title,
                        dates, location_type, zip_code, description, tools_info,
                        public_transport_info, completed_at, created_at, and updated_at.
    
    Raises:
        HTTPException: Returns a 404 status code if the task_id doesn't exist,
                        a 403 status code if the user lacks permission to update
                        the task, or a 500 status code for other system errors.
    
    Example:
        >>> updated_task = await update_task(
        ...     task_id="123e4567-e89b-12d3-a456-426614174000",
        ...     user_id="client-uuid-here",
        ...     hourly_rate=30.0,
        ...     description="Updated: Also need help with organizing after moving"
        ... )
    """
    try:
        request = TaskUpdate(
            title=title,
            description=description,
            dates=dates,
            location_type=location_type,
            zip_code=zip_code,
            hourly_rate=hourly_rate,
            tools_info=tools_info,
            public_transport_info=public_transport_info
        )
        result = await task_service.update_task(task_id, user_id, request)
        if not result:
            return HTTPException(status_code=500, detail="Failed to update task")
        return result
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@tool
async def delete_task(task_id: str, user_id: str) -> bool:
        """Permanently remove a task from the system.
        
        This function allows AI agents to delete tasks on behalf of authorized client users.
        Deletion is permanent and cannot be undone. This is typically used when
        a task is no longer needed, was created in error, or needs to be completely
        removed from the system. Only the task creator or authorized administrators
        should be able to delete tasks.
        
        Args:
            task_id (str): The unique identifier of the task to delete.
                          Must be a valid UUID string that exists in the system.
            user_id (str): The unique identifier of the user requesting the deletion.
                          Must have permission to delete this specific task.
                          Usually the client who created the task or an admin.
        
        Returns:
            bool: True if the task was successfully deleted, indicating the
                  operation completed successfully and the task no longer exists
                  in the system.
        
        Raises:
            HTTPException: Returns a 404 status code if the task_id doesn't exist,
                          a 403 status code if the user lacks permission to delete
                          the task, or a 500 status code for other system errors
                          like database connection issues.
        
        Example:
            >>> success = await delete_task(
            ...     task_id="123e4567-e89b-12d3-a456-426614174000",
            ...     user_id="client-uuid-here"
            ... )
            >>> if success:
            ...     print("Task successfully deleted")
        """
        try:
            result = await task_service.delete_task(task_id, user_id)
            if not result:
                return HTTPException(status_code=500, detail="Failed to delete task")
            return result 
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))

@tool
async def search_tasks(
    search_zip_code: Optional[str], 
    query: Optional[str], 
    location_type: Optional[str], 
    min_hourly_rate: Optional[float], 
    max_hourly_rate: Optional[float], 
    limit: int = 20, 
    offset: int = 0
) -> TaskSearchResponse:
    """Search for tasks based on multiple criteria with distance calculation.
    
    This function provides comprehensive task search functionality for AI agents
    to help helper users find relevant tasks. It uses the database's distance calculation
    functions to sort results by proximity to a specified ZIP code, making it
    easy to find nearby opportunities. The search automatically filters out
    completed tasks, ensuring only available/open tasks are returned for helpers.
    
    Args:
        search_zip_code (Optional[str]): The ZIP code to search from for distance
                                        calculation. If provided, results will be
                                        sorted by distance from this location.
                                        Must be a valid US ZIP code format.
                                        If not provided, distance sorting is disabled.
        query (Optional[str]): Text search term to match against task titles and
                                descriptions. Uses case-insensitive partial matching.
                                Can include keywords, phrases, or specific requirements.
        location_type (Optional[str]): Filter tasks by specific location type.
                                        Options include: 'remote', 'on_site', 'hybrid',
                                        or other location categories. If not specified,
                                        all location types are included.
        min_hourly_rate (Optional[float]): Minimum hourly rate filter in dollars.
                                            Only tasks with hourly_rate >= this value
                                            will be returned. Useful for finding
                                            well-paying opportunities.
        max_hourly_rate (Optional[float]): Maximum hourly rate filter in dollars.
                                            Only tasks with hourly_rate <= this value
                                            will be returned. Useful for budget
                                            constraints or rate expectations.
        limit (int): Maximum number of tasks to return in a single search.
                    Default is 20, maximum recommended is 100 for performance.
                    Useful for pagination and controlling result set size.
        offset (int): Number of tasks to skip for pagination. Default is 0.
                        Use this with limit to implement pagination: offset=20
                        would skip the first 20 results, offset=40 would skip
                        the first 40, etc.
    
    Returns:
        TaskSearchResponse: A structured response containing the search results
                            including a list of matching tasks with distance
                            calculations (if zip_code provided), total count,
                            and pagination information. Each task includes all
                            standard fields plus a distance field in miles.
    
    Raises:
        HTTPException: Returns a 404 status code if no tasks match the criteria,
                        a 400 status code if the search parameters are invalid
                        (e.g., invalid ZIP code), or a 500 status code for
                        other system errors.
    
    Example:
        >>> results = await search_tasks(
        ...     search_zip_code="12345",
        ...     query="moving help",
        ...     location_type="on_site",
        ...     min_hourly_rate=20.0,
        ...     max_hourly_rate=50.0,
        ...     limit=10,
        ...     offset=0
        ... )
        >>> for task in results.tasks:
        ...     print(f"{task.title} - {task.distance} miles away")
    """
    try:
        request = TaskSearchRequest(
            search_zip_code=search_zip_code,
            query=query,
            location_type=location_type,
            min_hourly_rate=min_hourly_rate,
            max_hourly_rate=max_hourly_rate,
            limit=limit,
            offset=offset
        )
        result = await task_service.search_tasks(request)
        if not result:
            return HTTPException(status_code=404, detail="No tasks found")
        return result
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

    
@tool
async def get_user_tasks(
    user_id: str, 
    limit: int = 20, 
    offset: int = 0
) -> TaskListResponse:
    """Retrieve all tasks associated with a specific user.
    
    This function allows AI agents to fetch all tasks that a particular user
    has created (as a client). It's useful for
    providing users with an overview of their task history, current open tasks,
    and completed work. The function supports pagination for users with many tasks.
    
    Args:
        user_id (str): The unique identifier of the user whose tasks to retrieve.
                        Must be a valid UUID string that exists in the system.
                        Can be either a client (task creator) or helper (task applicant).
        limit (int): Maximum number of tasks to return in a single request.
                    Default is 20, maximum recommended is 100 for performance.
                    Useful for pagination and controlling result set size.
        offset (int): Number of tasks to skip for pagination. Default is 0.
                        Use this with limit to implement pagination: offset=20
                        would skip the first 20 results, offset=40 would skip
                        the first 40, etc.
    
    Returns:
        TaskListResponse: A structured response containing a list of tasks
                            associated with the specified user, including both
                            open and completed tasks. Each task includes all
                            standard fields: id, client_id, hourly_rate, title,
                            dates, location_type, zip_code, description, tools_info,
                            public_transport_info, completed_at, created_at, and updated_at.
    
    Raises:
        HTTPException: Returns a 404 status code if no tasks are found for
                        the user, a 400 status code if the user_id is invalid,
                        or a 500 status code for other system errors like
                        database connection issues.
    
    Example:
        >>> user_tasks = await get_user_tasks(
        ...     user_id="client-uuid-here",
        ...     limit=50,
        ...     offset=0
        ... )
        >>> open_tasks = [t for t in user_tasks.tasks if t.completed_at is None]
        >>> completed_tasks = [t for t in user_tasks.tasks if t.completed_at is not None]
    """
    try:
        result = await task_service.get_user_tasks(user_id, limit, offset)
        if not result:
            return HTTPException(status_code=404, detail="No tasks found")
        
        return result
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@tool
async def complete_task(task_id: str, user_id: str) -> bool:
    """Mark a task as completed and update its status.
    
    This function allows AI agents to mark tasks as completed on behalf of
    authorized client users. When a task is completed, it's no longer searchable
    or available for new applications by helpers. The
    completed_at timestamp is automatically set to the current time.
    
    Args:
        task_id (str): The unique identifier of the task to mark as completed.
                        Must be a valid UUID string that exists in the system
                        and is currently in an open/active state.
        user_id (str): The unique identifier of the user requesting the completion.
                        Must have permission to complete this specific task.
                        Usually the client who created the task, the helper who
                        completed it, or an authorized administrator.
    
    Returns:
        bool: True if the task was successfully marked as completed,
                indicating the operation completed successfully and the task
                is now in a completed state and no longer searchable.
    
    Raises:
        HTTPException: Returns a 404 status code if the task_id doesn't exist,
                        a 400 status code if the task is already completed,
                        a 403 status code if the user lacks permission to
                        complete the task, or a 500 status code for other
                        system errors.
    
    Example:
        >>> success = await complete_task(
        ...     task_id="123e4567-e89b-12d3-a456-426614174000",
        ...     user_id="helper-uuid-here"
        ... )
        >>> if success:
        ...     print("Task marked as completed successfully")
    """
    try:
        result = await task_service.complete_task(task_id, user_id)
        if not result:
            return HTTPException(status_code=500, detail="Failed to complete task")
        
        return result
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@tool
async def get_remaining_post_limit(user_id: str) -> int:
    """Retrieve the remaining number of task posts a user can create before reaching their limit.
    
    This function allows AI agents to check a clientuser's remaining task posting capacity
    before they attempt to create a new task. This is crucial for subscription-based
    limits where users have a maximum number of tasks they can post based on their
    current plan or subscription tier. The function helps prevent users from hitting
    posting limits unexpectedly and provides transparency about their usage.
    
    Args:
        user_id (str): The unique identifier of the user whose remaining post limit
                        to check. Must be a valid UUID string that exists in the system.
                        This will return the remaining task posting capacity for this
                        specific user based on their current subscription plan.
    
    Returns:
        int: The number of remaining task posts the user can create before reaching
                their limit. A positive integer (0 or greater) indicating available
                posting capacity. If the user has unlimited posts, this will return
                a very large number.
    
    Raises:
        HTTPException: Returns a 404 status code if the user_id doesn't exist
                        in the system, or a 500 status code for other errors
                        like database connection issues, Stripe API problems,
                        or subscription validation failures.
    
    Example:
        >>> remaining_posts = await get_remaining_post_limit("user-uuid-here")
        >>> if remaining_posts > 0:
        ...     print(f"You can create {remaining_posts} more tasks")
        ... else:
        ...     print("You have reached your task posting limit")
    """
    try:
        result = await stripe_service.get_monthly_post_limit(user_id)
        return result
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
