from booking.api.routes.auth import router as auth_router
from booking.api.routes.booking import router as booking_router
from booking.api.routes.user import router as user_router

routers = [
    booking_router,
    auth_router,
    user_router,
]
