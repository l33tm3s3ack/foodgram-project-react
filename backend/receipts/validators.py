import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_hex(value):
    match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', value)
    if not match:
        raise ValidationError(
            _('%(value)s is not an HEX code'),
            params={'value': value},
        )
