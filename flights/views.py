from drf_spectacular import openapi
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets
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
from flights.permissions import IsAdminOrIfAuthenticatedReadOnly
from flights.serializers import (
    CountrySerializer,
    CitySerializer,
    AirportSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    RouteSerializer,
    FlightSerializer,
    OrderSerializer,
    TicketSerializer,
)


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all().select_related("country")
    serializer_class = CitySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "country",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by country id (ex. ?country=1,2)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        country_ids = request.query_params.getlist('country')

        if country_ids:
            country_ids = [int(cid) for cid in country_ids if cid.isdigit()]
            self.queryset = self.queryset.filter(country_id__in=country_ids)

        return super().list(request, *args, **kwargs)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all().select_related("closest_big_city__country")
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "city",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by closest big city id (ex. ?city=1,2)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        city_ids = request.query_params.getlist('city')

        if city_ids:
            city_ids = [int(cid) for cid in city_ids if cid.isdigit()]
            self.queryset = self.queryset.filter(closest_big_city_id__in=city_ids)

        return super().list(request, *args, **kwargs)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all().select_related("airplane_type")
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "airplane_types",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by airplane type id (ex. ?airplane_types=2,3)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of airplanes by type"""
        airplane_types = request.query_params.getlist('airplane_types')

        if airplane_types:
            airplane_types = [int(type_id) for type_id in airplane_types if type_id.isdigit()]
            self.queryset = self.queryset.filter(airplane_type_id__in=airplane_types)

        return super().list(request, *args, **kwargs)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related("source", "destination")
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by source airport id (ex. ?source=1,2)",
            ),
            OpenApiParameter(
                "destination",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by destination airport id (ex. ?destination=1,2)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        source_ids = request.query_params.getlist('source')
        destination_ids = request.query_params.getlist('destination')

        if source_ids:
            source_ids = [int(sid) for sid in source_ids if sid.isdigit()]
            self.queryset = self.queryset.filter(source_id__in=source_ids)

        if destination_ids:
            destination_ids = [int(did) for did in destination_ids if did.isdigit()]
            self.queryset = self.queryset.filter(destination_id__in=destination_ids)

        return super().list(request, *args, **kwargs)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all().select_related("route", "airplane")
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "route",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by route id (ex. ?route=1,2)",
            ),
            OpenApiParameter(
                "airplane",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by airplane id (ex. ?airplane=1,2)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        route_ids = request.query_params.getlist('route')
        airplane_ids = request.query_params.getlist('airplane')

        if route_ids:
            route_ids = [int(rid) for rid in route_ids if rid.isdigit()]
            self.queryset = self.queryset.filter(route_id__in=route_ids)

        if airplane_ids:
            airplane_ids = [int(aid) for aid in airplane_ids if aid.isdigit()]
            self.queryset = self.queryset.filter(airplane_id__in=airplane_ids)

        return super().list(request, *args, **kwargs)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().select_related("user")
    serializer_class = OrderSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().select_related("flight", "order")
    serializer_class = TicketSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "flight",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by flight id (ex. ?flight=1,2)",
            ),
            OpenApiParameter(
                "order",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by order id (ex. ?order=1,2)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        flight_ids = request.query_params.getlist('flight')
        order_ids = request.query_params.getlist('order')

        if flight_ids:
            flight_ids = [int(fid) for fid in flight_ids if fid.isdigit()]
            self.queryset = self.queryset.filter(flight_id__in=flight_ids)

        if order_ids:
            order_ids = [int(oid) for oid in order_ids if oid.isdigit()]
            self.queryset = self.queryset.filter(order_id__in=order_ids)

        return super().list(request, *args, **kwargs)
