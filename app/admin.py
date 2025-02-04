from django.contrib import admin
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from polygons.models import Polygon, User, PolygonToUser


class UserM2MInline(admin.StackedInline):
    model = User.polygons.through
    extra = 0


class PolygonM2MInline(admin.StackedInline):
    model = Polygon.users.through
    fk_name = "user"
    extra = 0


class PolygonAdmin(admin.ModelAdmin):
    list_filter = ["name", "antimeridian_crossing", 'created']
    inlines = [
        UserM2MInline,
    ]


class PolygonToUserAdmin(admin.ModelAdmin):
    list_filter = ["by_user", 'created']
    pass


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    usable_password = None

    class Meta:
        model = User
        fields = ["username"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ["username", "password", "is_staff", "is_superuser"]


class UserAdmin(BaseUserAdmin):
    inlines = [
        PolygonM2MInline,
    ]
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ["username", "is_staff", "is_superuser", 'created']
    list_filter = ["is_staff", "is_superuser", 'created']
    fieldsets = [
        (None, {"fields": ["username", "password"]}),
        ("Permissions", {"fields": ["is_staff", "is_superuser"]}),
    ]

    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["username", "password"],
            },
        ),
    ]
    search_fields = ["username"]
    ordering = ["username"]
    filter_horizontal = []


admin.site.register(Polygon, PolygonAdmin)
admin.site.register(PolygonToUser, PolygonToUserAdmin)

admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
