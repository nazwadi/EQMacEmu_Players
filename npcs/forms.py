from django import forms


class NpcSearchForm(forms.Form):
    npc_name = forms.CharField(required=False, max_length=100)
    min_level = forms.IntegerField(min_value=1, max_value=255, initial=1)
    max_level = forms.IntegerField(min_value=1, max_value=255, initial=99)
    # The max value of query_limit is arbitrary; intended to reduce database load
    query_limit = forms.IntegerField(min_value=0, max_value=200, initial=50)
    select_npc_body_type = forms.ChoiceField(required=False)
    select_expansion = forms.ChoiceField(required=False)
    select_npc_race = forms.ChoiceField(required=False)
    select_npc_class = forms.ChoiceField(required=False)
    exclude_merchants = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        # Pass choices dynamically if they come from the database
        expansions = kwargs.pop('expansions', [])
        npc_body_types = kwargs.pop('npc_body_types', [])
        npc_races = kwargs.pop('npc_races', [])
        npc_classes = kwargs.pop('npc_classes', [])
        super().__init__(*args, **kwargs)

        # self.fields['select_expansion'].choices = [('-1', 'Any')] + expansions
        # self.fields['select_npc_body_type'].choices = [('-1', 'Any')] + npc_body_types
        # self.fields['select_npc_race'].choices = [('-1', 'Any')] + npc_races
        # self.fields['select_npc_class'].choices = [('-1', 'Any')] + npc_classes
        # Convert IDs to strings so they match submitted form values
        self.fields['select_expansion'].choices = [('-1', 'any')] + [
            (str(e['id']), e['exp']) for e in expansions
        ]
        print(self.fields['select_expansion'].choices)
        self.fields['select_npc_body_type'].choices = [('-1', 'any')] + [
            (str(b['id']), b['type']) for b in npc_body_types
        ]
        self.fields['select_npc_race'].choices = [('-1', 'any')] + [
            (str(r['id']), r['race']) for r in npc_races
        ]
        self.fields['select_npc_class'].choices = [('-1', 'any')] + [
            (str(c['id']), c['class']) for c in npc_classes
        ]

    def clean_npc_name(self):
        name = self.cleaned_data.get('npc_name', '')
        return name.replace(' ', '_')

    def clean(self):
        cleaned_data = super().clean()
        min_level = cleaned_data.get('min_level')
        max_level = cleaned_data.get('max_level')

        if min_level and max_level and min_level > max_level:
            cleaned_data['min_level'], cleaned_data['max_level'] = max_level, min_level

        return cleaned_data