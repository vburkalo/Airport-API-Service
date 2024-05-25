from django.urls import path, include
from rest_framework.routers import DefaultRouter
from flights import views

router = DefaultRouter()
router.register("countries", views.CountryViewSet)
router.register("cities", views.CityViewSet)
router.register("airports", views.AirportViewSet)
router.register("airplane_types", views.AirplaneTypeViewSet)
router.register("airplanes", views.AirplaneViewSet)
router.register("routes", views.RouteViewSet)
router.register("flights", views.FlightViewSet)
router.register("orders", views.OrderViewSet)
router.register("tickets", views.TicketViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "flights"
