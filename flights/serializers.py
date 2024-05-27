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
    Ticket, Crew,
)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "name")


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ("id", "name", "country")


class AirportSerializer(serializers.ModelSerializer):
    closest_big_city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(),
        source='closest_big_city',
        write_only=True
    )

    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city_id")

    def create(self, validated_data):
        closest_big_city = validated_data.pop('closest_big_city')
        airport = Airport.objects.create(closest_big_city=closest_big_city, **validated_data)
        return airport


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = serializers.PrimaryKeyRelatedField(queryset=AirplaneType.objects.all())
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
        airplane_type_data = validated_data.pop('airplane_type')
        airplane_type, created = AirplaneType.objects.get_or_create(**airplane_type_data)
        airplane = Airplane.objects.create(airplane_type=airplane_type, **validated_data)
        return airplane

    def update(self, instance, validated_data):
        airplane_type_data = validated_data.pop('airplane_type')
        airplane_type, created = AirplaneType.objects.get_or_create(**airplane_type_data)

        instance.name = validated_data.get('name', instance.name)
        instance.rows = validated_data.get('rows', instance.rows)
        instance.seats_in_row = validated_data.get('seats_in_row', instance.seats_in_row)
        instance.airplane_type = airplane_type
        instance.save()
        return instance


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())
    destination = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())
    distance_display = serializers.SerializerMethodField()

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance", "distance_display")

    def get_distance_display(self, obj):
        distance_miles = obj.distance * 0.621371
        return f"{obj.distance} km ({distance_miles:.2f} miles)"


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class FlightSerializer(serializers.ModelSerializer):
    route = RouteSerializer()
    airplane = serializers.PrimaryKeyRelatedField(queryset=Airplane.objects.all())
    airplane_name = serializers.CharField(source='airplane.name', read_only=True)
    airplane_capacity = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "crew", "airplane_name", "airplane_capacity", "departure_time", "arrival_time")

    def get_airplane_capacity(self, obj):
        return obj.airplane.capacity

    def create(self, validated_data):
        route_data = validated_data.pop('route')
        airplane_data = validated_data.pop('airplane')

        flight = Flight.objects.create(**validated_data)

        Route.objects.create(flight=flight, **route_data)

        Airplane.objects.create(flight=flight, **airplane_data)

        return flight


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "created_at", "user")


class TicketSerializer(serializers.ModelSerializer):
    flight = FlightSerializer()
    order = OrderSerializer()

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order")
