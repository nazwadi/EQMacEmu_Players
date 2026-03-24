import json
from datetime import date

from django import forms

from dkp.models import RaidCircuit

from .models import RAID_TZ_CHOICES, RaidEvent, RaidTarget


class RaidEventForm(forms.ModelForm):
    # Targets handled manually via JS picker; hidden inputs named "targets"
    # submitted as a list — validated in the view, not here.

    circuit_name = forms.CharField(
        required=False,
        max_length=100,
        label='Circuit name (write-in)',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter circuit name if not listed above…',
            'id': 'id_circuit_name',
        }),
        help_text='Used only when your circuit is not in the dropdown.',
    )
    warnings_acknowledged = forms.BooleanField(
        required=False,
        label='I understand the scheduling conflict and wish to proceed',
        widget=forms.CheckboxInput(attrs={'id': 'id_warnings_acknowledged'}),
    )

    class Meta:
        model = RaidEvent
        fields = ['title', 'date', 'start_time', 'timezone', 'circuit', 'circuit_name', 'is_public', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. "Tuesday NToV Progression"'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'step': '900'}),
            'timezone': forms.Select(attrs={'id': 'id_timezone', 'class': 'rsf-input'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional notes for attendees…'}),
            'is_public': forms.CheckboxInput(attrs={'id': 'id_is_public'}),
        }
        labels = {
            'timezone': 'Time Zone',
            'is_public': 'Public raid (visible on the public board)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['circuit'].queryset = RaidCircuit.objects.filter(is_active=True).order_by('name')
        self.fields['circuit'].required = False
        self.fields['circuit'].empty_label = '— Select a circuit —'
        if not self.data and not self.instance.pk:
            self.fields['date'].initial = date.today()

    def clean(self):
        cleaned = super().clean()
        circuit = cleaned.get('circuit')
        circuit_name = cleaned.get('circuit_name', '').strip()
        if not circuit and not circuit_name:
            raise forms.ValidationError(
                'Please select a circuit from the list or enter a circuit name.'
            )
        return cleaned

    @staticmethod
    def targets_json():
        """Serialised target list for the JS picker, grouped by expansion."""
        EXPANSION_ORDER = {'Luclin': 0, 'Velious': 1, 'Kunark': 2, 'Classic': 3, 'PoP': 4}
        targets = list(RaidTarget.objects.filter(is_active=True).values('id', 'name', 'description'))
        for t in targets:
            expansion = t['description'].split(' \u2014 ')[0] if ' \u2014 ' in t['description'] else 'Other'
            t['expansion'] = expansion
            t['_order'] = (EXPANSION_ORDER.get(expansion, 99), t['name'])
        targets.sort(key=lambda t: t['_order'])
        for t in targets:
            del t['_order']
        return json.dumps(targets)
