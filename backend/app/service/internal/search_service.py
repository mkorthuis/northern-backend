from typing import TypeVar, Generic, Type, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel

T = TypeVar('T')

class GenericSearchService(Generic[T]):
    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    def build_base_query(self, params: BaseModel):
        query = self.session.query(self.model)
        
        if hasattr(params, 'query') and params.query:
            query = query.filter(
                or_(
                    getattr(self.model, 'title').ilike(f"%{params.query}%"),
                    getattr(self.model, 'description').ilike(f"%{params.query}%")
                )
            )
        
        if hasattr(params, 'filters') and params.filters:
            for field, value in params.filters.dict().items():
                if value is not None:
                    query = query.filter(getattr(self.model, field) == value)
        
        return query

    def apply_sorting(self, query, params: BaseModel):
        if hasattr(params, 'sort_by') and hasattr(params, 'sort_order'):
            sort_column = getattr(self.model, params.sort_by.value)
            if params.sort_order == 'desc':
                return query.order_by(sort_column.desc())
            return query.order_by(sort_column.asc())
        return query

    def execute_search(self, params: BaseModel) -> Dict[str, Any]:
        query = self.build_base_query(params)
        total_count = query.count()
        query = self.apply_sorting(query, params)
        
        if hasattr(params, 'page') and hasattr(params, 'page_size'):
            offset = (params.page - 1) * params.page_size
            query = query.offset(offset).limit(params.page_size)
        
        results = query.all()
        total_pages = (total_count + params.page_size - 1) // params.page_size
        
        return {
            "items": results,
            "total": total_count,
            "page": params.page,
            "page_size": params.page_size,
            "total_pages": total_pages
        }