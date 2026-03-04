from django import forms

from .models import Article, Publisher


class ArticleForm(forms.ModelForm):
    """
    Form used by journalists to submit or edit articles.
    """

    class Meta:
        model = Article
        fields = ["title", "content", "publisher"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "content": forms.Textarea(
                attrs={"class": "form-control", "rows": 10}
            ),
            "publisher": forms.Select(
                attrs={"class": "form-select"}
            ),
        }


class PublisherForm(forms.ModelForm):
    """
    Editor-only form to create publishers.
    """

    class Meta:
        model = Publisher
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
        }
