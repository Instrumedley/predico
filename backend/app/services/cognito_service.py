"""
AWS Cognito service for user management.

This service handles user authentication through AWS Cognito User Pools.
We maintain user data in our database for application-specific information,
while Cognito handles authentication, password policies, and MFA.

Note: boto3 is synchronous, so we wrap calls in asyncio.to_thread for async compatibility.
"""
import asyncio
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any
from app.core.config import settings
import structlog

logger = structlog.get_logger(__name__)


class CognitoService:
    """Service for interacting with AWS Cognito User Pools."""
    
    def __init__(self):
        """Initialize Cognito client."""
        # Only initialize if Cognito is enabled
        if settings.COGNITO_ENABLED and settings.COGNITO_USER_POOL_ID:
            self.client = boto3.client(
                'cognito-idp',
                region_name=settings.AWS_REGION
            )
            self.user_pool_id = settings.COGNITO_USER_POOL_ID
            self.client_id = settings.COGNITO_CLIENT_ID
        else:
            self.client = None
            self.user_pool_id = None
            self.client_id = None
        
    async def sign_up(
        self,
        email: str,
        password: str,
        username: str,
        user_attributes: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Register a new user in Cognito.
        
        Args:
            email: User's email address
            password: User's password
            username: Username
            user_attributes: Additional user attributes
            
        Returns:
            Dict with user sub (Cognito user ID) and other response data
        """
        if not self.user_pool_id or not self.client_id:
            logger.warning("Cognito not configured, skipping user creation")
            return {"sub": None, "user_confirmed": False}
        
        if not self.client or not self.user_pool_id or not self.client_id:
            logger.warning("Cognito not configured, skipping user creation")
            return {"sub": None, "user_confirmed": False}
        
        try:
            attributes = [
                {"Name": "email", "Value": email},
                {"Name": "preferred_username", "Value": username},
            ]
            
            if user_attributes:
                for key, value in user_attributes.items():
                    attributes.append({"Name": key, "Value": value})
            
            # Run boto3 call in thread pool (boto3 is synchronous)
            response = await asyncio.to_thread(
                self.client.sign_up,
                ClientId=self.client_id,
                Username=email,  # Cognito uses email as username
                Password=password,
                UserAttributes=attributes,
            )
            
            logger.info("User created in Cognito", email=email, sub=response.get("UserSub"))
            return {
                "sub": response.get("UserSub"),
                "user_confirmed": response.get("UserConfirmed", False),
                "code_delivery_details": response.get("CodeDeliveryDetails"),
            }
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            error_message = e.response.get("Error", {}).get("Message", "")
            logger.error(
                "Cognito signup failed",
                error_code=error_code,
                error_message=error_message,
                email=email
            )
            
            # Raise appropriate HTTP exceptions
            if error_code == "UsernameExistsException":
                raise ValueError("Email already registered in Cognito")
            elif error_code == "InvalidPasswordException":
                raise ValueError(f"Password does not meet requirements: {error_message}")
            elif error_code == "InvalidParameterException":
                raise ValueError(f"Invalid parameter: {error_message}")
            else:
                raise ValueError(f"Cognito error: {error_message}")
    
    async def confirm_sign_up(self, email: str, confirmation_code: str) -> bool:
        """
        Confirm user signup with verification code.
        
        Args:
            email: User's email
            confirmation_code: Verification code from email
            
        Returns:
            True if successful
        """
        if not self.user_pool_id or not self.client_id:
            logger.warning("Cognito not configured, skipping confirmation")
            return False
        
        try:
            await asyncio.to_thread(
                self.client.confirm_sign_up,
                ClientId=self.client_id,
                Username=email,
                ConfirmationCode=confirmation_code,
            )
            logger.info("User confirmed in Cognito", email=email)
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            error_message = e.response.get("Error", {}).get("Message", "")
            logger.error(
                "Cognito confirmation failed",
                error_code=error_code,
                error_message=error_message,
                email=email
            )
            raise ValueError(f"Confirmation failed: {error_message}")
    
    async def authenticate(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and get tokens.
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            Dict with access_token, id_token, refresh_token
        """
        if not self.user_pool_id or not self.client_id:
            logger.warning("Cognito not configured, skipping authentication")
            return {}
        
        try:
            response = await asyncio.to_thread(
                self.client.initiate_auth,
                ClientId=self.client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": email,
                    "PASSWORD": password,
                },
            )
            
            authentication_result = response.get("AuthenticationResult", {})
            logger.info("User authenticated in Cognito", email=email)
            
            return {
                "access_token": authentication_result.get("AccessToken"),
                "id_token": authentication_result.get("IdToken"),
                "refresh_token": authentication_result.get("RefreshToken"),
                "expires_in": authentication_result.get("ExpiresIn"),
            }
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            error_message = e.response.get("Error", {}).get("Message", "")
            logger.error(
                "Cognito authentication failed",
                error_code=error_code,
                error_message=error_message,
                email=email
            )
            
            if error_code == "NotAuthorizedException":
                raise ValueError("Invalid email or password")
            elif error_code == "UserNotConfirmedException":
                raise ValueError("User email not verified")
            else:
                raise ValueError(f"Authentication failed: {error_message}")
    
    async def resend_confirmation_code(self, email: str) -> bool:
        """
        Resend confirmation code to user.
        
        Args:
            email: User's email
            
        Returns:
            True if successful
        """
        if not self.user_pool_id or not self.client_id:
            logger.warning("Cognito not configured, skipping resend")
            return False
        
        try:
            await asyncio.to_thread(
                self.client.resend_confirmation_code,
                ClientId=self.client_id,
                Username=email,
            )
            logger.info("Confirmation code resent", email=email)
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            error_message = e.response.get("Error", {}).get("Message", "")
            logger.error(
                "Cognito resend failed",
                error_code=error_code,
                error_message=error_message,
                email=email
            )
            raise ValueError(f"Failed to resend code: {error_message}")
    
    async def forgot_password(self, email: str) -> bool:
        """
        Initiate password reset flow.
        
        Args:
            email: User's email
            
        Returns:
            True if successful
        """
        if not self.user_pool_id or not self.client_id:
            logger.warning("Cognito not configured, skipping password reset")
            return False
        
        try:
            await asyncio.to_thread(
                self.client.forgot_password,
                ClientId=self.client_id,
                Username=email,
            )
            logger.info("Password reset initiated", email=email)
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            error_message = e.response.get("Error", {}).get("Message", "")
            logger.error(
                "Cognito forgot password failed",
                error_code=error_code,
                error_message=error_message,
                email=email
            )
            # Don't raise - return success for security (don't reveal if email exists)
            return False
    
    async def confirm_forgot_password(
        self,
        email: str,
        confirmation_code: str,
        new_password: str
    ) -> bool:
        """
        Confirm password reset with code.
        
        Args:
            email: User's email
            confirmation_code: Verification code from email
            new_password: New password
            
        Returns:
            True if successful
        """
        if not self.user_pool_id or not self.client_id:
            logger.warning("Cognito not configured, skipping password reset confirmation")
            return False
        
        try:
            await asyncio.to_thread(
                self.client.confirm_forgot_password,
                ClientId=self.client_id,
                Username=email,
                ConfirmationCode=confirmation_code,
                Password=new_password,
            )
            logger.info("Password reset confirmed", email=email)
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            error_message = e.response.get("Error", {}).get("Message", "")
            logger.error(
                "Cognito password reset confirmation failed",
                error_code=error_code,
                error_message=error_message,
                email=email
            )
            raise ValueError(f"Password reset failed: {error_message}")


# Singleton instance
cognito_service = CognitoService()

