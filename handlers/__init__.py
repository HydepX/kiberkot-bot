from .common import router as common_router
from .shop import router as shop_router
from .support import router as support_router
from .admin_handler import router as admin_router
from .nlu_handler import router as nlu_router
from .fallbacks import router as fallbacks_router


all_routers = [
    common_router,
    shop_router,
    support_router,
    admin_router,
    nlu_router,
    fallbacks_router,
]
