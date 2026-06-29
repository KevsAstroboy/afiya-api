import base64
import hashlib
import os
from typing import Optional, List


class Utilities:
    @staticmethod
    def not_blank(value) -> bool:
        return value is not None and (not isinstance(value, str) or value.strip())


    @staticmethod
    def is_blank(value) -> bool:
        return value is None or (isinstance(value, str) and not value.strip())


    @staticmethod
    def is_not_empty(lst: Optional[List]) -> bool:
        """
        Vérifie si une liste n'est pas vide.

        :param lst: Liste à vérifier (peut être None)
        :return: True si la liste contient au moins un élément, False sinon.
        """
        return bool(lst) and len(lst) > 0

    @staticmethod
    def is_valid_id(value: int | None) -> bool:
        return isinstance(value, int) and value > 0

    @staticmethod
    def generate_salt(length=16):
        """Génère un sel aléatoire"""
        return os.urandom(length)

    @staticmethod
    def encrypt_password(password: str) -> str:
        """
        Crypte un mot de passe en utilisant SHA-256 avec un sel

        Args:
            password: Le mot de passe en clair

        Returns:
            str: Une chaîne unique combinant le hash et le sel, séparés par un point
        """
        # Génère un nouveau sel
        salt = Utilities.generate_salt()

        # Convertit le mot de passe en bytes s'il ne l'est pas déjà
        if isinstance(password, str):
            password = password.encode('utf-8')

        # Combine le sel et le mot de passe
        salted_password = salt + password

        # Utilise SHA-256 pour le hachage
        hashed = hashlib.sha256(salted_password).digest()

        # Encode en base64
        hashed_b64 = base64.b64encode(hashed).decode('utf-8')
        salt_b64 = base64.b64encode(salt).decode('utf-8')

        # Combine le hash et le sel en une seule chaîne
        return f"{hashed_b64}.{salt_b64}"

    @staticmethod
    def verify_password(password: str, encrypted: str) -> bool:
        """
        Vérifie si un mot de passe correspond au hash stocké

        Args:
            password: Le mot de passe à vérifier
            encrypted: La chaîne cryptée (format: "hash.salt")

        Returns:
            bool: True si le mot de passe correspond, False sinon
        """
        try:
            # Sépare le hash et le sel
            hashed_b64, salt_b64 = encrypted.split('.')

            # Décode le sel
            salt = base64.b64decode(salt_b64)

            # Convertit le mot de passe en bytes
            if isinstance(password, str):
                password = password.encode('utf-8')

            # Recalcule le hash avec le même sel
            salted_password = salt + password
            new_hash = hashlib.sha256(salted_password).digest()
            new_hash_b64 = base64.b64encode(new_hash).decode('utf-8')

            return new_hash_b64 == hashed_b64
        except:
            return False