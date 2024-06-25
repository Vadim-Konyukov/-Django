from django.http import HttpResponseRedirect
from django.views.generic.base import ContextMixin

from main.models import Category, Customer, Cart


class UserIsAuthenticatedMixin:
    """
        Проверка авторизации
    """
    @staticmethod
    def _is_authenticated(request):
        if not request.user.is_authenticated:
            return False
        return True

    def dispatch(self, request, *args, **kwargs):
        request_full_path = request.get_full_path()
        if 'login' in request_full_path or 'registration' in request_full_path:
            if self._is_authenticated(request):
                if request.META.get('HTTP_REFERER'):
                    return HttpResponseRedirect(request.META['HTTP_REFERER'])
                else:
                    return HttpResponseRedirect('/')
            else:
                return super().dispatch(request, *args, **kwargs)
        else:
            if self._is_authenticated(request):
                return super().dispatch(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('/login/')


class CartMixin(ContextMixin):
    """
    Вывод корзины в шаблон
    """
    def get_cart(self):
        # Получаем корзину для текущего покупателя
        if self.request.user.is_authenticated:
            customer = Customer.objects.filter(user=self.request.user).first()
            cart = Cart.objects.filter(in_order=False, owner=customer).first()
            if not customer:
                customer = Customer.objects.create(
                    user=self.request.user
                )
            if not cart:
                cart = Cart.objects.create(owner=customer)
                return cart
            return cart
        return Cart.objects.none()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cart'] = self.get_cart()
        return ctx


    def get_contex_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cart'] = self.get_cart()
        return ctx


class CategoriesMixin(ContextMixin):
    """
    Вывод категорий в шаблон
    """
    @property
    def categories(self):
        return Category.objects.all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        return ctx




















