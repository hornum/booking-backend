from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator

from booking.domain.bookings.models import BookingStatus


class BookRoomRequest(BaseModel):
    start: datetime
    end: datetime

    @model_validator(mode="after")
    def check_start_before_end(self) -> "BookRoomRequest":
        if self.start >= self.end:
            raise ValueError("Invalid start/end dates")
        return self


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    user_id: int
    start: datetime
    end: datetime
    status: BookingStatus
