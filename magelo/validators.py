class PermissionValidator:
    VALID_PERMISSIONS = [
        'inventory',
        'bags',
        'bank',
        'coin_inventory',
        'coin_bank'
    ]

    @classmethod
    def validate_permission_data(cls, data):
        """Validate the permission update data."""
        errors = {}

        # Validate permission field
        permission = data.get('permission')
        if not permission:
            errors['permission'] = 'This field is required.'
        elif permission not in cls.VALID_PERMISSIONS:
            errors['permission'] = f'Invalid permission: {permission}'

        # Validate value field
        value = data.get('value')
        if value is None:
            errors['value'] = 'This field is required.'
        elif not isinstance(value, bool):
            errors['value'] = 'This field must be a boolean.'

        if errors:
            raise ValueError(errors)

        return {
            'permission': permission,
            'value': value
        }