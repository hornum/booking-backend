from datetime import UTC, datetime, timedelta

from booking.domain.users.models import UserRole


### USERS ###
async def test_admin_can_deactivate_user(as_user, client, auth_json_data):
    user = as_user(1)
    auth_response = await user.post("/v1/auth/register", json=auth_json_data)
    assert auth_response.status_code == 201

    admin = as_user(user_id=2, role=UserRole.ADMIN)
    deactivate_user = await admin.post(
        "/v1/admin/users/1/status",
        params={"new_active_status": False},
    )
    assert deactivate_user.status_code == 200
    assert deactivate_user.json()["id"] == 1
    assert deactivate_user.json()["is_active"] is False

    user = as_user(1)
    login_response = await user.post(
        "/v1/auth/login",
        data={
            "username": auth_json_data["username"],
            "password": auth_json_data["password"],
        },
    )
    assert login_response.status_code == 401


async def test_admin_can_activate_user(as_user, client, auth_json_data):
    user = as_user(1)
    auth_response = await user.post("/v1/auth/register", json=auth_json_data)
    assert auth_response.status_code == 201

    admin = as_user(user_id=2, role=UserRole.ADMIN)
    deactivate_user = await admin.post(
        "/v1/admin/users/1/status",
        params={"new_active_status": False},
    )
    assert deactivate_user.status_code == 200

    user = as_user(1)
    login_response = await user.post(
        "/v1/auth/login",
        data={
            "username": auth_json_data["username"],
            "password": auth_json_data["password"],
        },
    )
    assert login_response.status_code == 401

    admin = as_user(user_id=2, role=UserRole.ADMIN)
    deactivate_user = await admin.post(
        "/v1/admin/users/1/status",
        params={"new_active_status": True},
    )
    assert deactivate_user.status_code == 200
    assert deactivate_user.json()["id"] == 1
    assert deactivate_user.json()["is_active"] is True

    user = as_user(1)
    login_response = await user.post(
        "/v1/auth/login",
        data={
            "username": auth_json_data["username"],
            "password": auth_json_data["password"],
        },
    )
    assert login_response.status_code == 200


async def test_regular_user_cannot_change_status_and_no_side_effects(
    as_user,
    client,
    auth_json_data,
):
    target_user = as_user(user_id=1)

    register_response = await target_user.post(
        "/v1/auth/register",
        json=auth_json_data,
    )
    assert register_response.status_code == 201

    regular_user = as_user(user_id=2)

    response = await regular_user.post(
        "/v1/admin/users/1/status",
        params={"new_active_status": False},
    )
    assert response.status_code == 403

    login_response = await client.post(
        "/v1/auth/login",
        data={
            "username": auth_json_data["username"],
            "password": auth_json_data["password"],
        },
    )

    assert login_response.status_code == 200


async def test_deactivate_missing_user_returns_404(as_user):
    admin = as_user(user_id=2, role=UserRole.ADMIN)
    deactivate_user = await admin.post(
        "/v1/admin/users/1/status",
        params={"new_active_status": False},
    )
    assert deactivate_user.status_code == 404


### BOOKINGS ###


async def test_admin_create_booking_unauthenticated(client):
    response = await client.post(
        "/v1/admin/bookings/create_confirmed_booking",
        data={"target_user_id": 1},
    )
    assert response.status_code == 401


async def test_admin_create_booking_not_authorized(as_user, client):
    user = as_user(user_id=1)
    response = await user.post(
        "/v1/admin/bookings/create_confirmed_booking",
        data={"target_user_id": 1},
    )
    assert response.status_code == 403


async def test_admin_create_confirmed_booking_success(
    as_user, client, registered_user_id
):
    admin = as_user(user_id=2, role=UserRole.ADMIN)
    now = datetime.now(UTC)
    response = await admin.post(
        "/v1/admin/bookings/create_confirmed_booking",
        json={
            "target_user_id": registered_user_id,
            "create_confirmed": True,
            "room_id": 1,
            "start": str(now + timedelta(hours=1)),
            "end": str(now + timedelta(hours=2)),
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"


async def test_admin_confirm_booking_not_found(as_user, client):
    user = as_user(user_id=1, role=UserRole.ADMIN)
    response = await user.post("/v1/admin/bookings/999/confirm")
    assert response.status_code == 404


async def test_admin_can_confirm_another_user_booking(as_user, client, booking_in_db):
    admin = as_user(user_id=2, role=UserRole.ADMIN)
    response = await admin.post(
        f"/v1/admin/bookings/{booking_in_db.id}/confirm",
    )
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"


async def test_admin_expired_booking_confirm_fail(
    as_user, client, expired_booking_in_db
):
    admin = as_user(user_id=2, role=UserRole.ADMIN)
    response = await admin.post(
        f"/v1/admin/bookings/{expired_booking_in_db.id}/confirm",
    )
    assert response.status_code == 409
