"""
Push notification service using Web Push protocol
"""
from pywebpush import webpush, WebPushException
from sqlalchemy.orm import Session
from typing import Optional
import json

from app.core.config import settings
from app.models.models import User, PushNotification


class PushNotificationService:
    """Service for sending web push notifications"""

    def __init__(self):
        self.vapid_private_key = settings.WEB_PUSH_PRIVATE_KEY
        self.vapid_public_key = settings.WEB_PUSH_PUBLIC_KEY
        self.vapid_claims = {
            "sub": f"mailto:{settings.WEB_PUSH_EMAIL or 'noreply@sahasplit.app'}"
        }

    async def send_notification(
        self,
        db: Session,
        user_id: int,
        title: str,
        body: str,
        data: Optional[dict] = None
    ) -> bool:
        """
        Send a push notification to a user

        Args:
            db: Database session
            user_id: Target user ID
            title: Notification title
            body: Notification body text
            data: Additional data payload

        Returns:
            True if sent successfully
        """
        # Get user's push subscription
        subscription = db.query(PushNotification).filter(
            PushNotification.user_id == user_id
        ).first()

        if not subscription or not subscription.subscription:
            return False

        try:
            # Parse subscription JSON
            subscription_info = json.loads(subscription.subscription)

            # Prepare notification payload
            payload = {
                "title": title,
                "body": body,
                "icon": "/icon-192x192.png",
                "badge": "/icon-192x192.png"
            }

            if data:
                payload["data"] = data

            # Send web push
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=self.vapid_private_key,
                vapid_claims=self.vapid_claims
            )

            return True

        except WebPushException as e:
            print(f"Error sending push notification: {e}")

            # If subscription is invalid, delete it
            if e.response and e.response.status_code in [404, 410]:
                db.delete(subscription)
                db.commit()

            return False
        except Exception as e:
            print(f"Unexpected error sending push: {e}")
            return False

    async def register_subscription(
        self,
        db: Session,
        user_id: int,
        subscription: str
    ) -> bool:
        """
        Register or update a user's push subscription

        Args:
            db: Database session
            user_id: User ID
            subscription: Push subscription JSON

        Returns:
            True if registered successfully
        """
        existing = db.query(PushNotification).filter(
            PushNotification.user_id == user_id
        ).first()

        if existing:
            existing.subscription = subscription
        else:
            push_notif = PushNotification(
                user_id=user_id,
                subscription=subscription
            )
            db.add(push_notif)

        db.commit()
        return True

    def get_public_key(self) -> str:
        """Get VAPID public key for client-side subscription"""
        return self.vapid_public_key or ""


# Global service instance
push_service = PushNotificationService()

