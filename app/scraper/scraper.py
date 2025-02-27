# app/scraper/scraper.py

"""
Proporciona herramientas para realizar web scraping utilizando Selenium.

Este módulo contiene la clase `Scraper`, que encapsula la lógica para
inicializar y controlar un navegador Chrome, gestionar las opciones del
navegador y asegurar la correcta liberación de recursos.

"""


import logging
from typing import Optional, Type, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

class ScraperError(Exception):
    """Excepción base para errores específicos del Scraper."""
    pass

class DriverInitializationError(ScraperError):
    """Excepción lanzada cuando falla la inicialización del WebDriver."""
    pass

class DriverShutdownError(ScraperError):
    """Excepción lanzada cuando ocurre un error al cerrar el WebDriver."""
    pass

class Scraper:
    """
    Gestiona la inicialización y el cierre de un navegador Chrome utilizando Selenium.
    
    Emplea el patrón context manager para asegurar la correcta liberación de recursos.
    
    Ejemplo:
        >>> with Scraper(headless=True) as driver:
        ...     driver.get("https://www.example.com")
        ...     # Operaciones de scraping
    """

    def __init__(
        self,
        driver_path: Optional[str] = None,
        headless: bool = False,
        implicit_wait: float = 10.0
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.driver_path = driver_path
        self.headless = headless
        self.implicit_wait = implicit_wait

        self._driver: Optional[webdriver.Chrome] = None
        self._service: Optional[ChromeService] = None

    def _configure_service(self) -> None:
        """
        Configura el servicio de ChromeDriver.
        
        Raises:
            DriverInitializationError: Si ocurre un error al configurar el servicio.
        """
        try:
            if self.driver_path:
                self._service = ChromeService(executable_path=self.driver_path)
            else:
                self._service = ChromeService()
        except WebDriverException as e:
            msg = f"Error al configurar ChromeService: {e}"
            self.logger.error(msg)
            raise DriverInitializationError(msg) from e

    def _configure_options(self) -> Options:
        """
        Configura las opciones para el navegador Chrome.
        
        Returns:
            Options: Objeto de configuración para Chrome.
        """
        options = Options()
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

        if self.headless:
            # Se utiliza la propiedad headless para mayor claridad
            options.headless = True
            options.add_argument("--disable-gpu")

        return options

    def start(self) -> webdriver.Chrome:
        """
        Inicia el navegador Chrome y retorna la instancia del WebDriver.
        
        Returns:
            webdriver.Chrome: Instancia del WebDriver.
        
        Raises:
            DriverInitializationError: Si falla la inicialización del navegador.
        """
        if self._driver:
            self.logger.warning("El navegador ya está iniciado.")
            return self._driver

        try:
            self._configure_service()
            options = self._configure_options()
            self._driver = webdriver.Chrome(service=self._service, options=options)
            self._driver.implicitly_wait(self.implicit_wait)
            self.logger.info("Navegador iniciado con éxito.")
            return self._driver
        except WebDriverException as e:
            msg = f"Error al iniciar el navegador: {e}"
            self.logger.critical(msg)
            self.stop()  # Limpieza en caso de fallo
            raise DriverInitializationError(msg) from e

    def stop(self) -> None:
        """
        Cierra el navegador y libera los recursos asociados.
        
        Raises:
            DriverShutdownError: Si ocurre un error al cerrar el navegador.
        """
        if self._driver:
            try:
                self._driver.quit()
                self.logger.info("Navegador cerrado correctamente.")
            except WebDriverException as e:
                msg = f"Error al cerrar el navegador: {e}"
                self.logger.error(msg)
                raise DriverShutdownError(msg) from e
            finally:
                self._driver = None
                self._service = None

    def __enter__(self) -> webdriver.Chrome:
        """
        Permite el uso del objeto como context manager.
        
        Returns:
            webdriver.Chrome: Instancia del WebDriver.
        """
        return self.start()

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any]
    ) -> bool:
        """
        Cierra el navegador al salir del bloque with.
        
        Args:
            exc_type: Tipo de excepción.
            exc_val: Valor de la excepción.
            exc_tb: Traceback de la excepción.
        
        Returns:
            bool: False para no suprimir excepciones.
        """
        self.stop()
        if exc_type:
            self.logger.error("Excepción en el bloque with", exc_info=(exc_type, exc_val, exc_tb))
        return False  # Propaga la excepción, si ocurrió.

