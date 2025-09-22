from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

from app.utils.emailer import send_contact_form_email
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


class ContactFormData(BaseModel):
    name: str
    email: EmailStr
    subject: str
    category: str
    message: str


class ContactResponse(BaseModel):
    success: bool
    message: str


@router.post("/contact", response_model=ContactResponse)
async def submit_contact_form(contact_data: ContactFormData):
    """
    Submit contact form and send emails
    """
    try:
        # Send contact form email
        success = send_contact_form_email(
            name=contact_data.name,
            email=contact_data.email,
            subject=contact_data.subject,
            category=contact_data.category,
            message=contact_data.message
        )
        
        if success:
            logger.info(f"Contact form submitted successfully by {contact_data.email}")
            return ContactResponse(
                success=True,
                message="Thank you for your message! We'll get back to you within 4 hours."
            )
        else:
            logger.error(f"Failed to send contact form email for {contact_data.email}")
            return ContactResponse(
                success=False,
                message="Sorry, there was an error sending your message. Please try again later."
            )
            
    except Exception as e:
        logger.error(f"Error processing contact form: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later."
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "contact"}
