from django import forms
from django.contrib.auth import get_user_model  # Django форма. Если использовать свою форму - settings.AUTH_USER_MODEL

from main.models import Order

User = get_user_model()


class OrderForm(forms.ModelForm):
    """
    Форма для создания заказа (доставка)
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order_date'].label = 'Дата получения заказа'
        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['phone'].label = 'Номер телефона'
        self.fields['address'].label = 'Адрес'

    order_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone = forms.CharField(required=True)
    address = forms.CharField(required=True)


    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'buying_type', 'order_date', 'address', 'comment']



class RegistrationForm(forms.ModelForm):

    confirm_password = forms.CharField(widget=forms.PasswordInput)
    password = forms.CharField(widget=forms.PasswordInput)
    phone = forms.CharField(required=False)
    address = forms.CharField(required=False)
    email = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].label = 'Пароль'
        self.fields['confirm_password'].label = 'Подтвердите пароль'
        self.fields['phone'].label = 'Номер телефона'
        self.fields['address'].label = 'Адрес'
        self.fields['email'].label = 'Электронная почта'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['first_name'].label = 'Имя'

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Данный почтовый адрес уже зарегистрирован в системе"
            )
        return email

    def clean(self):
        confirm_password = self.cleaned_data['confirm_password']
        password = self.cleaned_data['password']
        if confirm_password != password:
            raise forms.ValidationError("Пароли не совпадают")
        return self.cleaned_data

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'first_name', 'last_name', 'address', 'phone']


class LoginForm(forms.ModelForm):

    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = 'Почта'
        self.fields['password'].label = 'Пароль'

    def clean(self):
        """
        Этот метод используется для проверки полей электронной почты и пароля в процессе входа в систему.
        """
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        user_qs = User.objects.filter(email=email)
        if not user_qs.exists():
            raise forms.ValidationError(
                f"Пользователь с email {email} не найден в системе"
            )
        else:
            user = user_qs.first()
            if not user.check_password(password):
                raise forms.ValidationError("Неверный пароль")
        return self.cleaned_data


























