from fastapi import HTTPException

def check_role(user, allowed_roles):

    user_role = user["role"].upper()

    allowed_roles = [role.upper() for role in allowed_roles]

    if user_role not in allowed_roles:

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )