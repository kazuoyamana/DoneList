from .product import *

# local.pyが存在すれば読み込む
try:
    from .local import *
except ImportError:
    pass
