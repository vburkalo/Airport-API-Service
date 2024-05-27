import os
import uuid

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Country(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=64)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=64)
    closest_big_city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class AirplaneType(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


def airplane_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/airplanes/", filename)


class Airplane(models.Model):
    name = models.CharField(max_length=64)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    image = models.ImageField(null=True, upload_to=airplane_image_file_path)
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)

    class Meta:
        ordering = ["name"]

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Airport, related_name="routes_from", on_delete=models.CASCADE
    )
    destination = models.ForeignKey(
        Airport, related_name="routes_to", on_delete=models.CASCADE
    )
    distance = models.IntegerField()

    def __str__(self):
        distance_km = self.distance
        distance_miles = self.distance * 0.621371
        return f"{self.source} to {self.destination} ({distance_km} km / {distance_miles:.2f} miles)"


class Crew(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)

    def __str__(self):
        return self.first_name + " " + self.last_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    crew = models.ForeignKey(Crew, on_delete=models.CASCADE, default=1)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return f"Flight {self.id} on route {self.route}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    def __str__(self):
        return f"Order {self.id} by {self.user}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return f"Ticket {self.id} for flight {self.flight}"
