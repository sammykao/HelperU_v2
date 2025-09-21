"""Chat tools for AI agents

This module provides comprehensive tools for AI agents to interact with the chat
and messaging system. It includes functions for creating chats, sending messages,
retrieving chat history, managing chat participants, and handling message read
status. All functions are designed to work with LangChain's tool system and
return serializable JSON responses.
"""

from typing import List
from uuid import UUID
from app.deps.supabase import get_chat_service
from app.schemas.chat import (
    ChatResponse,
    ChatListResponse,
    MessageCreateRequest,
    MessageResponse,
    MessageListResponse,
    ChatMarkReadRequest,
    ChatWithParticipantsResponse
)
from langchain.tools import tool
from fastapi import HTTPException

# Global service instance
chat_service = get_chat_service()

@tool
async def create_chat(user_id: str, participant_id: str) -> ChatResponse:
        """Create a new chat conversation between two users.
        
        This function allows AI agents to create new chat conversations between
        two users in the system. If a chat already exists between the specified
        users, it will return the existing chat instead of creating a duplicate.
        This is useful for enabling communication between clients and helpers,
        or between any two users who need to discuss tasks or coordinate work.
        
        Args:
            user_id (str): The unique identifier of the user initiating the chat.
                          Must be a valid UUID string that exists in the system.
                          This user will be one of the two participants in the chat.
            participant_id (str): The unique identifier of the other user to
                                 include in the chat. Must be a valid UUID string
                                 that exists in the system. This user will be
                                 the second participant in the chat.
        
        Returns:
            ChatResponse: A complete chat object containing all the created chat
                         details. Fields include:
                         - id (UUID): Unique chat identifier
                         - users (List[ChatParticipantInfo]): Array of participant information
                         - created_at (datetime): Chat creation timestamp
                         - updated_at (datetime): Last update timestamp
                         
                         Each ChatParticipantInfo includes:
                         - id (UUID): Participant's unique identifier
                         - first_name (str): Participant's first name
                         - last_name (str): Participant's last name
                         - pfp_url (Optional[str]): Profile picture URL
                         - phone (Optional[str]): Phone number
        
        Raises:
            HTTPException: Returns a 500 status code with error details if the
                          chat creation fails due to validation errors, database
                          issues, user not found, or other system problems.
                          Common errors include: one or both users don't exist,
                          database connection issues, or permission problems.
        
        Example:
            >>> result = await create_chat(
            ...     user_id="client-uuid-here",
            ...     participant_id="helper-uuid-here"
            ... )
            >>> print(f"Chat created with ID: {result.id}")
        """
        try:
            result = await chat_service.create_chat(UUID(user_id), UUID(participant_id))
            if not result:
                return HTTPException(status_code=500, detail="Failed to create chat")
            return result
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
    
@tool
async def get_user_chats(user_id: str) -> ChatListResponse:
        """Retrieve all chat conversations for a specific user.
        
        This function allows AI agents to fetch all chat conversations that a
        particular user is participating in. This is useful for displaying a
        user's chat history, showing active conversations, or providing an
        overview of all ongoing communications. The chats are ordered by most
        recent activity to show the most relevant conversations first.
        
        Args:
            user_id (str): The unique identifier of the user whose chats to
                          retrieve. Must be a valid UUID string that exists in
                          the system. This will return all chats where this
                          user is a participant, regardless of whether they
                          initiated the chat or were added as a participant.
        
        Returns:
            ChatListResponse: A structured response containing a list of all
                             chats for the specified user. Fields include:
                             - chats (List[ChatResponse]): List of chat conversations
                             - total (int): Total number of chats for the user
                             
                             Each ChatResponse includes:
                             - id (UUID): Unique chat identifier
                             - users (List[ChatParticipantInfo]): Array of participant information
                             - created_at (datetime): Chat creation timestamp
                             - updated_at (datetime): Last update timestamp
                             
                             Each ChatParticipantInfo includes:
                             - id (UUID): Participant's unique identifier
                             - first_name (str): Participant's first name
                             - last_name (str): Participant's last name
                             - pfp_url (Optional[str]): Profile picture URL
                             - phone (Optional[str]): Phone number
        
        Raises:
            HTTPException: Returns a 500 status code with error details if the
                          chat retrieval fails due to database issues, user not
                          found, or other system problems.
        
        Example:
            >>> chats = await get_user_chats("user-uuid-here")
            >>> print(f"User has {len(chats.chats)} active chats")
            >>> for chat in chats.chats:
            ...     print(f"Chat {chat.id} with {len(chat.users)} participants")
        """
        try:
            result = await chat_service.get_user_chats(UUID(user_id))
            if not result:
                return HTTPException(status_code=500, detail="Failed to get user chats")
            return result
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
    
@tool
async def get_chat_with_participants(chat_id: str, user_id: str) -> ChatWithParticipantsResponse:
        """Retrieve detailed chat information including participant details.
        
        This function allows AI agents to fetch comprehensive information about
        a specific chat, including detailed participant information, last message
        details, and unread message counts. This is useful for displaying chat
        details, showing participant information, or providing context about
        ongoing conversations. The function verifies that the requesting user
        has access to the specified chat.
        
        Args:
            chat_id (str): The unique identifier of the chat to retrieve.
                          Must be a valid UUID string that exists in the system.
                          This will return detailed information about this
                          specific chat conversation.
            user_id (str): The unique identifier of the user requesting the
                          chat information. Must be a valid UUID string that
                          exists in the system and is a participant in the
                          specified chat. This is used for access control and
                          to calculate unread message counts.
        
        Returns:
            ChatWithParticipantsResponse: A comprehensive chat response containing
                                         detailed information. Fields include:
                                         - id (UUID): Unique chat identifier
                                         - users (List[UUID]): Array of participant UUIDs
                                         - participants (List[ChatParticipantInfo]): Detailed participant information
                                         - created_at (datetime): Chat creation timestamp
                                         - updated_at (datetime): Last update timestamp
                                         - last_message (Optional[str]): Content of the last message
                                         - last_message_at (Optional[datetime]): Timestamp of the last message
                                         - unread_count (int): Number of unread messages
                                         
                                         Each ChatParticipantInfo includes:
                                         - id (UUID): Participant's unique identifier
                                         - first_name (str): Participant's first name
                                         - last_name (str): Participant's last name
                                         - pfp_url (Optional[str]): Profile picture URL
                                         - phone (Optional[str]): Phone number
        
        Raises:
            HTTPException: Returns a 404 status code if the chat_id doesn't exist,
                          a 403 status code if the user lacks access to the chat,
                          or a 500 status code for other system errors like
                          database connection issues or validation problems.
        
        Example:
            >>> chat_details = await get_chat_with_participants(
            ...     chat_id="chat-uuid-here",
            ...     user_id="user-uuid-here"
            ... )
            >>> print(f"Chat with {len(chat_details.participants)} participants")
            >>> print(f"Unread messages: {chat_details.unread_count}")
        """
        try:
            result = await chat_service.get_chat_with_participants(UUID(chat_id), UUID(user_id))
            if not result:
                return HTTPException(status_code=500, detail="Failed to get chat with participants")
            return result
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
    
@tool
async def send_message(chat_id: str, sender_id: str, content: str) -> MessageResponse:
        """Send a new message in an existing chat conversation.
        
        This function allows AI agents to send messages on behalf of users in
        existing chat conversations. The message will be delivered to all
        participants in the chat and may trigger SMS notifications if the
        OpenPhone service is configured. This is useful for enabling real-time
        communication between users, coordinating tasks, or providing updates
        in ongoing conversations.
        
        Args:
            chat_id (str): The unique identifier of the chat where the message
                          should be sent. Must be a valid UUID string that exists
                          in the system. The sender must be a participant in
                          this chat to send messages.
            sender_id (str): The unique identifier of the user sending the
                            message. Must be a valid UUID string that exists in
                            the system and is a participant in the specified chat.
                            This user will be recorded as the sender of the message.
            content (str): The text content of the message to send. Should be
                          a meaningful message that provides value to the
                          conversation. The content will be stored in the
                          database and delivered to all chat participants.
        
        Returns:
            MessageResponse: A complete message object containing all the sent
                            message details. Fields include:
                            - id (UUID): Unique message identifier
                            - chat_id (UUID): ID of the chat this message belongs to
                            - sender_id (UUID): ID of the user who sent the message
                            - content (str): Message content/text
                            - read_at (Optional[datetime]): Timestamp when message was read (null for new messages)
                            - created_at (datetime): Message creation timestamp
                            - updated_at (datetime): Last update timestamp
        
        Raises:
            HTTPException: Returns a 404 status code if the chat_id doesn't exist,
                          a 403 status code if the sender is not a participant in
                          the chat, or a 500 status code for other system errors
                          like database connection issues or validation problems.
                          Common errors include: chat not found, sender not in chat,
                          or message creation failure.
        
        Example:
            >>> message = await send_message(
            ...     chat_id="chat-uuid-here",
            ...     sender_id="user-uuid-here",
            ...     content="Hi! I'm available to help with your task this weekend."
            ... )
            >>> print(f"Message sent with ID: {message.id}")
        """
        try:
            request = MessageCreateRequest(content=content)
            result = await chat_service.send_message(UUID(chat_id), UUID(sender_id), request)
            if not result:
                return HTTPException(status_code=500, detail="Failed to send message")
            return result
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
    
@tool
async def get_chat_messages(chat_id: str, user_id: str, limit: int = 50, offset: int = 0) -> MessageListResponse:
        """Retrieve messages from a specific chat conversation with pagination.
        
        This function allows AI agents to fetch message history from a specific
        chat conversation. The messages are returned in chronological order
        (oldest first) and support pagination for efficient data retrieval.
        This is useful for displaying chat history, loading message archives,
        or analyzing conversation content. The function verifies that the
        requesting user has access to the specified chat.
        
        Args:
            chat_id (str): The unique identifier of the chat to retrieve
                          messages from. Must be a valid UUID string that exists
                          in the system. The user must be a participant in
                          this chat to access its messages.
            user_id (str): The unique identifier of the user requesting the
                          messages. Must be a valid UUID string that exists in
                          the system and is a participant in the specified chat.
                          This is used for access control to ensure privacy.
            limit (int): Maximum number of messages to return in a single
                        request. Default is 50, maximum recommended is 100
                        for performance. Useful for pagination and controlling
                        result set size.
            offset (int): Number of messages to skip for pagination. Default
                         is 0. Use this with limit to implement pagination:
                         offset=50 would skip the first 50 messages, offset=100
                         would skip the first 100, etc.
        
        Returns:
            MessageListResponse: A structured response containing a list of
                                messages from the specified chat. Fields include:
                                - messages (List[MessageResponse]): List of messages in the chat
                                - total (int): Total number of messages in the chat
                                - has_more (bool): Whether there are more messages beyond the current page
                                
                                Each MessageResponse includes:
                                - id (UUID): Unique message identifier
                                - chat_id (UUID): ID of the chat this message belongs to
                                - sender_id (UUID): ID of the user who sent the message
                                - content (str): Message content/text
                                - read_at (Optional[datetime]): Timestamp when message was read
                                - created_at (datetime): Message creation timestamp
                                - updated_at (datetime): Last update timestamp
        
        Raises:
            HTTPException: Returns a 404 status code if the chat_id doesn't
                          exist, a 403 status code if the user lacks access
                          to the chat, or a 500 status code for other system
                          errors like database connection issues or validation
                          problems.
        
        Example:
            >>> messages = await get_chat_messages(
            ...     chat_id="chat-uuid-here",
            ...     user_id="user-uuid-here",
            ...     limit=20,
            ...     offset=0
            ... )
            >>> print(f"Retrieved {len(messages.messages)} messages")
            >>> print(f"Total messages in chat: {messages.total}")
            >>> if messages.has_more:
            ...     print("More messages available")
        """
        try:
            result = await chat_service.get_chat_messages(UUID(chat_id), UUID(user_id), limit, offset)
            if not result:
                return HTTPException(status_code=500, detail="Failed to get chat messages")
            return result
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
    
@tool
async def mark_messages_read(chat_id: str, user_id: str, message_ids: List[str]) -> dict:
        """Mark specific messages as read in a chat conversation.
        
        This function allows AI agents to mark messages as read on behalf of
        users, updating the read_at timestamp for specified messages. This is
        useful for tracking which messages have been seen by users, updating
        unread message counts, and providing read receipts in chat interfaces.
        Only messages sent by other participants (not the current user) can
        be marked as read.
        
        Args:
            chat_id (str): The unique identifier of the chat containing the
                          messages to mark as read. Must be a valid UUID string
                          that exists in the system. The user must be a
                          participant in this chat to mark messages as read.
            user_id (str): The unique identifier of the user marking the
                          messages as read. Must be a valid UUID string that
                          exists in the system and is a participant in the
                          specified chat. This user's read status will be
                          updated for the specified messages.
            message_ids (List[str]): A list of message UUIDs to mark as read.
                                    Each message ID must be a valid UUID string
                                    that exists in the system and belongs to
                                    the specified chat. Only messages sent by
                                    other participants can be marked as read.
        
        Returns:
            dict: A response object confirming the read status update was
                  successful. Fields include:
                  - success (bool): Whether the operation was successful
                  - message (str): Description of the operation
                  - read_at (str): ISO timestamp when messages were marked as read
        
        Raises:
            HTTPException: Returns a 404 status code if the chat_id doesn't
                          exist, a 403 status code if the user lacks access
                          to the chat, or a 500 status code for other system
                          errors like database connection issues or validation
                          problems. Common errors include: chat not found,
                          user not in chat, or message update failure.
        
        Example:
            >>> result = await mark_messages_read(
            ...     chat_id="chat-uuid-here",
            ...     user_id="user-uuid-here",
            ...     message_ids=["msg-uuid-1", "msg-uuid-2", "msg-uuid-3"]
            ... )
            >>> if result["success"]:
            ...     print(f"Marked {result['message']}")
        """
        try:
            request = ChatMarkReadRequest(message_ids=[UUID(msg_id) for msg_id in message_ids])
            result = await chat_service.mark_messages_read(UUID(chat_id), UUID(user_id), request)
            if not result:
                return HTTPException(status_code=500, detail="Failed to mark messages as read")
            return result
        except Exception as e:
            return HTTPException(status_code=500, detail=str(e))
        
    