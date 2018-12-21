# Return tracebacks with OperationOutcomes when an exceprion occurs
DEBUG = False

# How many items should we include in budles whwn count is not specified
DEFAULT_BUNDLE_SIZE = 20

# Limit bundles to this size even if more are requested
# TODO: Disable limiting when set to 0
MAX_BUNDLE_SIZE = 100

# Path to the models module
MODELS_PATH = "models"

# Which DB backend should be used
# SQLAlchemy | DjangoORM | PyMODM
DB_BACKEND = "SQLAlchemy"
