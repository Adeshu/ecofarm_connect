from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User, UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label="Email Address *",
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control fw-bold border-primary',
            'placeholder': 'Email (used for login)',
            'autocomplete': 'email'
        })
    )
    phone = forms.CharField(
        label="Phone Number",
        max_length=17,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number'
        })
    )
    first_name = forms.CharField(
        label="First Name",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        label="Last Name",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    state = forms.CharField(
        label="State",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State (optional)'
        })
    )
    district = forms.CharField(
        label="District",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'District (optional)'
        })
    )
    village = forms.CharField(
        label="Village",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Village (optional)'
        })
    )
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password (8+ chars)'
        }),
        help_text="Minimum 8 characters."
    )
    password2 = forms.CharField(
        label="Confirm Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )

    class Meta:
        model = User
        fields = (
            'email', 'phone', 'first_name', 'last_name', 'state', 
            'district', 'village', 'password1', 'password2',
        )
        field_classes = {
            'email': forms.EmailField,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email prominent (login credential)
        self.fields['email'].help_text = "Required. Used as your login email."
        self.fields['phone'].required = True

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email is **required** for login.")
        email = email.lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise ValidationError("Phone number is required.")
        phone = phone.strip()
        if User.objects.filter(phone=phone).exists():
            raise ValidationError("A user with this phone number already exists.")
        return phone

    def save(self, commit=True):
        """🚀 CRITICAL: Auto-set username = email"""
        user = super().save(commit=False)
        # Set username = email (for login)
        user.username = user.email
        user.email = user.email.lower().strip()
        user.first_name = self.cleaned_data['first_name'].strip()
        user.last_name = self.cleaned_data['last_name'].strip()
        
        if commit:
            user.save()
            # Save profile fields to User model (if they exist)
            # Note: These might need to go to UserProfile model
        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-control fw-bold border-primary',
            'placeholder': 'Enter your email address',
            'autofocus': True,
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Email"
        self.fields['username'].help_text = None


class UserProfileForm(forms.ModelForm):
    avatar = forms.ImageField(
        label="Profile Avatar",
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    gender = forms.ChoiceField(
        label="Gender",
        choices=UserProfile.GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = UserProfile
        fields = [
            'avatar',
            'date_of_birth',
            'bio',
            'farming_experience_years',
            'preferred_farming_type',
            'gender',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Tell us about your farming journey...'
            }),
            'farming_experience_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '50'
            }),
            'preferred_farming_type': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].help_text = "Upload profile picture (optional)"


class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control fw-bold',
            'readonly': True  # Prevent email change
        }),
    )
    phone = forms.CharField(
        label="Phone Number",
        max_length=17,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
    )
    first_name = forms.CharField(
        label="First Name",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
    )
    last_name = forms.CharField(
        label="Last Name",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
    )
    state = forms.CharField(
        label="State",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
    )
    district = forms.CharField(
        label="District",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
    )
    village = forms.CharField(
        label="Village",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
    )

    class Meta:
        model = User
        fields = ('email', 'phone', 'first_name', 'last_name', 'state', 'district', 'village')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email read-only (it's login credential)
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['email'].help_text = "Email cannot be changed (used for login)"

    def clean_email(self):
        # Prevent email changes
        return self.instance.email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and User.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This phone number is already in use.")
        return phone
