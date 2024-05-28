from users.models import User
from rest_framework import serializers

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
    Crew,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email")


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "name")


class CitySerializer(serializers.ModelSerializer):
    country_name = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = ("id", "name", "country", "country_name")

    def get_country_name(self, obj):
        return obj.country.name


class AirportSerializer(serializers.ModelSerializer):
    closest_big_city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(), source="closest_big_city", write_only=True
    )

    class Meta:
        model = Airport
        fields = ("id", "name", "code", "closest_big_city_id")

    def create(self, validated_data):
        closest_big_city = validated_data.pop("closest_big_city")
        airport = Airport.objects.create(
            closest_big_city=closest_big_city, **validated_data
        )
        return airport


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = serializers.PrimaryKeyRelatedField(
        queryset=AirplaneType.objects.all()
    )
    capacity = serializers.SerializerMethodField()

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "image",
            "airplane_type",
            "capacity",
        )

    def get_capacity(self, obj):
        return obj.capacity

    def create(self, validated_data):
        airplane_type = validated_data.pop("airplane_type")
        airplane = Airplane.objects.create(
            airplane_type=airplane_type, **validated_data
        )
        return airplane

    def update(self, instance, validated_data):
        airplane_type = validated_data.pop("airplane_type")

        instance.name = validated_data.get("name", instance.name)
        instance.rows = validated_data.get("rows", instance.rows)
        instance.seats_in_row = validated_data.get(
            "seats_in_row", instance.seats_in_row
        )
        instance.airplane_type = airplane_type
        instance.save()
        return instance


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())
    source_name = serializers.SerializerMethodField()
    destination = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())
    destination_name = serializers.SerializerMethodField()
    distance_display = serializers.SerializerMethodField()

    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "distance",
            "distance_display",
            "source_name",
            "destination_name",
        )

    def get_distance_display(self, obj):
        distance_miles = obj.distance * 0.621371
        return f"{obj.distance} km ({distance_miles:.2f} miles)"

    def get_source_name(self, obj):
        return obj.source.name

    def get_destination_name(self, obj):
        return obj.destination.name


class CrewSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class FlightSerializer(serializers.ModelSerializer):
    route = serializers.PrimaryKeyRelatedField(queryset=Route.objects.all())
    airplane = serializers.PrimaryKeyRelatedField(queryset=Airplane.objects.all())
    airplane_name = serializers.CharField(source="airplane.name", read_only=True)
    airplane_capacity = serializers.SerializerMethodField()
    crew = CrewSerializer(many=True, read_only=True)
    crew_ids = serializers.PrimaryKeyRelatedField(
        queryset=Crew.objects.all(), many=True, write_only=True
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "crew",
            "crew_ids",
            "airplane_name",
            "airplane_capacity",
            "departure_time",
            "arrival_time",
        )

    def get_airplane_capacity(self, obj):
        return obj.airplane.capacity

    def create(self, validated_data):
        route_data = validated_data.pop("route")
        airplane = validated_data.pop("airplane")
        crew_data = validated_data.pop("crew_ids", None)

        route = Route.objects.create(**route_data)
        flight = Flight.objects.create(airplane=airplane, route=route, **validated_data)
        if crew_data:
            flight.crew.set(crew_data)

        return flight

    def update(self, instance, validated_data):
        route_data = validated_data.pop("route")
        airplane = validated_data.pop("airplane")
        crew_data = validated_data.pop("crew_ids", None)

        for attr, value in route_data.items():
            setattr(instance.route, attr, value)
        instance.route.save()

        instance.airplane = airplane
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if crew_data:
            instance.crew.set(crew_data)

        return instance


class OrderReadOnlySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Order
        fields = ("id", "created_at", "user")


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "created_at", "user")


class TicketReadOnlySerializer(serializers.ModelSerializer):
    flight = FlightSerializer()
    order = OrderReadOnlySerializer()

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order")


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order")
