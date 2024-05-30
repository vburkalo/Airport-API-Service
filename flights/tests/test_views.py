from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import (
    APIClient,
    APITestCase,
)

from flights.models import (
    Country,
    City,
    Airport,
    AirplaneType,
    Airplane,
    Route,
    Flight,
    Order,
    Ticket,
)
from flights.serializers import (
    CountrySerializer,
    CitySerializer,
    AirportSerializer,
    AirplaneSerializer,
    TicketReadOnlySerializer,
)
from users.models import User


class CountryViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="password"
        )
        self.client.force_authenticate(user=self.user)
        self.country1 = Country.objects.create(name="Country 1")
        self.country2 = Country.objects.create(name="Country 2")

    def test_list_countries(self):
        response = self.client.get(reverse("flights:country-list"))
        countries = Country.objects.all()
        serializer = CountrySerializer(countries, many=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_country(self):
        response = self.client.get(
            reverse("flights:country-detail", args=[self.country1.id])
        )
        country = Country.objects.get(id=self.country1.id)
        serializer = CountrySerializer(country)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)


class CityViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="password"
        )
        self.client.force_authenticate(user=self.user)
        self.country1 = Country.objects.create(name="Country 1")
        self.city1 = City.objects.create(name="City 1", country=self.country1)
        self.city2 = City.objects.create(name="City 2", country=self.country1)

    def test_list_cities(self):
        response = self.client.get(reverse("flights:city-list"))
        cities = City.objects.all().select_related("country")
        serializer = CitySerializer(cities, many=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_city(self):
        response = self.client.get(reverse(
            "flights:city-detail", args=[self.city1.id])
        )
        city = City.objects.select_related("country").get(id=self.city1.id)
        serializer = CitySerializer(city)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)

    def test_filter_by_country(self):
        response = self.client.get(
            reverse("flights:city-list") + "?country=" + str(self.country1.id)
        )
        cities = City.objects.filter(country=self.country1)
        serializer = CitySerializer(cities, many=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)


class AirportViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="password"
        )
        self.client.force_authenticate(user=self.user)
        self.country1 = Country.objects.create(name="Country 1")
        self.country2 = Country.objects.create(name="Country 2")
        self.city1 = City.objects.create(name="City 1", country=self.country1)
        self.city2 = City.objects.create(name="City 2", country=self.country2)
        self.airport1 = Airport.objects.create(
            name="Airport 1", code="AAA", closest_big_city=self.city1
        )
        self.airport2 = Airport.objects.create(
            name="Airport 2", code="BBB", closest_big_city=self.city2
        )

    def test_list_airports_without_filter(self):
        url = reverse("flights:airport-list")
        response = self.client.get(url)
        airports = (
            Airport.objects.all()
            .select_related("closest_big_city__country")
        )
        serializer = AirportSerializer(airports, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_list_airports_with_city_filter(self):
        url = reverse("flights:airport-list") + "?city=1"
        response = self.client.get(url)
        airports = Airport.objects.filter(
            closest_big_city_id=1
        ).select_related(
            "closest_big_city__country"
        )
        serializer = AirportSerializer(airports, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_list_airports_with_invalid_city_filter(self):
        url = reverse("flights:airport-list") + "?city=abc"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AirplaneViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="password"
        )
        self.client.force_authenticate(user=self.user)
        self.type1 = AirplaneType.objects.create(name="Type 1")
        self.type2 = AirplaneType.objects.create(name="Type 2")
        self.airplane1 = Airplane.objects.create(
            name="Airplane 1",
            airplane_type=self.type1,
            rows=100,
            seats_in_row=6
        )
        self.airplane2 = Airplane.objects.create(
            name="Airplane 2",
            airplane_type=self.type2,
            rows=150,
            seats_in_row=6
        )

    def test_list_airplanes_without_filter(self):
        url = reverse("flights:airplane-list")
        response = self.client.get(url)
        airplanes = Airplane.objects.all().select_related("airplane_type")
        serializer = AirplaneSerializer(airplanes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_list_airplanes_with_type_filter(self):
        url = reverse("flights:airplane-list") + "?airplane_types=1"
        response = self.client.get(url)
        airplanes = Airplane.objects.filter(airplane_type_id=1).select_related(
            "airplane_type"
        )
        serializer = AirplaneSerializer(airplanes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_list_airplanes_with_invalid_type_filter(self):
        url = reverse("flights:airplane-list") + "?airplane_types=abc"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RouteViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)
        self.country = Country.objects.create(name="Country Name")
        self.big_city1 = City.objects.create(
            name="Big City 1",
            country=self.country
        )
        self.big_city2 = City.objects.create(
            name="Big City 2",
            country=self.country
        )
        self.big_city3 = City.objects.create(
            name="Big City 3",
            country=self.country
        )
        self.airport1 = Airport.objects.create(
            name="Airport 1",
            code="AAA",
            closest_big_city=self.big_city1
        )
        self.airport2 = Airport.objects.create(
            name="Airport 2",
            code="BBB",
            closest_big_city=self.big_city2
        )
        self.airport3 = Airport.objects.create(
            name="Airport 3",
            code="CCC",
            closest_big_city=self.big_city3
        )
        self.route1 = Route.objects.create(
            source=self.airport1,
            destination=self.airport2,
            distance=100
        )
        self.route2 = Route.objects.create(
            source=self.airport2,
            destination=self.airport3,
            distance=150
        )
        self.route3 = Route.objects.create(
            source=self.airport3,
            destination=self.airport1,
            distance=200
        )

    def test_list_routes(self):
        url = reverse("flights:route-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_list_routes_with_source_filter(self):
        url = (
                reverse("flights:route-list")
                + "?source=" + str(self.airport1.id)
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_routes_with_destination_filter(self):
        url = (
                reverse("flights:route-list")
                + "?destination=" + str(self.airport2.id)
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_routes_with_source_and_destination_filter(self):
        url = (
                reverse("flights:route-list")
                + "?source="
                + str(self.airport1.id)
                + "&destination="
                + str(self.airport2.id)
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class FlightViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

        self.airplane_type1 = AirplaneType.objects.create(name="Type 1")
        self.airplane_type2 = AirplaneType.objects.create(name="Type 2")

        self.country1 = Country.objects.create(name="Country 1")
        self.city1 = City.objects.create(name="City 1", country=self.country1)
        self.country2 = Country.objects.create(name="Country 2")
        self.city2 = City.objects.create(name="City 2", country=self.country2)

        self.airport1 = Airport.objects.create(
            name="Airport 1", code="AAB", closest_big_city=self.city1
        )
        self.airport2 = Airport.objects.create(
            name="Airport 2", code="BBC", closest_big_city=self.city1
        )
        self.airport3 = Airport.objects.create(
            name="Airport 3", code="QWA", closest_big_city=self.city2
        )

        self.route1 = Route.objects.create(
            source=self.airport1, destination=self.airport2, distance=100
        )
        self.route2 = Route.objects.create(
            source=self.airport2, destination=self.airport3, distance=150
        )
        self.airplane1 = Airplane.objects.create(
            name="Airplane 1",
            rows=10,
            seats_in_row=20,
            airplane_type=self.airplane_type1,
        )
        self.airplane2 = Airplane.objects.create(
            name="Airplane 2",
            rows=10,
            seats_in_row=20,
            airplane_type=self.airplane_type2,
        )

        arrival_time1 = timezone.now() + timedelta(hours=2)
        arrival_time2 = timezone.now() + timedelta(hours=3)

        self.flight1 = Flight.objects.create(
            route=self.route1,
            airplane=self.airplane1,
            departure_time=timezone.now(),
            arrival_time=arrival_time1,
        )
        self.flight2 = Flight.objects.create(
            route=self.route2,
            airplane=self.airplane2,
            departure_time=timezone.now(),
            arrival_time=arrival_time2,
        )

    def test_list_flights_without_filters(self):
        url = reverse("flights:flight-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_flights_with_route_filter(self):
        url = reverse("flights:flight-list") + "?route=" + str(self.route1.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["route"], self.route1.id)

    def test_list_flights_with_airplane_filter(self):
        url = (
                reverse("flights:flight-list")
                + "?airplane=" + str(self.airplane2.id)
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["airplane"], self.airplane2.id)

    def test_list_flights_with_route_and_airplane_filters(self):
        url = (
                reverse("flights:flight-list")
                + "?route="
                + str(self.route1.id)
                + "&airplane="
                + str(self.airplane1.id)
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["route"], self.route1.id)
        self.assertEqual(response.data[0]["airplane"], self.airplane1.id)

    def test_list_flights_with_invalid_filters(self):
        url = reverse("flights:flight-list") + "?route=abc&airplane=xyz"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TicketViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="password"
        )
        self.client.force_authenticate(user=self.user)

        self.country = Country.objects.create(name="Country 1")
        self.city = City.objects.create(name="City 1", country=self.country)
        self.airport = Airport.objects.create(
            name="Airport 1", code="AAA", closest_big_city=self.city
        )
        self.airplane_type = AirplaneType.objects.create(name="Type 1")
        self.airplane = Airplane.objects.create(
            name="Airplane 1",
            rows=100,
            seats_in_row=6,
            airplane_type=self.airplane_type,
        )
        self.route = Route.objects.create(
            source=self.airport, destination=self.airport, distance=500
        )

        self.flight1 = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timedelta(hours=2),
        )
        self.flight2 = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now() + timedelta(days=1),
            arrival_time=timezone.now() + timedelta(days=1, hours=2),
        )

        self.order1 = Order.objects.create(user=self.user)
        self.order2 = Order.objects.create(user=self.user)

        self.ticket1 = Ticket.objects.create(
            flight=self.flight1, order=self.order1, seat="1", row=1
        )
        self.ticket2 = Ticket.objects.create(
            flight=self.flight2, order=self.order2, seat="2", row=2
        )

    def test_list_tickets_without_filter(self):
        url = reverse("flights:ticket-list")
        response = self.client.get(url)
        tickets = Ticket.objects.all().select_related("flight", "order")
        serializer = TicketReadOnlySerializer(tickets, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_list_tickets_with_flight_filter(self):
        url = (
                reverse("flights:ticket-list")
                + "?flight=" + str(self.flight1.id)
        )
        response = self.client.get(url)
        tickets = Ticket.objects.filter(
            flight_id=self.flight1.id
        ).select_related(
            "flight", "order"
        )
        serializer = TicketReadOnlySerializer(tickets, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_list_tickets_with_order_filter(self):
        url = reverse("flights:ticket-list") + "?order=" + str(self.order1.id)
        response = self.client.get(url)
        tickets = Ticket.objects.filter(
            order_id=self.order1.id
        ).select_related(
            "flight", "order"
        )
        serializer = TicketReadOnlySerializer(tickets, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_list_tickets_with_flight_and_order_filter(self):
        url = (
                reverse("flights:ticket-list")
                + "?flight="
                + str(self.flight1.id)
                + "&order="
                + str(self.order1.id)
        )
        response = self.client.get(url)
        tickets = Ticket.objects.filter(
            flight_id=self.flight1.id, order_id=self.order1.id
        ).select_related("flight", "order")
        serializer = TicketReadOnlySerializer(tickets, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_list_tickets_with_invalid_flight_filter(self):
        url = reverse("flights:ticket-list") + "?flight=abc"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_tickets_with_invalid_order_filter(self):
        url = reverse("flights:ticket-list") + "?order=abc"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_tickets_with_invalid_flight_and_order_filter(self):
        url = reverse("flights:ticket-list") + "?flight=abc&order=xyz"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
