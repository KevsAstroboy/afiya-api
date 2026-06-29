import os
import importlib
import logging
from typing import Any


def discover_and_include_routers(app: Any) -> None:
    """
    Découvre et inclut automatiquement tous les routeurs dans le projet.

    Cette méthode parcourt le répertoire des adaptateurs core et inclut dynamiquement
    tous les routeurs trouvés dans l'application FastAPI.

    :param app: Instance de l'application FastAPI
    """
    logger = logging.getLogger(__name__)
    base_path = os.path.relpath(os.path.join(os.path.dirname(__file__), '..', 'controllers', 'api'))
    included_routers = []
    skipped_routers = []

    try:
        # Parcourir tous les sous-dossiers des adaptateurs core
        for entity_name in os.listdir(base_path):
            entity_path = os.path.join(base_path, entity_name, 'controller')

            # Vérifier si le dossier controller existe
            if os.path.isdir(entity_path):
                controller_file = f'{entity_name}_controller.py'
                full_controller_path = os.path.join(entity_path, controller_file)

                # Vérifier si le fichier de contrôleur existe
                if os.path.exists(full_controller_path):
                    try:
                        # Importer dynamiquement le module
                        module_name = f'controllers.api.{entity_name}.controller.{entity_name}_controller'
                        module = importlib.import_module(module_name)

                        # Chercher un attribut qui se termine par '_router'
                        routers_added = False
                        for attr_name in dir(module):
                            if attr_name.endswith('_router'):
                                router = getattr(module, attr_name)
                                app.include_router(router)
                                included_routers.append(attr_name)
                                routers_added = True
                                logger.info(f"Included router: {attr_name}")

                        if not routers_added:
                            skipped_routers.append(entity_name)
                            logger.warning(f"No routers found in {module_name}")

                    except ImportError as e:
                        logger.error(f"Could not import router for {entity_name}: {e}")
                        skipped_routers.append(entity_name)

        # Logging summary
        logger.info(f"Router Discovery Summary:")
        logger.info(f"Total Routers Included: {len(included_routers)}")
        logger.info(f"Included Routers: {', '.join(included_routers) or 'None'}")
        logger.info(f"Skipped Entities: {', '.join(skipped_routers) or 'None'}")

    except Exception as e:
        logger.critical(f"Unexpected error during router discovery: {e}", exc_info=True)
