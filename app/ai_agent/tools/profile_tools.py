"""Profile tools for AI agents

This module provides comprehensive tools for AI agents to interact with the user
profile management system. It includes functions for retrieving profile completion
status, fetching client and helper profiles, and updating profile information
for both user types. All functions are designed to work with LangChain's tool
system and return serializable JSON responses.
"""

from typing import Optional
from app.deps.supabase import get_profile_service
from langchain.tools import tool
from app.schemas.profile import (
    UserProfileStatusResponse,
    ClientProfileData,
    HelperProfileData,
    ProfileUpdateResponse,
    ProfileUpdateData
)
from fastapi import HTTPException

# Global service instance
profile_service = get_profile_service()
    
    
@tool
async def get_user_profile_status(user_id: str) -> UserProfileStatusResponse:
        """Retrieve the profile completion status for a specific user.
        
        This function allows AI agents to check how complete a user's profile is
        and what information might still be needed. This is useful for determining
        whether a user can access certain features, guiding users through profile
        completion, or assessing the quality of user data in the system. The
        status helps identify which profile sections need attention.
        
        Args:
            user_id (str): The unique identifier of the user whose profile status
                          to retrieve. Must be a valid UUID string that exists in
                          the system. This will return the completion status for
                          this specific user regardless of whether they are a
                          client or helper.
        
        Returns:
            UserProfileStatusResponse: A structured response containing the user's
                                      profile completion status. Fields include:
                                      - user_type (str): Type of user ("client" or "helper")
                                      - profile_completed (bool): Whether the profile is complete
                                      - email_verified (bool): Whether email is verified
                                      - phone_verified (bool): Whether phone is verified
                                      - profile_data (Optional[dict]): Profile data (ClientProfileData or HelperProfileData)
        
        Raises:
            HTTPException: Returns a 500 status code with error details if the
                          profile status retrieval fails due to database issues,
                          user not found, or other system problems.
        
        Example:
            >>> status = await get_user_profile_status("user-uuid-here")
            >>> print(f"Profile completion: {status.completion_percentage}%")
            >>> if not status.is_complete:
            ...     print("Missing sections:", status.missing_sections)
        """
        try:
            result = await profile_service.get_user_profile_status(user_id)
            if not result:
                return HTTPException(status_code=500, detail="Failed to get user profile status")
            return result
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
    
@tool
async def get_client_profile(user_id: str) -> ClientProfileData:
        """Retrieve the complete profile data for a client user.
        
        This function allows AI agents to fetch the full profile information for
        a specific client user. This is useful for displaying client information,
        verifying client details, personalizing user experiences, or retrieving
        client data for further processing. Client profiles contain basic personal
        information and preferences relevant to task creation and management.
        
        Args:
            user_id (str): The unique identifier of the client user whose profile
                          to retrieve. Must be a valid UUID string that exists in
                          the system and corresponds to a client account type.
                          This will return the complete client profile including
                          all personal and preference information.
        
        Returns:
            ClientProfileData: A complete client profile object containing all
                              client-specific information. Fields include:
                              - id (str): Unique client identifier
                              - first_name (Optional[str]): Client's first name
                              - last_name (Optional[str]): Client's last name
                              - phone (Optional[str]): Client's phone number
                              - email (Optional[str]): Client's email address
                              - pfp_url (Optional[str]): Profile picture URL
                              - number_of_posts (Optional[int]): Number of tasks posted
                              - created_at (Optional[datetime]): Account creation timestamp
                              - updated_at (Optional[datetime]): Last update timestamp
        
        Raises:
            HTTPException: Returns a 500 status code with error details if the
                          client profile retrieval fails due to database issues,
                          user not found, or other system problems. Common errors
                          include: user doesn't exist, user is not a client type,
                          or profile data is corrupted.
        
        Example:
            >>> client_profile = await get_client_profile("client-uuid-here")
            >>> print(f"Client: {client_profile.first_name} {client_profile.last_name}")
            >>> if client_profile.pfp_url:
            ...     print(f"Profile picture: {client_profile.pfp_url}")
        """
        try:
            result = await profile_service.get_client_profile(user_id)
            if not result:
                return HTTPException(status_code=500, detail="Failed to get client profile")
            return result
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
    
@tool
async def get_helper_profile(user_id: str) -> HelperProfileData:
        """Retrieve the complete profile data for a helper user.
        
        This function allows AI agents to fetch the full profile information for
        a specific helper user. This is useful for displaying helper information,
        evaluating helper qualifications, matching helpers to tasks, or retrieving
        helper data for further processing. Helper profiles contain comprehensive
        information including education, skills, location, and availability details
        that are crucial for task matching and client decision-making.
        
        Args:
            user_id (str): The unique identifier of the helper user whose profile
                          to retrieve. Must be a valid UUID string that exists in
                          the system and corresponds to a helper account type.
                          This will return the complete helper profile including
                          all professional, educational, and personal information.
        
        Returns:
            HelperProfileData: A complete helper profile object containing all
                              helper-specific information. Fields include:
                              - id (str): Unique helper identifier
                              - first_name (Optional[str]): Helper's first name
                              - last_name (Optional[str]): Helper's last name
                              - email (Optional[str]): Helper's email address
                              - phone (Optional[str]): Helper's phone number
                              - college (Optional[str]): Name of the college/university
                              - bio (Optional[str]): Helper's biography/description
                              - graduation_year (Optional[int]): Year of graduation
                              - zip_code (Optional[str]): ZIP code for location
                              - pfp_url (Optional[str]): Profile picture URL
                              - number_of_applications (Optional[int]): Number of applications submitted
                              - created_at (Optional[datetime]): Account creation timestamp
                              - updated_at (Optional[datetime]): Last update timestamp
        
        Raises:
            HTTPException: Returns a 500 status code with error details if the
                          helper profile retrieval fails due to database issues,
                          user not found, or other system problems. Common errors
                          include: user doesn't exist, user is not a helper type,
                          or profile data is corrupted.
        
        Example:
            >>> helper_profile = await get_helper_profile("helper-uuid-here")
            >>> print(f"Helper: {helper_profile.first_name} {helper_profile.last_name}")
            >>> print(f"College: {helper_profile.college}")
            >>> print(f"Graduation Year: {helper_profile.graduation_year}")
            >>> print(f"Bio: {helper_profile.bio}")
        """
        try:
            result = await profile_service.get_helper_profile(user_id)
            if not result:
                return HTTPException(status_code=500, detail="Failed to get helper profile")
            return result
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
    
@tool
async def update_client_profile(user_id: str,
        first_name: Optional[str],
        last_name: Optional[str],
        pfp_url: Optional[str]) -> ProfileUpdateResponse:
        """Update the profile information for a client user.
        
        This function allows AI agents to modify client profile details on behalf
        of users or authorized administrators. Only the fields that need to be
        updated should be provided - omitted fields will retain their current
        values. This is useful for clients who want to update their personal
        information, change their profile picture, or correct information in
        their profile. Client profiles typically contain basic personal information
        relevant to task creation and account management.
        
        Args:
            user_id (str): The unique identifier of the client user whose profile
                          to update. Must be a valid UUID string that exists in
                          the system and corresponds to a client account type.
                          The system will verify this user has the right to update
                          their own profile.
            first_name (Optional[str]): Updated first name for the client. If
                                       provided, this will replace the existing
                                       first name. Should be a valid name string
                                       (typically 1-50 characters). Can be null
                                       to keep the existing first name unchanged.
            last_name (Optional[str]): Updated last name for the client. If
                                      provided, this will replace the existing
                                      last name. Should be a valid name string
                                      (typically 1-50 characters). Can be null
                                      to keep the existing last name unchanged.
            pfp_url (Optional[str]): Updated profile picture URL for the client.
                                     If provided, this will replace the existing
                                     profile picture URL. Should be a valid URL
                                     pointing to an image file. Can be null to
                                     remove the profile picture or keep the
                                     existing one unchanged.
        
        Returns:
            ProfileUpdateResponse: A response object confirming the profile update
                                  was successful. Fields include:
                                  - success (bool): Whether the update was successful
                                  - message (str): Description of the operation
                                  - profile_data (Optional[dict]): Updated profile data
        
        Raises:
            HTTPException: Returns a 404 status code if the user_id doesn't exist,
                          a 403 status code if the user lacks permission to update
                          the profile, or a 500 status code for other system errors
                          like database connection issues or validation problems.
        
        Example:
            >>> result = await update_client_profile(
            ...     user_id="client-uuid-here",
            ...     first_name="John",
            ...     last_name="Doe",
            ...     pfp_url="https://example.com/new-profile-pic.jpg"
            ... )
            >>> print("Client profile updated successfully")
        """
        try:
            profile_data = ProfileUpdateData(
                first_name=first_name,
                last_name=last_name,
                pfp_url=pfp_url
            )
            result = await profile_service.update_client_profile(user_id, profile_data)
            if not result:
                return HTTPException(status_code=500, detail="Failed to update client profile")
            return result
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
    
@tool
async def update_helper_profile(user_id: str,
        first_name: Optional[str],
        last_name: Optional[str],
        college: Optional[str],
        bio: Optional[str],
        graduation_year: Optional[int],
        zip_code: Optional[str],
        pfp_url: Optional[str]) -> ProfileUpdateResponse:
        """Update the profile information for a helper user.
        
        This function allows AI agents to modify helper profile details on behalf
        of users or authorized administrators. Only the fields that need to be
        updated should be provided - omitted fields will retain their current
        values. This is useful for helpers who want to update their professional
        information, educational background, skills, location, or personal details.
        Helper profiles contain comprehensive information that is crucial for
        task matching and client decision-making, so keeping this information
        current is important for both helpers and clients.
        
        Args:
            user_id (str): The unique identifier of the helper user whose profile
                          to update. Must be a valid UUID string that exists in
                          the system and corresponds to a helper account type.
                          The system will verify this user has the right to update
                          their own profile.
            first_name (Optional[str]): Updated first name for the helper. If
                                       provided, this will replace the existing
                                       first name. Should be a valid name string
                                       (typically 1-50 characters). Can be null
                                       to keep the existing first name unchanged.
            last_name (Optional[str]): Updated last name for the helper. If
                                      provided, this will replace the existing
                                      last name. Should be a valid name string
                                      (typically 1-50 characters). Can be null
                                      to keep the existing last name unchanged.
            college (Optional[str]): Updated college or university name for the
                                     helper. If provided, this will replace the
                                     existing college information. Should be a
                                     valid institution name. Can be null to
                                     remove college information or keep the
                                     existing value unchanged.
            bio (Optional[str]): Updated biographical information for the helper.
                                 If provided, this will replace the existing bio.
                                 Should be a compelling description of the helper's
                                 skills, experience, and what they can offer.
                                 Can be null to remove the bio or keep the
                                 existing one unchanged.
            graduation_year (Optional[int]): Updated graduation year for the helper.
                                            If provided, this will replace the
                                            existing graduation year. Should be a
                                            valid year (typically 4 digits, e.g.,
                                            2024). Can be null to remove graduation
                                            year information or keep the existing
                                            value unchanged.
            zip_code (Optional[str]): Updated ZIP code for the helper's location.
                                     If provided, this will replace the existing
                                     ZIP code. Must be a valid US ZIP code format
                                     (5 digits). Can be null to remove location
                                     information or keep the existing ZIP code
                                     unchanged.
            pfp_url (Optional[str]): Updated profile picture URL for the helper.
                                     If provided, this will replace the existing
                                     profile picture URL. Should be a valid URL
                                     pointing to an image file. Can be null to
                                     remove the profile picture or keep the
                                     existing one unchanged.
        
        Returns:
            ProfileUpdateResponse: A response object confirming the profile update
                                  was successful. Fields include:
                                  - success (bool): Whether the update was successful
                                  - message (str): Description of the operation
                                  - profile_data (Optional[dict]): Updated profile data
        
        Raises:
            HTTPException: Returns a 404 status code if the user_id doesn't exist,
                          a 403 status code if the user lacks permission to update
                          the profile, or a 500 status code for other system errors
                          like database connection issues or validation problems.
                          Common validation errors include: invalid ZIP code format,
                          graduation year out of reasonable range, or bio text
                          exceeding maximum length limits.
        
        Example:
            >>> result = await update_helper_profile(
            ...     user_id="helper-uuid-here",
            ...     first_name="Jane",
            ...     last_name="Smith",
            ...     college="University of Technology",
            ...     bio="Experienced mover with 3 years helping families relocate. Specialize in careful handling of antiques and fragile items.",
            ...     graduation_year=2023,
            ...     zip_code="12345",
            ...     pfp_url="https://example.com/new-helper-pic.jpg"
            ... )
            >>> print("Helper profile updated successfully")
        """
        try:
            profile_data = ProfileUpdateData(
                first_name=first_name,
                last_name=last_name,
                college=college,
                bio=bio,
                graduation_year=graduation_year,
                zip_code=zip_code,
                pfp_url=pfp_url
            )
            result = await profile_service.update_helper_profile(user_id, profile_data)
            if not result:
                return HTTPException(status_code=500, detail="Failed to update helper profile")
            return result
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
    