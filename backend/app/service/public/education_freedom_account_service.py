from typing import List, Optional
from sqlmodel import Session, select, func
from fastapi import HTTPException

from app.model.education_freedom_account import (
    EducationFreedomAccountEntryType,
    EducationFreedomAccountEntryTypeValue,
    EducationFreedomAccountEntry
)
from app.model.location import Town, TownDistrictLink
from app.schema.education_freedom_account_schema import (
    EducationFreedomAccountEntryGet,
    EFAEntryTypeGet
)

class EducationFreedomAccountService:
    def get_entry_types_with_values(self, session: Session, year: Optional[int] = None) -> List[EFAEntryTypeGet]:
        """
        Get all education freedom account entry types with their values.
        If year is provided, returns values for that specific year.
        If year is not provided, returns values for all years.
        
        Args:
            session: The database session
            year: Optional year to filter by
            
        Returns:
            List[EFAEntryTypeGet]: A list of entry types with their values
        """
        # Base query to join entry types with their values
        statement = (
            select(
                EducationFreedomAccountEntryType.id,
                EducationFreedomAccountEntryType.name,
                EducationFreedomAccountEntryType.description,
                EducationFreedomAccountEntryTypeValue.year,
                EducationFreedomAccountEntryTypeValue.value
            )
            .join(
                EducationFreedomAccountEntryTypeValue,
                EducationFreedomAccountEntryType.id == EducationFreedomAccountEntryTypeValue.education_freedom_account_entry_type_id_fk
            )
        )
        
        # Apply year filter if provided
        if year is not None:
            statement = statement.where(EducationFreedomAccountEntryTypeValue.year == year)
            
        # Order by entry type ID and year
        statement = statement.order_by(
            EducationFreedomAccountEntryType.id,
            EducationFreedomAccountEntryTypeValue.year.desc()
        )
        
        results = session.exec(statement).all()
        
        if not results:
            detail = "No education freedom account entry type values found"
            if year is not None:
                detail += f" for year {year}"
            raise HTTPException(status_code=404, detail=detail)
            
        # Convert results to EFAEntryTypeGet objects
        return [
            EFAEntryTypeGet(
                id=result[0],
                name=result[1],
                description=result[2],
                year=result[3],
                value=result[4]
            )
            for result in results
        ]
    
    def get_entries(
        self, 
        session: Session, 
        year: Optional[int] = None,
        district_id: Optional[int] = None,
        town_id: Optional[int] = None
    ) -> List[EducationFreedomAccountEntryGet]:
        """
        Get education freedom account entries, optionally filtered by year, district ID, and town ID.
        
        Args:
            session: The database session
            year: Optional year to filter by
            district_id: Optional district ID to filter by
            town_id: Optional town ID to filter by (if both district_id and town_id are provided, district_id takes precedence)
            
        Returns:
            List[EducationFreedomAccountEntryGet]: A list of entries
        """
        # Base query for entries
        statement = select(EducationFreedomAccountEntry)
        
        # Apply year filter if provided
        if year is not None:
            statement = statement.where(EducationFreedomAccountEntry.year == year)
        
        # Apply district_id filter if provided
        if district_id is not None:
            # We need to join with the town_district_xref table to filter by district_id
            # First, get all town IDs that belong to the district
            town_ids_stmt = select(TownDistrictLink.town_id_fk).where(
                TownDistrictLink.district_id_fk == district_id
            )
            town_ids = session.exec(town_ids_stmt).all()
            
            if not town_ids:
                raise HTTPException(
                    status_code=404,
                    detail=f"No towns found for district ID {district_id}"
                )
            
            # Filter entries by these town IDs
            statement = statement.where(EducationFreedomAccountEntry.town_id_fk.in_(town_ids))
        # Apply town_id filter if provided and district_id is not provided
        elif town_id is not None:
            statement = statement.where(EducationFreedomAccountEntry.town_id_fk == town_id)
            
        # Order by town ID and year (most recent first)
        statement = statement.order_by(
            EducationFreedomAccountEntry.town_id_fk, 
            EducationFreedomAccountEntry.year.desc()
        )
        
        results = session.exec(statement).all()
        
        if not results:
            detail = "No education freedom account entries found"
            if year is not None:
                detail += f" for year {year}"
            if district_id is not None:
                detail += f" for district ID {district_id}"
            elif town_id is not None:
                detail += f" for town ID {town_id}"
            raise HTTPException(status_code=404, detail=detail)
        
        # Convert to response schema
        return [EducationFreedomAccountEntryGet.model_validate(result.model_dump()) for result in results]

# Create singleton instance
education_freedom_account_service = EducationFreedomAccountService() 