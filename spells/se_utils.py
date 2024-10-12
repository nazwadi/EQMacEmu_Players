"""
se_utils.py - utility functions for spell effects
"""
def describe_se_ac(spell_effect: str, min_value: int, max_value: int, min_level: int, max_level: int) -> str:
    """
    Builds a spell effect description for spells with an AC spell effect

    :param spell_effect:
    :param min_value:
    :param max_value:
    :param min_level:
    :param max_level:
    :return:
    """
    description = f"{'Decrease' if max_value < 0 else 'Increase'} {spell_effect}"

    # Cloth casters have different rules than everybody else for AC buffs
    cloth_min = int(int(min_value / 3) * 1000 / 847)
    cloth_max = int(int(max_value / 3) * 1000 / 847)
    all_min = int(int(min_value / 4) * 1000 / 847)
    all_max = int(int(max_value / 4) * 1000 / 847)

    if min_value != max_value:
        if cloth_min != cloth_max:
            description += f" for Cloth Casters by {cloth_min} (L{min_level}) to {cloth_max} (L{max_level}),"
        else:
            description += f" for Cloth Casters by {cloth_max},"
        if all_min != all_max:
            description += f" Everyone else by {all_min} (L{min_level}) to {all_max} (L{max_level})"
        else:
            description += f" Everyone else by {all_max}"
    else:
        if max_value < 0:
            max_value = -max_value
        description += f" for Cloth Casters by {cloth_max}, Everyone else by {all_max}"
    return description
