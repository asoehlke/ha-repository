import logging

from .relay import Relay

logging.basicConfig(format='%(asctime)-15s  %(levelname)-8s  %(message)s',
                    level=logging.INFO)

log = logging.getLogger(__name__)

__version__ = '0.1.0'

__all__ = ['Relay']
