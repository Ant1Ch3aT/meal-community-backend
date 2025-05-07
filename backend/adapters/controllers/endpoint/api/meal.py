from sanic import json
from sanic.blueprints import Blueprint
from sanic_ext import validate

from backend.application.dtos.meal import MealDTO
from backend.application.use_cases.get.meal import GetDailyMealUseCase
from backend.application.use_cases.get.user import GetUserByIDUseCase
from backend.infrastructure.jwt import require_auth
from backend.infrastructure.sanic import BackendRequest

meal = Blueprint("meal_endpoint", url_prefix="/meal")


@meal.post("/daily")
@validate(json=MealDTO, body_argument="meal_dto")
@require_auth
async def get_daily_meal(request: BackendRequest, user_id: str, meal_dto: MealDTO):
    user = await GetUserByIDUseCase(request.app.ctx.user_repository).execute(
        int(user_id)
    )

    results = await GetDailyMealUseCase(request.app.ctx.meal_repository).execute(
        user.school_info.edu_office_code,
        user.school_info.standard_school_code,
        meal_dto.date,
    )

    return json(
        {
            "results": [result.to_dict() for result in results],
        }
    )
