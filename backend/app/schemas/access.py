from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MenuBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    code: str = Field(min_length=1, max_length=100)
    parent_id: int | None = None
    sequence: int = 10
    icon: str | None = None
    active: bool = True


class MenuCreate(MenuBase):
    pass


class MenuUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    code: str | None = Field(default=None, min_length=1, max_length=100)
    parent_id: int | None = None
    sequence: int | None = None
    icon: str | None = None
    active: bool | None = None


class MenuRead(MenuBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    role_names: list[str] = []


class PageBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    code: str = Field(min_length=1, max_length=100)
    route: str = Field(min_length=1, max_length=255)
    active: bool = True


class PageCreate(PageBase):
    pass


class PageUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    code: str | None = Field(default=None, min_length=1, max_length=100)
    route: str | None = Field(default=None, min_length=1, max_length=255)
    active: bool | None = None


class PageRead(PageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    role_names: list[str] = []


class ModelAccessBase(BaseModel):
    model: str = Field(min_length=1, max_length=100)
    perm_create: bool = False
    perm_read: bool = False
    perm_write: bool = False
    perm_unlink: bool = False


class ModelAccessUpsert(ModelAccessBase):
    role_name: str = Field(min_length=1, max_length=50)


class ModelAccessRead(ModelAccessBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_id: int
    role_name: str
    created_at: datetime


class ModelAccessSummary(BaseModel):
    model: str
    create: bool = False
    read: bool = False
    write: bool = False
    unlink: bool = False


class Permissions(BaseModel):
    menus: list[MenuRead]
    pages: list[PageRead]
    model_accesses: list[ModelAccessSummary]


class RoleAssignment(BaseModel):
    role_names: list[str] = []
