from fastapi import Request, HTTPException, status
from app.models.user import UserRole


def get_current_user(request: Request) -> dict:
    if not hasattr(request.state, "user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return {
        "user_id": request.state.user_id,
        "email": request.state.email,
        "role": request.state.role,
        "jti": request.state.jti,
        "exp": request.state.exp,
    }


class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, request: Request) -> dict:
        user = get_current_user(request)
        if user["role"] not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return user


require_super_admin = RoleChecker([UserRole.SUPER_ADMIN.value])
require_any_role = RoleChecker([UserRole.SUPER_ADMIN.value, UserRole.FRANCHISE.value])
