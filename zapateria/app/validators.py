# app/validators.py
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class MinimumLengthValidator:
    def __init__(self, min_length=16):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("La contraseña debe tener al menos %(min_length)d caracteres."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return _(
            "Tu contraseña debe contener al menos %(min_length)d caracteres."
            % {'min_length': self.min_length}
        )

class UppercaseValidator:
    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            raise ValidationError(
                _("La contraseña debe contener al menos 1 letra mayúscula."),
                code='password_no_upper',
            )

    def get_help_text(self):
        return _("Tu contraseña debe contener al menos 1 letra mayúscula.")

class DigitValidator:
    def validate(self, password, user=None):
        if not re.findall(r'\d', password):
            raise ValidationError(
                _("La contraseña debe contener al menos 1 dígito."),
                code='password_no_digit',
            )

    def get_help_text(self):
        return _("Tu contraseña debe contener al menos 1 dígito.")

class SymbolValidator:
    def validate(self, password, user=None):
        if not re.findall('[^A-Za-z0-9]', password):
            raise ValidationError(
                _("La contraseña debe contener al menos 1 símbolo especial."),
                code='password_no_symbol',
            )

    def get_help_text(self):
        return _("Tu contraseña debe contener al menos 1 símbolo especial (@, #, $, %, etc.).")