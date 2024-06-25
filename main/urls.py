from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    IndexView,
    RegistrationView,
    LoginView,
    ProductDetailView,
    CategoryDetailView,
    CartView,
    AddToCartView,
    RemoveFromCartView,
    ChangeQtyInCartView,
    MakeOrderView,
    ProfileView,

    )

urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    path('product/<int:pk>/', ProductDetailView.as_view(), name="product"),
    path('category/<int:pk>/', CategoryDetailView.as_view(), name="category"),
    # авторизация-регистрация
    path('registration/', RegistrationView.as_view(), name="registration"),
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(next_page="/"), name="logout"),
    # Корзина
    path('cart/', CartView.as_view(), name="cart"),
    path('add-to-cart/', AddToCartView.as_view(), name="add_to_cart"),
    path('remove-from-cart/<int:item_id>/', RemoveFromCartView.as_view(), name="remove_from_cart"),
    path('change-qty/', ChangeQtyInCartView.as_view(), name="change_qty"),

    path('make-order/', MakeOrderView.as_view(), name="make_order"),
    path('profile/', ProfileView.as_view(), name="profile"),

]











