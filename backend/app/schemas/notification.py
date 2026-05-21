import re
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, field_validator


# Channel-specific configurations
class NtfyConfig(BaseModel):
    server: str = "https://ntfy.sh"
    topic: str
    token: str | None = None

    @field_validator("server")
    @classmethod
    def validate_server(cls, v: str) -> str:
        if not v.startswith("http://") and not v.startswith("https://"):
            raise ValueError("Server-URL muss mit http:// oder https:// beginnen")
        if len(v) > 500:
            raise ValueError("Server-URL darf maximal 500 Zeichen lang sein")
        return v.rstrip("/")

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v: str) -> str:
        if not v or len(v) < 3:
            raise ValueError("Topic muss mindestens 3 Zeichen lang sein")
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Topic darf nur Buchstaben, Zahlen, - und _ enthalten")
        return v


class MattermostConfig(BaseModel):
    webhook_url: str

    @field_validator("webhook_url")
    @classmethod
    def validate_webhook(cls, v: str) -> str:
        if not v.startswith("https://"):
            raise ValueError("Webhook-URL muss HTTPS verwenden")
        if "/hooks/" not in v:
            raise ValueError("Ungültiges Mattermost-Webhook-URL-Format")
        return v


class EmailConfig(BaseModel):
    address: str

    @field_validator("address")
    @classmethod
    def validate_email(cls, v: str) -> str:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Ungültige E-Mail-Adresse")
        return v


class ExpoPushConfig(BaseModel):
    push_token: str

    @field_validator("push_token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        if not v.startswith("ExponentPushToken[") and not v.startswith("ExpoPushToken["):
            raise ValueError("Ungültiges Expo-Push-Token-Format")
        return v


# Notification settings schemas
class NotificationSettingsBase(BaseModel):
    channel: Literal["ntfy", "mattermost", "email", "expo_push"]
    enabled: bool = True
    priority: int = 1
    config: dict


class NotificationSettingsCreate(NotificationSettingsBase):
    pass


class NotificationSettingsUpdate(BaseModel):
    enabled: bool | None = None
    priority: int | None = None
    config: dict | None = None


class NotificationSettingsResponse(NotificationSettingsBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


VALID_OCCASIONS = {"casual", "office", "formal", "date", "sporty", "outdoor", "work", "party"}


# Schedule schemas
class ScheduleBase(BaseModel):
    day_of_week: int  # 0=Monday, 6=Sunday (day to WEAR the outfit)
    notification_time: str  # HH:MM format
    occasion: str = "casual"
    enabled: bool = True
    notify_day_before: bool = False  # If True, notification comes evening before

    @field_validator("occasion")
    @classmethod
    def validate_occasion(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in VALID_OCCASIONS:
            raise ValueError(
                f"Ungültiger Anlass. Erlaubt: {', '.join(sorted(VALID_OCCASIONS))}"
            )
        return v

    @field_validator("day_of_week")
    @classmethod
    def validate_day(cls, v: int) -> int:
        if v < 0 or v > 6:
            raise ValueError("day_of_week muss 0–6 sein (Montag–Sonntag)")
        return v

    @field_validator("notification_time")
    @classmethod
    def validate_time(cls, v: str) -> str:
        if not re.match(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", v):
            raise ValueError("notification_time muss im Format HH:MM sein")
        return v


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleUpdate(BaseModel):
    day_of_week: int | None = None
    notification_time: str | None = None
    occasion: str | None = None
    enabled: bool | None = None
    notify_day_before: bool | None = None

    @field_validator("occasion")
    @classmethod
    def validate_occasion(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip().lower()
            if v not in VALID_OCCASIONS:
                raise ValueError(
                    f"Ungültiger Anlass. Erlaubt: {', '.join(sorted(VALID_OCCASIONS))}"
                )
        return v

    @field_validator("notification_time")
    @classmethod
    def validate_time(cls, v: str | None) -> str | None:
        if v is not None and not re.match(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", v):
            raise ValueError("notification_time muss im Format HH:MM sein")
        return v

    @field_validator("day_of_week")
    @classmethod
    def validate_day(cls, v: int | None) -> int | None:
        if v is not None and (v < 0 or v > 6):
            raise ValueError("day_of_week muss 0–6 sein (Montag–Sonntag)")
        return v


class ScheduleResponse(BaseModel):
    id: UUID
    user_id: UUID
    day_of_week: int
    notification_time: str  # Converted from Time object
    occasion: str
    enabled: bool
    notify_day_before: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @field_validator("notification_time", mode="before")
    @classmethod
    def convert_time(cls, v):
        if hasattr(v, "strftime"):
            return v.strftime("%H:%M")
        return v


# Notification delivery tracking
class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    outfit_id: UUID | None
    channel: str
    status: str
    attempts: int
    sent_at: datetime | None
    delivered_at: datetime | None
    error_message: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class TestNotificationRequest(BaseModel):
    pass


class TestNotificationResponse(BaseModel):
    success: bool
    message: str


class MessageResponse(BaseModel):
    message: str
