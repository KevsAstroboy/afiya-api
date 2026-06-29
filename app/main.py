import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from core.database import DatabaseManager
from core.exceptions.exception_handler import setup_global_exception_handler
from utilities.utils import discover_and_include_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup + shutdown lifecycle
    """
    try:
        await DatabaseManager.create_all_tables()
        logging.info("Database tables created successfully")
    except Exception as e:
        logging.error(f"Error during startup: {e}")

    yield  # application running

    logging.info("Application shutdown")


app = FastAPI(
    title="Telemedecine AI API",
    description="""
API backend pour une plateforme de télémédecine augmentée par IA.

Cette API gère les patients, médecins, consultations et dossiers médicaux,
et intègre un agent d’intelligence artificielle basé sur RAG (Retrieval-Augmented Generation)
afin d’améliorer la qualité des réponses, l’aide à la décision médicale,
et l’assistance conversationnelle.

Elle permet l’interaction sécurisée entre les applications clientes,
les services médicaux, et les modules d’IA.
""",
    version="1.0.0",
    lifespan=lifespan
)


setup_global_exception_handler(app)
discover_and_include_routers(app)
