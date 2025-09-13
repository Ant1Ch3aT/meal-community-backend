from sanic import json
from sanic.blueprints import Blueprint
from sanic_ext import validate

from backend.application.dtos.comment import CreateCommentDTO, GetCommentDTO
from backend.application.exceptions import CommentNotFound
from backend.application.use_cases.create.comment import CreateCommentUseCase
from backend.application.use_cases.get.comment import GetCommentByMealIdUseCase
from backend.application.use_cases.get.user import GetUserByIDUseCase
from backend.domain.entities.comment import Comment
from backend.infrastructure.jwt import require_auth
from backend.infrastructure.sanic import BackendRequest

comment = Blueprint("comment_endpoint", url_prefix="/comment")


@comment.post("/write")
@validate(json=CreateCommentDTO, body_argument="create_comment_dto")
@require_auth
async def write_comment(
    request: BackendRequest,
    user_id: int,
    create_comment_dto: CreateCommentDTO,
):
    user = await GetUserByIDUseCase(request.app.ctx.user_repository).execute(user_id)

    comment_entity = Comment(
        content=create_comment_dto.content,
        author=user,
        parent_id=create_comment_dto.parent_id,
    )

    await CreateCommentUseCase(request.app.ctx.comment_repository).execute(
        user_id=user_id,
        meal_id=create_comment_dto.meal_id,
        comment=comment_entity,
    )

    return json({"message": "Comment created successfully"})


@comment.get("/<meal_id:int>")
@require_auth
async def get_comments_by_meal_id(
    request: BackendRequest,
    _,
    meal_id: int,
):
    try:
        comments = await GetCommentByMealIdUseCase(
            request.app.ctx.comment_repository
        ).execute(meal_id)
    except CommentNotFound:
        return json({"results": []})

    result = [GetCommentDTO.from_entity(comment) for comment in comments]

    return json({"results": [comment.to_dict() for comment in result]})
