from booking.api.routes.admin.booking import router as admin_booking_router
from booking.api.routes.admin.user import router as admin_users_router
from booking.api.routes.auth import router as auth_router
from booking.api.routes.booking import router as booking_router
from booking.api.routes.payment import router as payment_router
from booking.api.routes.user import router as user_router

routers = [
    booking_router,
    auth_router,
    user_router,
    payment_router,
    admin_booking_router,
    admin_users_router,
]
