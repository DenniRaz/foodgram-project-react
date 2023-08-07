from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import webcolors


def validate_HEX_format(value):
    """
    Checks whether the value can be
    interpreted as a hexadecimal color value.
    """

    try:
        webcolors.normalize_hex(value)
    except ValueError:
        raise ValidationError(
            _('The color can only be recorded in HEX format'),
        )
