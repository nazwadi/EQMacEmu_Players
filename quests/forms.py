from django import forms
from quests.models import EXPANSION_INTRODUCED_CHOICES, PLAYER_CLASS_RESTRICTION_CHOICES, PLAYER_RACE_RESTRICTION_CHOICES


class QuestSearchForm(forms.Form):
    quest_name = forms.CharField(required=False, max_length=100)
    starting_zone = forms.CharField(required=False, max_length=100)
    min_level = forms.IntegerField(min_value=1, max_value=60, initial=1, required=False)
    max_level = forms.IntegerField(min_value=1, max_value=60, initial=60, required=False)
    expansion = forms.ChoiceField(required=False)
    player_class = forms.ChoiceField(required=False)
    player_race = forms.ChoiceField(required=False)
    query_limit = forms.IntegerField(min_value=0, max_value=200, initial=50, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['expansion'].choices = [('-1', 'Any')] + [
            (str(k), v) for k, v in EXPANSION_INTRODUCED_CHOICES.items()
        ]
        self.fields['player_class'].choices = [('-1', 'Any')] + [
            (str(k), v) for k, v in PLAYER_CLASS_RESTRICTION_CHOICES.items() if k > 0
        ]
        self.fields['player_race'].choices = [('-1', 'Any')] + [
            (str(k), v) for k, v in PLAYER_RACE_RESTRICTION_CHOICES.items() if k > 0
        ]

    def clean(self):
        cleaned_data = super().clean()
        min_level = cleaned_data.get('min_level')
        max_level = cleaned_data.get('max_level')

        if min_level and max_level and min_level > max_level:
            cleaned_data['min_level'], cleaned_data['max_level'] = max_level, min_level

        return cleaned_data
