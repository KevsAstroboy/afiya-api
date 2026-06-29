from utilities.common.exceptions.simple_exception import SimpleException

from core.exceptions.exceptions import ErrorType

from utilities.utilities import Utilities

from core.exceptions.exceptions import BusinessException

from utilities.common.enums.user_type import UserType


class Validator:
    @staticmethod
    def require_non_null(value, field_name):
        """
        Vérifie que la valeur n'est pas None, une chaîne vide ou une liste/dictionnaire vide.
        :param value: La valeur à vérifier.
        :param field_name: Nom du champ pour le message d'erreur.
        :raises ValueError: Si la valeur est invalide.
        :return: La valeur validée.
        """
        if value is None or (isinstance(value, (str, list, dict, set)) and not value):
            raise SimpleException(f"{field_name} is required and cannot be empty", ErrorType.VALIDATION_ERROR)

        return value

    @staticmethod
    async def validate_reference(repo, entity_id: int | None, entity_name: str):
        if not Utilities.is_valid_id(entity_id):
            raise BusinessException(
                f"{entity_name} not found",
                ErrorType.NOT_FOUND
            )

        return await repo.get_by_id(entity_id)

    @staticmethod
    def validate_not_exists(exists_condition: bool, message: str):
        if exists_condition:
            raise BusinessException(message, ErrorType.ALREADY_EXISTS)

    @staticmethod
    def validate_user_type(value: str) -> UserType:
        try:
            return UserType(value)
        except ValueError:
            allowed = ", ".join([e.value for e in UserType])
            raise BusinessException(
                f"Invalid user type. Allowed values: {allowed}",
                ErrorType.NOT_FOUND
            )