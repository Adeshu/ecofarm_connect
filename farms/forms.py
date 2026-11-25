from django import forms
from .models import Farm, Crop, FarmActivity

class FarmForm(forms.ModelForm):
    class Meta:
        model = Farm
        fields = ['name', 'location', 'area_acres', 'farm_type', 'description', 'established_date', 'latitude', 'longitude']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'area_acres': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'farm_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'established_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001'}),
        }

class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['name', 'variety', 'planted_date', 'expected_harvest_date','actual_harvest_date', 'status', 'area_planted', 'expected_yield','actual_yield', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'variety': forms.TextInput(attrs={'class': 'form-control'}),
            'planted_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_harvest_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'actual_harvest_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'area_planted': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'expected_yield': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'actual_yield': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class FarmActivityForm(forms.ModelForm):
    class Meta:
        model = FarmActivity
        fields = ['activity_type', 'description', 'date_performed', 'cost', 'crop', 'notes']
        widgets = {
            'activity_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_performed': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'crop': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        farm = kwargs.pop('farm', None)
        super().__init__(*args, **kwargs)
        if farm:
            self.fields['crop'].queryset = Crop.objects.filter(farm=farm)
