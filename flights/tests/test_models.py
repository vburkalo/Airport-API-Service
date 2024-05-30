import os

import pytest
from django.utils.text import slugify

from flights.models import (
    Country,
    City,
    Airport,
    AirplaneType,
    Airplane,
    Route,
    Crew,
    Flight,
    Order,
    Ticket,
    airplane_image_file_path,
)
from users.models import User


@pytest.mark.django_db
def test_country_str():
    country = Country(name="Test Country")
    assert str(country) == "Test Country"


@pytest.mark.django_db
def test_city_str():
    country = Country.objects.create(name="Test Country")
    city = City.objects.create(name="Test City", country=country)
    assert str(city) == "Test City"


@pytest.mark.django_db
def test_airport_str():
    country = Country.objects.create(name="Test Country")
    city = City.objects.create(name="Test City", country=country)
    airport = Airport.objects.create(
        name="Test Airport", code="TST", closest_big_city=city
    )
    assert str(airport) == "Test Airport (TST)"


@pytest.mark.django_db
def test_airplane_str():
    airplane_type = AirplaneType.objects.create(name="Test Type")
    airplane = Airplane.objects.create(
        name="Test Airplane",
        rows=10,
        seats_in_row=4,
        airplane_type=airplane_type,
    )
    assert str(airplane) == "Test Airplane"


@pytest.mark.django_db
def test_route_str():
    country = Country.objects.create(name="Test Country")
    city = City.objects.create(name="Test City", country=country)
    airport1 = Airport.objects.create(
        name="Airport1",
        code="A1",
        closest_big_city=city
    )
    airport2 = Airport.objects.create(
        name="Airport2",
        code="A2",
        closest_big_city=city
    )
    route = Route.objects.create(
        source=airport1,
        destination=airport2,
        distance=500
    )
    assert (
        str(route)
        == f"Airport1 (A1) to Airport2 (A2) "
           f"(500 km / {500 * 0.621371:.2f} miles)"
    )


@pytest.mark.django_db
def test_crew_str():
    crew = Crew.objects.create(first_name="John", last_name="Doe")
    assert str(crew) == "John Doe"


@pytest.mark.django_db
def test_flight_str():
    country = Country.objects.create(name="Test Country")
    city = City.objects.create(name="Test City", country=country)
    airport1 = Airport.objects.create(
        name="Airport1",
        code="A1",
        closest_big_city=city
    )
    airport2 = Airport.objects.create(
        name="Airport2",
        code="A2",
        closest_big_city=city
    )
    route = Route.objects.create(
        source=airport1,
        destination=airport2,
        distance=500
    )
    airplane_type = AirplaneType.objects.create(name="Test Type")
    airplane = Airplane.objects.create(
        name="Test Airplane",
        rows=10,
        seats_in_row=4,
        airplane_type=airplane_type,
    )
    flight = Flight.objects.create(
        route=route,
        airplane=airplane,
        departure_time="2023-01-01T10:00:00Z",
        arrival_time="2023-01-01T12:00:00Z",
    )
    assert str(flight) == f"Flight {flight.id} on route {route}"


@pytest.mark.django_db
def test_order_str():
    user = User.objects.create_user(
        email="testuser@example.com", password="testpass"
    )  # Correct instantiation
    order = Order.objects.create(user=user)
    assert str(order) == f"Order {order.id} by {user.email}"


@pytest.mark.django_db
def test_ticket_str():
    user = User.objects.create_user(
        email="testuser@example.com", password="testpass"
    )  # Correct instantiation
    order = Order.objects.create(user=user)
    country = Country.objects.create(name="Test Country")
    city = City.objects.create(name="Test City", country=country)
    airport1 = Airport.objects.create(
        name="Airport1",
        code="A1",
        closest_big_city=city
    )
    airport2 = Airport.objects.create(
        name="Airport2",
        code="A2",
        closest_big_city=city
    )
    route = Route.objects.create(
        source=airport1,
        destination=airport2,
        distance=500
    )
    airplane_type = AirplaneType.objects.create(name="Test Type")
    airplane = Airplane.objects.create(
        name="Test Airplane",
        rows=10,
        seats_in_row=4,
        airplane_type=airplane_type
    )
    flight = Flight.objects.create(
        route=route,
        airplane=airplane,
        departure_time="2023-01-01T10:00:00Z",
        arrival_time="2023-01-01T12:00:00Z",
    )
    ticket = Ticket.objects.create(
        row=1,
        seat=1,
        flight=flight,
        order=order
    )
    assert str(ticket) == f"Ticket {ticket.id} for flight {flight}"


@pytest.mark.django_db
def test_airplane_image_file_path():
    instance = Airplane(name="Test Airplane")
    filename = "example.jpg"
    path = airplane_image_file_path(instance, filename)
    expected_slug = slugify(instance.name)
    expected_extension = os.path.splitext(filename)[1]
    assert path.startswith(f"uploads/airplanes/{expected_slug}-")
    assert path.endswith(expected_extension)
