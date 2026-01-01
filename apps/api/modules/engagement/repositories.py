"""Employee Engagement Module - Repositories"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional
from datetime import datetime
import uuid

from modules.engagement.models import Survey, SurveyQuestion, SurveyResponse, Recognition
from modules.engagement.schemas import SurveyCreate, SurveyQuestionCreate, SurveyResponseCreate, RecognitionCreate


class SurveyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, survey_data: SurveyCreate, country_code: str) -> Survey:
        survey = Survey(**survey_data.model_dump(), country_code=country_code)
        self.db.add(survey)
        await self.db.flush()
        return survey
    
    async def get_all(self, is_active: Optional[bool] = None) -> List[Survey]:
        query = select(Survey).where(Survey.is_deleted == False)
        if is_active is not None:
            query = query.where(Survey.is_active == is_active)
        result = await self.db.execute(query)
        return list(result.scalars().all())


class SurveyQuestionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, question_data: SurveyQuestionCreate, country_code: str) -> SurveyQuestion:
        question = SurveyQuestion(**question_data.model_dump(), country_code=country_code)
        self.db.add(question)
        await self.db.flush()
        return question


class SurveyResponseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, response_data: SurveyResponseCreate, country_code: str) -> SurveyResponse:
        response_dict = response_data.model_dump()
        response_dict["submitted_date"] = datetime.utcnow()
        response_dict["country_code"] = country_code
        response = SurveyResponse(**response_dict)
        self.db.add(response)
        
        # Update survey response count
        survey = await self.db.get(Survey, response_data.survey_id)
        if survey:
            survey.response_count += 1
        
        await self.db.flush()
        return response


class RecognitionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, recognition_data: RecognitionCreate, country_code: str) -> Recognition:
        recognition = Recognition(**recognition_data.model_dump(), country_code=country_code)
        self.db.add(recognition)
        await self.db.flush()
        return recognition
    
    async def get_all(self, employee_id: Optional[uuid.UUID] = None) -> List[Recognition]:
        query = select(Recognition).where(Recognition.is_deleted == False)
        if employee_id:
            query = query.where(Recognition.employee_id == employee_id)
        query = query.order_by(Recognition.recognition_date.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

