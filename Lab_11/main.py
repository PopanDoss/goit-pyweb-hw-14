from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from typing import Callable

import re

from ipaddress import ip_address

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from routes.contacts import router as contact_router
from routes.users import router as users_router

from settings import limiter, user_agent_ban_list

origins = [ 
    "http://localhost:3000"
    ]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# banned_ips = []

# @app.middleware("http")
# async def ban_ips(request: Request, call_next: Callable):
#     """
#     Middleware to ban specific IP addresses.
#     """
#     ip = ip_address(request.client.host)
#     if ip in banned_ips:
#         return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"})
#     response = await call_next(request)
#     return response


# user_agent_ban_list = []

# @app.middleware("http")
# async def user_agent_ban_middleware(request: Request, call_next: Callable):
#     """
#     Middleware to ban requests based on user-agent header.
#     """
#     user_agent = request.headers.get("user-agent")
#     for ban_pattern in user_agent_ban_list:
#         if re.search(ban_pattern, user_agent):
#             return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"})
#     response = await call_next(request)
#     return response

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(contact_router, prefix='/api')
app.include_router(users_router, prefix='/api')

@app.get("/")
def read_root():
    """
    Root endpoint to test API availability.
    """
    return {"message": "Hello World"}