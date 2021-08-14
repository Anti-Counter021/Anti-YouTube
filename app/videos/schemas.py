from datetime import datetime

from pydantic import BaseModel

from app.auth.schemas import UserPublic
from app.categories.schemas import GetCategory


class VideoBase(BaseModel):
    """ Video base """

    title: str
    description: str


class CreateVideo(VideoBase):
    """ Create video """

    category_id: int


class VideoUpdate(VideoBase):
    """ Update video """

    category_id: int


class GetVideoBase(VideoBase):
    """ Get video base """

    id: int
    video_file: str
    preview_file: str
    created_at: datetime
    views: int


class GetVideoNotUser(GetVideoBase):
    """ Get video """

    category: GetCategory


class GetVideo(GetVideoNotUser):
    """ Get video """

    user: UserPublic