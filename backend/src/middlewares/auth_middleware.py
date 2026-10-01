from jose import JWTError, jwt

from src.config.settings import JWT_ALGORITHM, JWT_SECRET, LOCAL_USERS

# 只读演示：不登录也给默认身份；带了 Authorization Bearer 就解 JWT，
# 带 x-user-id / x-role 头则切换本地演示账号，方便评审多角色冲突。
DEFAULT_USER = {"id": 3, "name": "郑主管", "role": "SUPERVISOR"}


async def auth_middleware(request, call_next):
    user = dict(DEFAULT_USER)
    authorization = request.headers.get("authorization", "")
    if authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user = {"id": payload.get("uid"), "name": payload.get("name", ""), "role": payload.get("role")}
        except JWTError:
            user = dict(DEFAULT_USER)
    elif request.headers.get("x-user-id"):
        try:
            local = LOCAL_USERS.get(int(request.headers["x-user-id"]))
            if local:
                user = dict(local)
        except ValueError:
            pass

    request.state.user = user
    response = await call_next(request)
    response.headers["x-actor-role"] = str(user["role"])
    return response
