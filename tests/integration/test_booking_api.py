async def test_create_booking_returns_201(auth_client):
    response = await auth_client.post(
        "/v1/bookings/1/book",
        json={
            "room_id": 1,
            "start": "2026-06-01T10:00:00",
            "end": "2026-06-01T11:00:00",
        },
    )
    assert response.status_code == 201
    assert response.json()["status"] == "hold"


async def test_confirm_booking_returns_confirmed(auth_client, booking_data):
    create = await auth_client.post(
        "/v1/bookings/1/book",
        json=booking_data,
    )
    booking_id = create.json()["id"]

    response = await auth_client.post(f"/v1/bookings/{booking_id}/confirm")
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"


async def test_double_confirm_returns_409(auth_client, booking_data):
    create = await auth_client.post(
        "/v1/bookings/1/book",
        json=booking_data,
    )
    booking_id = create.json()["id"]

    await auth_client.post(f"/v1/bookings/{booking_id}/confirm")
    response = await auth_client.post(f"/v1/bookings/{booking_id}/confirm")
    assert response.status_code == 409


async def test_confirm_missing_returns_404(auth_client):
    response = await auth_client.post("/v1/bookings/99999/confirm")
    assert response.status_code == 404


async def test_cancel_booking_returns_cancelled(auth_client, booking_data):
    create = await auth_client.post(
        "/v1/bookings/1/book",
        json=booking_data,
    )
    booking_id = create.json()["id"]

    response = await auth_client.post(f"/v1/bookings/{booking_id}/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


async def test_cancel_already_cancelled_fail(auth_client, booking_data):
    create = await auth_client.post(
        "/v1/bookings/1/book",
        json=booking_data,
    )
    booking_id = create.json()["id"]

    await auth_client.post(f"/v1/bookings/{booking_id}/cancel")
    response = await auth_client.post(f"/v1/bookings/{booking_id}/cancel")
    assert response.status_code == 409


async def test_confirm_cancelled_fail(auth_client, booking_data):
    create = await auth_client.post(
        "/v1/bookings/1/book",
        json=booking_data,
    )
    booking_id = create.json()["id"]

    await auth_client.post(f"/v1/bookings/{booking_id}/cancel")
    response = await auth_client.post(f"/v1/bookings/{booking_id}/confirm")
    assert response.status_code == 409


async def test_confirm_without_auth_returns_401(client):
    response = await client.post("/v1/bookings/1/confirm")
    assert response.status_code == 401
