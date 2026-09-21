"""
用户管理路由模块

- 管理员：用户列表、新建用户、编辑用户、删除用户；
- 普通用户：通过 /profile 维护个人信息、通过 /password 修改密码。
注意：个人信息类路由需声明在 /{user_id} 动态路由之前，避免路径被误匹配。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin
from app.core.id_utils import next_available_id
from app.core.security import md5_encrypt
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    PasswordUpdate,
    UserCreate,
    UserProfileUpdate,
    UserResponse,
    UserUpdate,
)


def _normalize(value: str | None) -> str | None:
    """把空字符串规范化为 None，避免多个空值触发数据库唯一索引冲突。"""
    if value is None:
        return None
    value = value.strip()
    return value or None


def _check_unique_contact(
    db: Session, email: str | None, phone: str | None, exclude_id: int | None = None
) -> None:
    """
    校验邮箱与手机号的全局唯一性。

    :param db: 数据库会话
    :param email: 邮箱（可为空）
    :param phone: 手机号（可为空）
    :param exclude_id: 编辑时排除自身ID，避免与自己冲突
    :raises HTTPException 400: 邮箱或手机号已被使用
    """
    conditions = []
    if email is not None:
        conditions.append(User.email == email)
    if phone is not None:
        conditions.append(User.phone == phone)

    if not conditions:
        return

    stmt = select(User).where(or_(*conditions))
    if exclude_id is not None:
        stmt = stmt.where(User.id != exclude_id)

    conflict = db.scalar(stmt)
    if conflict is None:
        return

    if email is not None and conflict.email == email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="该邮箱已被使用"
        )
    if phone is not None and conflict.phone == phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="该手机号已被使用"
        )

# 用户路由，统一前缀 /api/users
router = APIRouter(prefix="/api/users", tags=["用户管理"])


# --------------------------------------------------------------------------
# 以下为登录用户本人可用的接口（个人主页）
# --------------------------------------------------------------------------

@router.put("/profile", response_model=UserResponse, summary="编辑个人信息")
def update_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    修改当前登录用户自己的基础信息（姓名、邮箱、手机号）。

    :param payload: 待更新的个人信息
    :param db: 数据库会话
    :param current_user: 当前登录用户
    :return: 更新后的用户信息
    """
    # 仅更新调用方实际传入的非空字段
    if payload.real_name is not None:
        current_user.real_name = payload.real_name.strip() or None

    email = _normalize(payload.email)
    phone = _normalize(payload.phone)
    # 邮箱/手机号变更时校验全局唯一性（排除自身）
    if email != current_user.email or phone != current_user.phone:
        _check_unique_contact(db, email, phone, exclude_id=current_user.id)
    current_user.email = email
    current_user.phone = phone

    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/password", summary="修改密码")
def update_password(
    payload: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    修改当前登录用户的登录密码。

    :param payload: 原密码与新密码
    :param db: 数据库会话
    :param current_user: 当前登录用户
    :return: 操作结果提示
    :raises HTTPException 400: 原密码不正确
    """
    # 校验原密码
    if current_user.password != md5_encrypt(payload.old_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="原密码不正确"
        )

    # 更新为新密码的 MD5 值
    current_user.password = md5_encrypt(payload.new_password)
    db.commit()
    return {"message": "密码修改成功"}


# --------------------------------------------------------------------------
# 以下为管理员专属接口
# --------------------------------------------------------------------------

@router.get(
    "",
    response_model=list[UserResponse],
    summary="用户列表（管理员）",
    dependencies=[Depends(require_admin)],
)
def list_users(keyword: str | None = None, db: Session = Depends(get_db)):
    """
    查询全部用户，支持按用户名或真实姓名模糊搜索。

    :param keyword: 搜索关键词
    :param db: 数据库会话
    :return: 用户列表
    """
    stmt = select(User).order_by(User.id)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(
            or_(User.username.like(like), User.real_name.like(like))
        )
    return db.scalars(stmt).all()


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="新建用户（管理员）",
    dependencies=[Depends(require_admin)],
)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """
    创建新用户。

    :param payload: 用户信息
    :param db: 数据库会话
    :return: 新建的用户信息
    :raises HTTPException 400: 用户名已存在
    """
    # 用户名唯一性校验
    exists = db.scalar(select(User).where(User.username == payload.username))
    if exists is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在"
        )

    # 邮箱与手机号全局唯一校验（空字符串统一按 None 处理）
    email = _normalize(payload.email)
    phone = _normalize(payload.phone)
    _check_unique_contact(db, email, phone)

    # 创建用户，密码做 MD5 加密；ID 取最小可用值，删除后可自动填补空缺
    user = User(
        id=next_available_id(db, User),
        username=payload.username,
        password=md5_encrypt(payload.password),
        real_name=payload.real_name.strip() if payload.real_name else None,
        email=email,
        phone=phone,
        role=payload.role,
        status=payload.status,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="编辑用户（管理员）",
    dependencies=[Depends(require_admin)],
)
def update_user(
    user_id: int, payload: UserUpdate, db: Session = Depends(get_db)
):
    """
    修改指定用户的信息（角色、状态、基础资料）。

    :param user_id: 待修改的用户ID
    :param payload: 待更新字段
    :param db: 数据库会话
    :return: 更新后的用户信息
    :raises HTTPException 404: 用户不存在
    """
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
        )

    # 逐字段更新非空值
    for field in ("role", "status"):
        value = getattr(payload, field)
        if value is not None:
            setattr(user, field, value)

    if payload.real_name is not None:
        user.real_name = payload.real_name.strip() or None

    # 邮箱与手机号变更时校验全局唯一性（排除被编辑用户自身）
    email = _normalize(payload.email)
    phone = _normalize(payload.phone)
    if email != user.email or phone != user.phone:
        _check_unique_contact(db, email, phone, exclude_id=user.id)
    user.email = email
    user.phone = phone

    db.commit()
    db.refresh(user)
    return user


@router.delete(
    "/{user_id}",
    summary="删除用户（管理员）",
    dependencies=[Depends(require_admin)],
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除指定用户（不允许删除自己）。

    :param user_id: 待删除的用户ID
    :param db: 数据库会话
    :param current_user: 当前登录的管理员
    :return: 操作结果提示
    :raises HTTPException 400/404: 删除自己 / 用户不存在
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="不能删除当前登录账号"
        )

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
        )

    db.delete(user)
    db.commit()
    return {"message": "删除成功"}
