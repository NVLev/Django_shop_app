from django import forms
from django.contrib.auth.models import Group
from django.core import validators
from django.forms import ModelForm

from .models import Order, Product


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ("name",)


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "name", "price", "description", "discount", "preview"

    images = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={"class": "form-control", "accept": "image/*"}),
    )

    def clean_images(self):
        """
        Проверка изображений
        """
        images = self.files.getlist("images")
        for image in images:
            if not image.content_type.startswith("image"):
                raise forms.ValidationError("File is not an image")
        return images


class OrderForm(forms.ModelForm):
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    class Meta:
        model = Order
        fields = "delivery_address", "promocode", "products"


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()


class CSVImportForm(forms.Form):
    csv_file = forms.FileField()
