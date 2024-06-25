from django.db.models import Sum, Count
from django.utils.safestring import mark_safe


def convert_to_rubles_to_html(obj):
    value = f'{obj.normalize():,}'.replace(',', ' ')
    return mark_safe(" ".join([value, "<i class='fa-solid fa-ruble-sign'></i>"]))


def recalc_cart(cart):
    cart_data = cart.items.aggregate(Sum("total_cost"), Count("id"))
    if cart_data.get("total_cost__sum"):
        cart.total_cost = cart_data["total_cost__sum"]
    else:
        cart.total_cost = 0
    cart.save()







