from enum import Enum


class UserType(str, Enum):
    MEDECIN = "MEDECIN"
    PATIENT = "PATIENT"