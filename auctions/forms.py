import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Bid, Comment, Listing

User = get_user_model()


class ListingForm(forms.ModelForm):
    CATEGORY_CHOICES = [
        # ('value', 'display_name')
        ("Fashion", "Fashion"),
        ("Toys", "Toys"),
        ("Electronics", "Electronics"),
        ("Home", "Home"),
        ("Books", "Books"),
        ("Other", "Other"),
    ]
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, widget=forms.Select)

    class Meta:
        model = Listing
        fields = ["title", "description", "starting_bid", "image", "category"]
        error_messages = {
            "image": {
                "invalid": "Please enter a valid URL (https//).",
            }
        }

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if title == "":
            raise forms.ValidationError("Title cannot be empty.")
        if Listing.objects.filter(title=title).exists():
            raise forms.ValidationError("This title is already taken.")
        return title

    def clean_description(self):
        description = self.cleaned_data.get("description")
        if description == "":
            raise forms.ValidationError("Description cannot be empty.")
        return description

    def clean_starting_bid(self):
        starting_bid = self.cleaned_data.get("starting_bid")
        if starting_bid is None:
            raise forms.ValidationError("Starting bid cannot be empty.")
        if starting_bid < 0:
            raise forms.ValidationError("Starting bid must be positive.")
        return starting_bid

    def clean_image(self):
        url = self.cleaned_data.get("image")
        if url:
            url_pattern = (
                r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\."
                r"[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
            )
            if not re.match(url_pattern, url):
                raise ValidationError("Invalid URL format.")
        return url


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["amount"]

    def clean_amount(self):
        bid_value = self.cleaned_data.get("amount")
        if bid_value is None:
            raise forms.ValidationError("The bid value cannot be empty.")
        if bid_value <= 0:
            raise forms.ValidationError("The bid must be greater than 0.")
        return bid_value


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirmation = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already taken.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmation = cleaned_data.get("confirmation")
        if password and confirmation and password != confirmation:
            raise forms.ValidationError("Passwords must match.")
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                self.add_error("password", e)
        return cleaned_data

    def save(self):
        return User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
        )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Share your thoughts about this auction...",
                    "maxlength": "500",
                    "style": "resize: none;",
                    "aria-label": "Comment text",
                }
            ),
        }
        labels = {
            "text": "Add a comment:",
        }

    def clean_text(self):
        text = self.cleaned_data.get("text", "").strip()
        if not text:
            raise forms.ValidationError("Comment cannot be empty.")
        return text
