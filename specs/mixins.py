from main.models import Product


class SearchResultsCategory:

    EXCLUDED_MODELS = ['specunitvalidation']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request,queryset, search_term)
        request_full_path = request.get_full_path()
        for excluded_models in self.EXCLUDED_MODELS:
            if excluded_models in request_full_path:
                return queryset, use_distinct
        if 'autocomplete' in request_full_path:
            product_id = [i for i in request.META['HTTP_REFERER'].split('/') if i.isnumeric()]
            if product_id:
                product_id = product_id[0]
                p = Product.objects.get(id=product_id)
                queryset = queryset.filter(category=p.category)
        return queryset, use_distinct


