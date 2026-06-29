import logging
from typing import Optional, List
from core.database import DatabaseBackend

from models.user.entity.user_model import User
from models.user.entity.user_entity import UserEntity
from models.user.mapper.user_mapper import UserMapper
from models.user.repository.user_repository import UserRepository
from core.exceptions.exceptions import BusinessException, ErrorType

from models.sexe.entity.sexe_model import Sexe
from models.sexe.entity.sexe_entity import SexeEntity
from models.sexe.mapper.sexe_mapper import SexeMapper
from models.statut.entity.statut_model import Statut
from models.statut.entity.statut_entity import StatutEntity
from models.statut.mapper.statut_mapper import StatutMapper
from models.sexe.repository import SexeRepository
from models.statut.repository import StatutRepository
from utilities.common.validator import Validator
from utilities.utilities import Utilities

from models.dossier_medical.entity.dossier_medical_model import DossierMedical
from services.dossier_medical import DossierMedicalService
from utilities.common.enums.user_type import UserType

from utilities.common.exceptions.invalid_field_exception import InvalidFieldException

logger = logging.getLogger(__name__)




class UserService:
    """Service layer for User business logic"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend
        self.user_repository = backend.get_repository(UserEntity, User, UserMapper)
        self.sexe_repository = backend.get_repository(SexeEntity, Sexe, SexeMapper)
        self.statut_repository = backend.get_repository(StatutEntity, Statut, StatutMapper)
        self.dossier_medical_service = DossierMedicalService(backend)

    async def create(self, domain: User) -> User:
        """Create a new User"""
        # Vérification des dépendances
        Validator.require_non_null(domain.sexe_id, "sexe_id")
        Validator.require_non_null(domain.statut_id, "statut_id")
        Validator.require_non_null(domain.telephone, "telephone")
        try:
            sexe = await Validator.validate_reference(self.sexe_repository, domain.sexe_id, "User sexe")
            statut = await Validator.validate_reference(self.statut_repository, domain.statut_id, "User statut")
            Validator.validate_user_type(domain.type_user)
            if not domain.is_valid_phone_number:
                raise InvalidFieldException("phone number")
            Validator.validate_not_exists(await self.user_repository.exists_by_phone_number(domain.telephone),
                                          "User phone number already exists")
            if not domain.is_valid_email:
                raise InvalidFieldException("email")
            Validator.validate_not_exists(await self.user_repository.exists_by_email(domain.email),
                                          "User email already exists")
            domain.password = Utilities.encrypt_password(domain.telephone)
            domain.is_defalut_password = True
            user_saved = await self.user_repository.create(domain)
            if user_saved.is_patient():
                await self._create_patient_medical_record(user_saved.id)
            return user_saved
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Service error creating User: {e}")
            raise BusinessException(str(e), ErrorType.INTERNAL_SERVER_ERROR)

    async def get_by_id(self, record_id: int) -> Optional[User]:
        """Get User by ID"""
        return await self.user_repository.get_by_id(record_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all User records"""
        return await self.user_repository.get_all(skip=skip, limit=limit)

    async def update(self, record_id: int, updates: dict) -> User:
        """Update User"""
        return await self.user_repository.update(record_id, updates)

    async def delete(self, record_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete User"""
        return await self.user_repository.delete(record_id, deleted_by=deleted_by)

    @staticmethod
    def create_dossier_medical_model(id: int) -> Optional[DossierMedical]:
        return DossierMedical(user_id=id)

    async def _create_patient_medical_record(self, user_id: int):
        dossier_medical = self.create_dossier_medical_model(user_id)
        await self.dossier_medical_service.create(dossier_medical)