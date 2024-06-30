def calc_buff_duration(level, formula, duration):
    """Calculates the buffer duration of a spell based on a level and formula"""
    def apply_duration(i):
        return min(max(i, 1), duration) if i < duration else duration

    if formula >= 200:
        return formula

    match formula:
        case 0:  # not a buff
            return 0
        case 1:
            i = level // 2
            return apply_duration(i)
        case 2:
            i = 6 if level <= 1 else level // 2 + 5
            return apply_duration(i)
        case 3:
            i = level * 30
            return apply_duration(i)
        case 4:
            i = 50
            return i if duration == 0 else min(i, duration)
        case 5:
            i = 2
            return i if duration == 0 else min(i, duration)
        case 6:
            i = level // 2 + 2
            return i if duration == 0 else min(i, duration)
        case 7:
            i = level
            return i if duration == 0 else min(i, duration)
        case 8:
            i = level + 10
            return apply_duration(i)
        case 9:
            i = level * 2 + 10
            return apply_duration(i)
        case 10:
            i = level * 3 + 10
            return apply_duration(i)
        case 11:
            i = level * 30 + 90
            return apply_duration(i)
        case 12:  # not used by any spells
            i = level // 4
            i = max(i, 1)
            return i if duration == 0 else min(i, duration)
        case 50:  # permanent buff
            return 65534
        case _:
            return 0
