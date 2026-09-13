from django.contrib import admin
from django.urls import path

from config import views


urlpatterns = [

    # =========================
    # Main pages
    # =========================

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "customer/",
        views.customer_page,
        name="customer_page"
    ),

    path(
        "artisan/",
        views.artisan_page,
        name="artisan_page"
    ),


    # =========================
    # Artisan authentication
    # =========================

    path(
        "artisan/login/",
        views.artisan_login_page,
        name="artisan_login_page"
    ),

    path(
        "artisan/register/",
        views.artisan_register_page,
        name="artisan_register_page"
    ),


    # =========================
    # Artisan workflow pages
    # =========================

    path(
        "artisan/dashboard/",
        views.artisan_dashboard_page,
        name="artisan_dashboard"
    ),

    path(
        "artisan/upload/",
        views.artisan_upload_page,
        name="artisan_upload"
    ),

    path(
        "artisan/review/",
        views.artisan_review_page,
        name="artisan_review"
    ),

    path(
        "artisan/price/",
        views.artisan_price_page,
        name="artisan_price"
    ),

    path(
        "artisan/publish/",
        views.artisan_publish_page,
        name="artisan_publish"
    ),


    # =========================
    # Artisan product pages
    # =========================

    path(
        "artisan/product/edit/",
        views.artisan_edit_page,
        name="artisan_edit"
    ),

    path(
        "artisan/product/view/",
        views.artisan_view_page,
        name="artisan_view"
    ),


    # =========================
    # AI APIs - Image + Voice
    # =========================

    path(
        "api/analyze-product-image/",
        views.analyze_product_image,
        name="analyze_product_image"
    ),

    path(
        "api/transcribe-product-voice/",
        views.transcribe_product_voice,
        name="transcribe_product_voice"
    ),


    # =========================
    # ML Price Prediction API
    # =========================

    path(
        "api/predict-price/",
        views.predict_price,
        name="predict_price"
    ),


    # =========================
    # Artisan profile
    # =========================

    path(
        "artisan/profile/page/",
        views.artisan_profile_page,
        name="artisan_profile_page"
    ),

    path(
        "artisan/profile/create/",
        views.create_artisan_profile,
        name="create_artisan_profile"
    ),

    path(
        "artisan/profile/",
        views.get_artisan_profile,
        name="get_artisan_profile"
    ),

    path(
        "artisan/profile/update/",
        views.update_artisan_profile,
        name="update_artisan_profile"
    ),


    # =========================
    # Customer profile
    # =========================

    path(
        "customer/profile/create/",
        views.create_customer_profile,
        name="create_customer_profile"
    ),

    path(
        "customer/profile/",
        views.get_customer_profile,
        name="get_customer_profile"
    ),

    path(
        "customer/profile/update/",
        views.update_customer_profile,
        name="update_customer_profile"
    ),


    # =========================
    # Authentication
    # =========================

    path(
        "auth/protected-test/",
        views.protected_test,
        name="protected_test"
    ),

    path(
        "auth/signup/",
        views.signup,
        name="signup"
    ),

    path(
        "auth/login/",
        views.login_user,
        name="login"
    ),

    path(
        "auth/logout/",
        views.logout_user,
        name="logout"
    ),


    # =========================
    # Product APIs
    # =========================

    path(
        "products/create/",
        views.create_product,
        name="create_product"
    ),

    path(
        "products/mine/",
        views.get_my_products,
        name="get_my_products"
    ),

    path(
        "products/<uuid:product_id>/",
        views.get_product,
        name="get_product"
    ),

    path(
        "products/<uuid:product_id>/update/",
        views.update_product,
        name="update_product"
    ),

    path(
        "products/<uuid:product_id>/delete/",
        views.delete_product,
        name="delete_product"
    ),

    path(
        "products/<uuid:product_id>/publish/",
        views.publish_product,
        name="publish_product"
    ),

    path(
        "products/<uuid:product_id>/image/",
        views.upload_product_image,
        name="upload_product_image"
    ),


    # =========================
    # Marketplace
    # =========================

    path(
        "marketplace/products/",
        views.public_products,
        name="public_products"
    ),

    path(
        "marketplace/products/<uuid:product_id>/",
        views.public_product_detail,
        name="public_product_detail"
    ),


    # =========================
    # Orders
    # =========================

    path(
        "orders/create/",
        views.create_order,
        name="create_order"
    ),

    path(
        "orders/mine/",
        views.get_my_orders,
        name="get_my_orders"
    ),

    path(
        "orders/<uuid:order_id>/",
        views.get_order_detail,
        name="get_order_detail"
    ),

    path(
        "orders/<uuid:order_id>/status/",
        views.update_order_status,
        name="update_order_status"
    ),

    path(
        "artisan/orders/",
        views.get_artisan_orders,
        name="get_artisan_orders"
    ),


    # =========================
    # Transactions
    # =========================

    path(
        "transactions/create/",
        views.create_transaction,
        name="create_transaction"
    ),

    path(
        "transactions/mine/",
        views.get_my_transactions,
        name="get_my_transactions"
    ),

    path(
        "transactions/<uuid:transaction_id>/",
        views.get_transaction,
        name="get_transaction"
    ),

    path(
        "transactions/<uuid:transaction_id>/status/",
        views.update_transaction_status,
        name="update_transaction_status"
    ),


    # =========================
    # Django Admin
    # =========================

    path(
        "admin/",
        admin.site.urls
    ),
]