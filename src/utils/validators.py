# -*- coding: utf-8 -*-

__author__ = "Hagata"
__version__ = "0.0.1"
__date__ = "2025/1/3 (Created: 2025/1/3)"

import re

from prompt_toolkit.validation import ValidationError, Validator

from src.enums import NotificationFormat


class UsernameValidator(Validator):
    """UsernameValidator

    UsernameValidator is a prompt_toolkit Validator that validates the username input
    """
    def validate(self, document) -> None:
        """Validate the username input

        Args:
            document (Document): The input document

        Raises:
            ValidationError: The username is empty or contains non-alphanumeric characters
        """
        if not document.text: # 入力が空の場合
            raise ValidationError(message="Username cannot be empty", cursor_position=len(document.text))
        if not re.match(r"^[a-zA-Z0-9_]+$", document.text): # 英数字とアンダースコア以外が含まれている場合
            raise ValidationError(message="Username must be alphanumeric", cursor_position=len(document.text))

class FormatValidator(Validator):
    """FormatValidator

    FormatValidator is a prompt_toolkit Validator that validates the format input
    """
    def validate(self, document) -> None:
        """Validate the format input

        Args:
            document (Document): The input document(display format)

        Raises:
            ValidationError: The format is invalid. Not Notification or Dialog
        """
        valid_formats = [fmt.value for fmt in NotificationFormat.__members__.values()]
        if document.text not in valid_formats:
            raise ValidationError(
                message="Invalid notification method. Valid options are: Notification, Dialog",
                cursor_position=len(document.text)
            )
