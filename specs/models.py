from django.db import models

from main.models import Category


class SearchFilterType(models.Model):

    CHECKBOX = "checkbox"

    HTML_TYPE_CHOICES = (
        (CHECKBOX, "Чекбокс"),
    )

    key = models.CharField("Ключ поиска", max_length=50, choices=HTML_TYPE_CHOICES, default=CHECKBOX)
    html_code = models.TextField("HTML код для страницы фильтрации")

    class Meta:
        verbose_name = "Тип поиска при фильтрации"
        verbose_name_plural = "Типы поиска при фильтрации"

    def __str__(self):
        return f"{self.get_key_display()}"


class SpecCategoryName(models.Model):

    category = models.ForeignKey(Category, models.CASCADE, verbose_name="Категория")
    name = models.CharField("Название характеристики", max_length=100)
    key = models.CharField("Ключ характеристики", max_length=100)
    search_filter_type = models.ForeignKey(SearchFilterType, models.CASCADE, verbose_name="Тип фильтра для поиска")
    use_in_product_shortlist_specs = models.BooleanField("Использовать для отображения в коротком описании товара", default=False)

    class Meta:
        unique_together = ("category", "name", "key")
        verbose_name = "Категория характеристики"
        verbose_name_plural = "Категории характеристик"

    def __str__(self):
        return f"Характеристики категории - {self.category.name} | {self.name}"

class Spec(models.Model):

    INT = "int"
    STR = "str"
    FLOAT = "float"
    BOOL = "bool"

    TYPE_CHOICES = (
        (INT, "Целое число"),
        (STR, "Строка"),
        (FLOAT, "Десятичная дробь"),
    )

    category = models.ForeignKey(Category, models.CASCADE, verbose_name="Категория характеристик", related_name="category_specs")
    spec_category = models.ForeignKey(SpecCategoryName, models.CASCADE, verbose_name="Название категории характеристик", related_name="specnames",)
    product = models.ForeignKey("main.Product", models.CASCADE, verbose_name="Товар", related_name="product_specs", null=True, blank=True)
    spec_unit = models.ForeignKey("SpecUnit", models.CASCADE, verbose_name="Единица измерения", null=True, blank=True)
    value = models.CharField("Значение характеристики", max_length=100)
    var_type = models.CharField("Тип значения", max_length=50, choices=TYPE_CHOICES, null=True, blank=True)

    class Meta:
        unique_together = ("category", "spec_category", "product", "value")
        verbose_name = "Характеристика товара"
        verbose_name_plural = "Характеристики товаров"

    def __str__(self):
        return " | ".join([
            self.category.name,
            self.spec_category.name,
            self.spec_category.key,
            self.value,
        ])

    def get_spec_unit(self):
        spec_unit = self.spec_unit
        if spec_unit:
            type_choices_reversed = {v: k for k, v in self.TYPE_CHOICES}
            if type_choices_reversed.get(spec_unit.unit) == self.BOOL:
                return self.value
            return f'{self.value} {self.spec_unit.unit}'
        else:
            return self.value



class SpecUnit(models.Model):

    category = models.ForeignKey(Category, models.CASCADE, verbose_name="Категория характеристик", )
    name = models.CharField("Название", max_length=100)
    unit = models.CharField("Единица измерения", max_length=10)

    class Meta:
        unique_together = ("category", "name", "unit")
        verbose_name = "Единица измерения характеристики"
        verbose_name_plural = "Единицы измерения характеристик"

    def __str__(self):
        return f"Единица измерения характеристики - {self.category.name} | {self.name} | {self.unit}"


class SpecUnitValidation(models.Model):

    INT = "int"
    STR = "str"
    FLOAT = "float"
    BOOL = "bool"

    TYPE_CHOICES = (
        (INT, "Целое число"),
        (STR, "Строка"),
        (FLOAT, "Десятичная дробь"),
        (BOOL, "Да/Нет"),
    )

    specunit = models.ForeignKey(SpecUnit, models.CASCADE, verbose_name="Единица измерения", )
    name = models.CharField("Имя единицы измерения для валидации", max_length=100)
    var_type = models.CharField("Тип значения", max_length=50, choices=TYPE_CHOICES)

    class Meta:
        unique_together = ("specunit", "name", "var_type")
        verbose_name = "Валидация единицы измерения товара"
        verbose_name_plural = "Валидации единиц измерения товаров"

    def __str__(self):
        return f"Валидация {self.specunit}"
















