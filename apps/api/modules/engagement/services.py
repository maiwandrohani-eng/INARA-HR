"""Employee Engagement Module - Services"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from modules.engagement.repositories import (
    SurveyRepository, SurveyQuestionRepository, SurveyResponseRepository, RecognitionRepository
)
from modules.engagement.schemas import (
    SurveyCreate, SurveyQuestionCreate, SurveyResponseCreate, RecognitionCreate
)


class EngagementService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.survey_repo = SurveyRepository(db)
        self.question_repo = SurveyQuestionRepository(db)
        self.response_repo = SurveyResponseRepository(db)
        self.recognition_repo = RecognitionRepository(db)
    
    async def create_survey(self, survey_data: SurveyCreate, country_code: str = "US") -> dict:
        survey = await self.survey_repo.create(survey_data, country_code)
        await self.db.commit()
        return {"id": str(survey.id), "title": survey.title}
    
    async def get_surveys(self, is_active: Optional[bool] = None) -> List[dict]:
        surveys = await self.survey_repo.get_all(is_active=is_active)
        return [{
            "id": str(s.id),
            "title": s.title,
            "survey_type": s.survey_type,
            "is_active": s.is_active,
            "response_count": s.response_count
        } for s in surveys]
    
    async def create_recognition(self, recognition_data: RecognitionCreate, country_code: str = "US") -> dict:
        recognition = await self.recognition_repo.create(recognition_data, country_code)
        await self.db.commit()
        return {"id": str(recognition.id), "title": recognition.title}
    
    async def get_recognitions(self, employee_id: Optional[uuid.UUID] = None) -> List[dict]:
        recognitions = await self.recognition_repo.get_all(employee_id=employee_id)
        return [{
            "id": str(r.id),
            "employee_id": str(r.employee_id),
            "title": r.title,
            "recognition_type": r.recognition_type,
            "recognition_date": str(r.recognition_date)
        } for r in recognitions]

