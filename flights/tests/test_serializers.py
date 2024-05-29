import pytest
from django.contrib.auth import get_user_model
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
)
from flights.serializers import (
    CountrySerializer,
    CitySerializer,
    AirportSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    RouteSerializer,
    CrewSerializer,
    FlightSerializer,
    OrderSerializer,
    TicketSerializer,
)

User = get_user_model()


@pytest.fixture
def sample_country():
    return Country.objects.create(name="Test Country")


@pytest.fixture
def sample_city(sample_country):
    return City.objects.create(name="Test City", country=sample_country)


@pytest.fixture
def sample_airport(sample_city):
    return Airport.objects.create(
        name="Test Airport", code="TST", closest_big_city=sample_city
    )


@pytest.fixture
def sample_airplane_type():
    return AirplaneType.objects.create(name="Test Airplane Type")


@pytest.fixture
def sample_airplane(sample_airplane_type):
    return Airplane.objects.create(
        name="Test Airplane",
        rows=10,
        seats_in_row=6,
        airplane_type=sample_airplane_type,
    )


@pytest.fixture
def sample_route(sample_airport):
    destination_airport = Airport.objects.create(
        name="Destination Airport",
        code="DST",
        closest_big_city=sample_airport.closest_big_city,
    )
    return Route.objects.create(
        source=sample_airport, destination=destination_airport, distance=1000
    )


@pytest.fixture
def sample_crew():
    return Crew.objects.create(first_name="John", last_name="Doe")


@pytest.fixture
def sample_flight(sample_route, sample_airplane, sample_crew):
    flight = Flight.objects.create(
        route=sample_route,
        airplane=sample_airplane,
        departure_time="2024-05-29T08:00:00Z",
        arrival_time="2024-05-29T10:00:00Z",
    )
    flight.crew.add(sample_crew)
    return flight


@pytest.fixture
def sample_user():
    return User.objects.create_user(
        email="test@example.com", password="testpassword"
    )


@pytest.fixture
def sample_order(sample_user):
    return Order.objects.create(user=sample_user)


@pytest.fixture
def sample_ticket(sample_flight, sample_order):
    return Ticket.objects.create(
        row=1, seat=1, flight=sample_flight, order=sample_order
    )


@pytest.mark.django_db
def test_country_serializer():
    country_data = {"name": "Test Country"}
    serializer = CountrySerializer(data=country_data)
    assert serializer.is_valid()
    country = serializer.save()
    assert country.name == country_data["name"]


@pytest.mark.django_db
def test_city_serializer(sample_city):
    serializer = CitySerializer(instance=sample_city)
    assert serializer.data["name"] == sample_city.name
    assert serializer.data["country_name"] == sample_city.country.name


@pytest.mark.django_db
def test_airport_serializer(sample_airport):
    serializer = AirportSerializer(instance=sample_airport)
    assert serializer.data["name"] == sample_airport.name
    assert serializer.data["code"] == sample_airport.code


@pytest.mark.django_db
def test_airplane_type_serializer(sample_airplane_type):
    serializer = AirplaneTypeSerializer(instance=sample_airplane_type)
    assert serializer.data["name"] == sample_airplane_type.name


@pytest.mark.django_db
def test_airplane_serializer(sample_airplane):
    serializer = AirplaneSerializer(instance=sample_airplane)
    assert serializer.data["name"] == sample_airplane.name
    assert serializer.data["rows"] == sample_airplane.rows
    assert serializer.data["seats_in_row"] == sample_airplane.seats_in_row
    assert serializer.data["airplane_type"] == sample_airplane.airplane_type.id


@pytest.mark.django_db
def test_route_serializer(sample_route):
    serializer = RouteSerializer(instance=sample_route)
    assert serializer.data["source"] == sample_route.source.id
    assert serializer.data["destination"] == sample_route.destination.id
    assert serializer.data["distance"] == sample_route.distance


@pytest.mark.django_db
def test_crew_serializer(sample_crew):
    serializer = CrewSerializer(instance=sample_crew)
    assert serializer.data["first_name"] == sample_crew.first_name
    assert serializer.data["last_name"] == sample_crew.last_name


@pytest.mark.django_db
def test_flight_serializer(sample_flight, sample_crew):
    serializer = FlightSerializer(instance=sample_flight)
    assert serializer.data["route"] == sample_flight.route.id
    assert serializer.data["airplane"] == sample_flight.airplane.id
    assert serializer.data["crew"][0]["id"] == sample_crew.id


@pytest.mark.django_db
def test_order_serializer(sample_order, sample_user):
    serializer = OrderSerializer(instance=sample_order)
    assert serializer.data["user"] == sample_user.id


@pytest.mark.django_db
def test_ticket_serializer(sample_ticket):
    serializer = TicketSerializer(instance=sample_ticket)
    assert serializer.data["row"] == sample_ticket.row
    assert serializer.data["seat"] == sample_ticket.seat
    assert serializer.data["flight"] == sample_ticket.flight.id
    assert serializer.data["order"] == sample_ticket.order.id
