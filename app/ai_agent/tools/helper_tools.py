"""Helper tools for AI agents

This module provides comprehensive tools for AI agents to interact with the helper
management system. It includes functions for retrieving helper information, searching
for helpers based on various criteria, and managing helper data. All functions are
designed to work with LangChain's tool system and return serializable JSON responses.
"""

from typing import Optional
from app.deps.supabase import get_helper_service
from app.schemas.helper import (
    HelperResponse, 
    HelperListResponse, 
    HelperSearchRequest
)
from langchain.tools import tool
from fastapi import HTTPException

# Global service instance
helper_service = get_helper_service()
    
@tool
async def get_helper(helper_id: str) -> HelperResponse:
        """Retrieve detailed information for a specific helper.
        
        This function allows AI agents to fetch the complete profile information
        for a specific helper user. This is useful for displaying helper details,
        evaluating helper qualifications, retrieving helper information for task
        matching, or providing helper data for further processing. The function
        returns comprehensive helper information while excluding sensitive fields
        like phone numbers and email addresses for privacy and security.
        
        Args:
            helper_id (str): The unique identifier of the helper to retrieve.
                            Must be a valid UUID string that exists in the system.
                            This will return the complete helper profile including
                            all public information like name, college, bio, skills,
                            and location details.
        
        Returns:
            HelperResponse: A complete helper profile object containing all
                            public helper information. Fields include:
                            - id (str): Unique helper identifier
                            - first_name (str): Helper's first name
                            - last_name (str): Helper's last name
                            - college (str): Name of the college/university
                            - bio (str): Helper's biography/description
                            - graduation_year (int): Year of graduation
                            - zip_code (str): ZIP code for location
                            - pfp_url (Optional[str]): Profile picture URL
        
        Raises:
            HTTPException: Returns a 404 status code if the helper_id doesn't
                          exist in the system, or a 500 status code for other
                          errors like database connection issues or validation
                          problems. Common errors include: helper not found,
                          invalid UUID format, or database access issues.
        
        Example:
            >>> helper = await get_helper("helper-uuid-here")
            >>> print(f"Helper: {helper.first_name} {helper.last_name}")
            >>> print(f"College: {helper.college}")
            >>> print(f"Bio: {helper.bio}")
        """
        try:
            result = await helper_service.get_helper(helper_id)
            if not result:
                return HTTPException(status_code=500, detail="Failed to get helper")
            return result
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
    
@tool
async def get_helpers(limit: int = 20, offset: int = 0) -> HelperListResponse:
        """Retrieve a paginated list of all helpers in the system.
        
        This function allows AI agents to fetch a list of all helper users
        in the system with pagination support. This is useful for displaying
        helper directories, browsing available helpers, or retrieving helper
        data for bulk operations. The function provides efficient pagination
        to handle large numbers of helpers without overwhelming the system.
        
        Args:
            limit (int): Maximum number of helpers to return in a single
                        request. Default is 20, maximum recommended is 100
                        for performance. Useful for pagination and controlling
                        result set size. Smaller limits provide faster response
                        times and better user experience.
            offset (int): Number of helpers to skip for pagination. Default
                         is 0. Use this with limit to implement pagination:
                         offset=20 would skip the first 20 helpers, offset=40
                         would skip the first 40, etc. This enables efficient
                         browsing through large helper databases.
        
        Returns:
            HelperListResponse: A structured response containing a list of
                                helpers with pagination metadata. Fields include:
                                - helpers (List[HelperResponse]): List of helper profiles
                                - total_count (int): Total number of helpers in the system
                                - limit (int): Number of helpers returned
                                - offset (int): Number of helpers skipped
                                
                                Each HelperResponse includes:
                                - id (str): Unique helper identifier
                                - first_name (str): Helper's first name
                                - last_name (str): Helper's last name
                                - college (str): Name of the college/university
                                - bio (str): Helper's biography/description
                                - graduation_year (int): Year of graduation
                                - zip_code (str): ZIP code for location
                                - pfp_url (Optional[str]): Profile picture URL
        
        Raises:
            HTTPException: Returns a 404 status code if no helpers are found
                          in the system, or a 500 status code for other errors
                          like database connection issues or validation problems.
                          Common errors include: database connection failure,
                          query execution errors, or data processing issues.
        
        Example:
            >>> helpers = await get_helpers(limit=10, offset=0)
            >>> print(f"Retrieved {len(helpers.helpers)} helpers")
            >>> print(f"Total helpers in system: {helpers.total_count}")
            >>> for helper in helpers.helpers:
            ...     print(f"- {helper.first_name} {helper.last_name} from {helper.college}")
        """
        try:
            result = await helper_service.get_helpers(limit, offset)
            if not result:
                return HTTPException(status_code=500, detail="Failed to get helpers")
            return result
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
    
@tool
async def search_helpers(
                           search_query: Optional[str] = None,
                           search_college: Optional[str] = None,
                           search_graduation_year: Optional[int] = None,
                           search_zip_code: Optional[str] = None,
                           limit: int = 20,
                           offset: int = 0) -> HelperListResponse:
        """Search for helpers based on multiple criteria with advanced filtering.
        
        This function allows AI agents to perform sophisticated searches for
        helpers based on various criteria including text search, college
        preferences, graduation year, and location. This is useful for finding
        helpers that match specific requirements, filtering helpers by location
        or education, or discovering helpers with particular skills or backgrounds.
        The search uses the database's optimized search functions for efficient
        results and supports pagination for large result sets.
        
        Args:
            search_query (Optional[str]): Text search term to match against
                                         helper names, bio, and college information.
                                         Uses case-insensitive partial matching and
                                         full-text search capabilities. Can include
                                         keywords, phrases, or specific requirements.
                                         If not provided, text search is disabled.
            search_college (Optional[str]): Filter helpers by specific college or
                                           university name. Uses case-insensitive
                                           partial matching. If not specified,
                                           all colleges are included in results.
                                           Useful for finding helpers from specific
                                           institutions or educational backgrounds.
            search_graduation_year (Optional[int]): Filter helpers by specific
                                                   graduation year. Must be a valid
                                                   year (typically 4 digits, e.g.,
                                                   2024). If not specified, all
                                                   graduation years are included.
                                                   Useful for finding helpers with
                                                   specific educational timelines.
            search_zip_code (Optional[str]): Filter helpers by specific ZIP code
                                            location. Must be a valid US ZIP code
                                            format (5 digits). If not specified,
                                            all locations are included. Useful for
                                            finding helpers in specific geographic
                                            areas for location-based tasks.
            limit (int): Maximum number of helpers to return in a single search.
                        Default is 20, maximum recommended is 100 for performance.
                        Useful for pagination and controlling result set size.
                        Smaller limits provide faster response times.
            offset (int): Number of helpers to skip for pagination. Default is 0.
                         Use this with limit to implement pagination: offset=20
                         would skip the first 20 results, offset=40 would skip
                         the first 40, etc. Enables efficient browsing through
                         large search result sets.
        
        Returns:
            HelperListResponse: A structured response containing search results
                               with pagination metadata. Fields include:
                               - helpers (List[HelperResponse]): List of matching helper profiles
                               - total_count (int): Number of helpers matching the search criteria
                               - limit (int): Number of helpers returned
                               - offset (int): Number of helpers skipped
                               
                               Each HelperResponse includes:
                               - id (str): Unique helper identifier
                               - first_name (str): Helper's first name
                               - last_name (str): Helper's last name
                               - college (str): Name of the college/university
                               - bio (str): Helper's biography/description
                               - graduation_year (int): Year of graduation
                               - zip_code (str): ZIP code for location
                               - pfp_url (Optional[str]): Profile picture URL
        
        Raises:
            HTTPException: Returns a 500 status code with error details if the
                          search fails due to database issues, invalid search
                          parameters, or other system problems. Common errors
                          include: database connection issues, invalid ZIP code
                          format, or search function execution failures.
        
        Example:
            >>> results = await search_helpers(
            ...     search_query="moving furniture",
            ...     search_college="University of Technology",
            ...     search_graduation_year=2023,
            ...     search_zip_code="12345",
            ...     limit=10,
            ...     offset=0
            ... )
            >>> print(f"Found {results.total_count} matching helpers")
            >>> for helper in results.helpers:
            ...     print(f"- {helper.first_name} {helper.last_name} from {helper.college}")
        """
        try:
            search_request = HelperSearchRequest(
                search_query=search_query,
                search_college=search_college,
                search_graduation_year=search_graduation_year,
                search_zip_code=search_zip_code,
                limit=limit,
                offset=offset
            )
            result = await helper_service.search_helpers(search_request)
            if not result:
                return HTTPException(status_code=500, detail="Failed to search helpers")
            return result
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))