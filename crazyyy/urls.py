from django.urls import path
from django.views.generic import TemplateView

from crazyyy import views


urlpatterns = [
    # Home
    path("", views.index, name="home"),

    # Artisan / Seller
    path(
        "seller/",
        TemplateView.as_view(template_name="artisan-login.html"),
        name="seller",
    ),

    path(
        "seller/register/",
        TemplateView.as_view(template_name="artisan-register.html"),
        name="seller-register",
    ),

    path(
        "seller/dashboard/",
        TemplateView.as_view(template_name="artisan-dashboard.html"),
        name="seller-dashboard",
    ),

    path(
        "seller/profile/",
        TemplateView.as_view(template_name="artisan-profile.html"),
        name="seller-profile",
    ),

    path(
        "seller/publish/",
        TemplateView.as_view(template_name="artisan-publish-product.html"),
        name="seller-publish",
    ),

    path(
        "seller/price-prediction/",
        TemplateView.as_view(template_name="artisan-price-prediction.html"),
        name="seller-price-prediction",
    ),

    path(
        "seller/upload/",
        TemplateView.as_view(template_name="artisan-upload-camera-fixed.html"),
        name="seller-upload",
    ),
]