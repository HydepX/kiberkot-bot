from .common import router as common_router
from .shop import router as shop_router
from .support import router as support_router
from .fallbacks import router as fallbacks_router


all_routers = [
    common_router,
    shop_router,
    support_router,
    fallbacks_router,
]
