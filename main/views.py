from collections import defaultdict
from decimal import Decimal

from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from django.db.models import Min, Max, Q
from django.http import HttpResponseRedirect
from django.db import transaction
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.views import View
from django.contrib import messages
from django.views.generic.detail import DetailView
from natsort import natsorted

from specs.models import Spec, SpecCategoryName
from utils.help_funcs import recalc_cart
from .models import Product, Customer, Category, CartItem, Order
from .mixins import CategoriesMixin, CartMixin, UserIsAuthenticatedMixin
from .forms import RegistrationForm, LoginForm, OrderForm


class IndexView(CategoriesMixin, CartMixin, View):

    def get(self, request, *args, **kwargs):
        products = Product.objects.all().order_by("?")[:4]
        ctx = {
            'products': products,
            'categories': self.categories,
            'cart': self.get_cart(),
        }
        return render(request, 'index.html', ctx)


class RegistrationView(View):

    @staticmethod
    def get(request, *args, **kwargs):
        form = RegistrationForm()
        ctx = {
            'form': form
        }
        return render(request, 'registration.html', ctx)


    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # обработка входящих данных после регистрации. Сохранение в БД
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.email = form.cleaned_data['email']
            new_user.username = form.cleaned_data['email']
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            Customer.objects.create(
                user=new_user,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address']
            )
            user = authenticate(
                username=new_user.username, password=form.cleaned_data['password']
            )
            login(request, user)
            return HttpResponseRedirect('/')
        ctx = {
            'form': form
        }
        return render(request, 'registration.html', ctx)


class LoginView(View):

    @staticmethod
    def get(request, *args, **kwargs):
        form = LoginForm()
        ctx = {
            'form': form
        }
        return render(request, 'login.html', ctx)

    @staticmethod
    def post(request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(
                email=email, password=password
            )
            if user:
                login(request, user)
                return HttpResponseRedirect('/')
        ctx = {
            'form': form
        }
        return render(request, 'login.html', ctx)


class ProductDetailView(DetailView, CategoriesMixin, CartMixin):

    model = Product
    context_object_name = 'product'
    template_name = 'product_detail.html'
    pk_url_kwarg = 'pk'




class CategoryDetailView(DetailView, CategoriesMixin, CartMixin):

    model = Category
    context_object_name = 'category'
    template_name = 'category_detail.html'
    pk_url_kwarg = 'pk'


    @staticmethod
    def get_specs_data(category):
        """
        Метод для получения характеристик для HTML
        """
        data = defaultdict(list)
        specs = Spec.objects.filter(category=category).select_related(
            'spec_category', 'spec_category__search_filter_type', 'spec_unit', 'product'
        ).distinct("value", "spec_category__key")
        for s in specs:
            data[(s.spec_category.name,
                  s.get_spec_unit(),
                  s.spec_category.key,
                  s.spec_category.search_filter_type.html_code)].append(s.value)

        result = defaultdict(list)
        result_for_sort = defaultdict(list)
        counter = 1
        for (spec_category, unit, key, html_code), values in data.items():
            for val in values:
                res = html_code.format(
                    id_="-".join([str(counter), key]),
                    key=key,
                    html_value=unit,
                    value=val
                )
                counter += 1
                result[spec_category].append({'res': res, 'val': val})
                result_for_sort[spec_category].append(val)

        for sc, v in result_for_sort.items():
            result_for_sort[sc] = natsorted(v)

        for spec, data in result.items():
            prepared_data = result_for_sort[spec]
            new_data = []
            for pos in prepared_data:
                for d in data:
                    if d['val'] == pos:
                        new_data.append(d['res'])
            result[spec] = new_data
        return result



    def set_paginated_qs(self, qs):
        paginator = Paginator(qs, 4)

        page_number = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)
        return page_obj



    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        category_obj = super().get_object()
        products = Product.objects.filter(category=category_obj)
        ctx['filter_data'] = {k: v for k, v in self.get_specs_data(category_obj).items()}
        ctx['price_range'] = products.aggregate(minimum=Min('price'), maximum=Max('price'))
        specs_list_from_query_string = list(self.request.GET.values())
        if not specs_list_from_query_string:
            ctx['page_obj'] = self.set_paginated_qs(products)
            return ctx

        q = Q()
        q.default = Q.AND
        data_for_q = {}
        min_price = self.request.GET.get('min-price')
        max_price = self.request.GET.get('max-price')
        prices_q = Q()
        if min_price:
            prices_q &= Q(price__gte=Decimal(min_price))
        if max_price:
            prices_q &= Q(price__lte=Decimal(max_price))

        spec_categories = SpecCategoryName.objects.filter(
            category=category_obj, key__in=list(self.request.GET.keys())
        )
        for item in spec_categories:
            if self.request.GET.get(item.key):
                data_for_q[item] = self.request.GET.getlist(item.key)

        for sc, values in data_for_q.items():
            q |= Q(spec_category=sc, value__in=values)

        specs = None
        if q:
            specs = Spec.objects.filter(q, category=category_obj)
        if specs:
            if self.request.GET.get('brand'):
                products = products.filter(prices_q, product_specs__in=specs, brand__name__in=self.request.GET.getlist('brand')).distinct()
            else:
                products = products.filter(prices_q, product_specs__in=specs).distinct()
        else:
            if self.request.GET.get('brand'):
                products = products.filter(prices_q, brand__name__in=self.request.GET.getlist('brand')).distinct()
            else:
                products = products.filter(prices_q)
        ctx['page_obj'] = self.set_paginated_qs(products)
        request_get = self.request.GET.copy()
        if len(request_get):
            if "page" in list(request_get.keys()):
                request_get.pop("page")
        self.request.GET = request_get
        return ctx



class CartView(View, CategoriesMixin, CartMixin):

    def get(self, request, *args, **kwargs):
        ctx = {
            'cart': self.get_cart(),
            'categories': self.categories,
        }
        return render(request, 'cart.html', ctx)


class AddToCartView(CartMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        qty = int(request.POST.get('qty', 1))
        p = Product.objects.get(id=product_id)
        cart = self.get_cart()
        if p in [item.product for item in cart.items.all()]:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            cart.add(p, qty)
            recalc_cart(cart)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class ChangeQtyInCartView(CartMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        item_id = request.POST.get('item_id')
        qty = int(request.POST.get('qty', 1))
        cart_item = CartItem.objects.get(id=item_id)
        cart = self.get_cart()
        if cart_item in [item for item in cart.items.all()]:
            cart.change_item_qty(cart_item, qty)
            recalc_cart(cart)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class RemoveFromCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        item_id = kwargs.get('item_id')
        cart = self.get_cart()
        cart_item = CartItem.objects.get(id=item_id)
        if cart_item in [item for item in cart.items.all()]:
            cart.remove(cart_item)
            recalc_cart(cart)
        return HttpResponseRedirect('/cart/')


class MakeOrderView(CartMixin, CategoriesMixin, UserIsAuthenticatedMixin, View):

    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        form = OrderForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'phone': customer.phone,
            'address': customer.address,
            # 'email': request.user.email,
        })
        cart = self.get_cart()
        if cart and not cart.items.count():
            if request.Meta.get('HTTP_REFERER'):
                return HttpResponseRedirect(request.Meta['HTTP_REFERER'])
            return HttpResponseRedirect('/')
        ctx = {
            'form': form,
            'cart': self.get_cart(),
            'categories': self.categories,
        }
        return render(request,'order.html', ctx)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        customer = Customer.objects.get(user=request.user)
        cart = self.get_cart()
        if form.is_valid():
            Order.objects.create(
                customer=customer,
                order_cost=cart.total_cost,
                cart=cart,
                **form.cleaned_data
            )
            cart.in_order = True
            cart.save()
            messages.info(request, mark_safe(f'Спасибо за Ваш заказ! Можете отслеживать статус заказа <a href="/profile/">личном кабинете</a>'))
            return HttpResponseRedirect('/')
        return HttpResponseRedirect('/make-order/')


class ProfileView(UserIsAuthenticatedMixin, View):

    @staticmethod
    def get(request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        orders = Order.objects.filter(customer=customer)
        ctx = {
            'customer': customer,
            'orders': orders,
        }
        return render(request, 'profile.html', ctx)





















