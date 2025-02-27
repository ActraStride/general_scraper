# app/scraper/__init__.py
"""
El paquete `scraper` proporciona herramientas para realizar web scraping.

Este paquete expone la clase `Scraper` para la interacción con Selenium.

Example:
    >>> from app.scraper import Scraper
    >>> with Scraper() as driver:
    ...    # Realizar web scraping con driver

"""

from .scraper import Scraper

__all__ = ["Scraper"]