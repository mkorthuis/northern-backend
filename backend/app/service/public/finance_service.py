from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from fastapi import HTTPException

from app.model.finance import (
    DOEForm, BalanceSheet, Revenue, Expenditure,
    BalanceEntryType, BalanceFundType,
    RevenueEntryType, RevenueFundType,
    ExpenditureEntryType, ExpenditureFundType,
    BalanceEntryCategory, BalanceEntrySuperCategory,
    RevenueEntryCategory, RevenueEntrySuperCategory,
    ExpenditureEntryCategory, ExpenditureEntrySuperCategory,
    StateCostPerPupil, DistrictCostPerPupil,
    ExpenditureStateRollup, RevenueStateTotal, ExpenditureStateTotal
)
from app.model.location import District
from app.schema.finance_schema import (
    DOEFormGet, BalanceSheetGet, RevenueGet, ExpenditureGet,
    FinancialReportGet, AllEntryTypesGet,
    BalanceEntryTypeGet, RevenueEntryTypeGet, ExpenditureEntryTypeGet,
    BalanceEntryCategoryGet, RevenueEntryCategoryGet, ExpenditureEntryCategoryGet,
    BalanceFundTypeGet, RevenueFundTypeGet, ExpenditureFundTypeGet,
    AllFundTypesGet, StateCostPerPupilGet, DistrictCostPerPupilGet,
    ExpenditureStateRollupGet, RevenueStateTotalGet, ExpenditureStateTotalGet
)
from app.schema.location_schema import DistrictGet

class FinanceService:
    def get_doe_form(self, session: Session, district_id: int, year: int) -> Optional[DOEForm]:
        """Get DOE form by district_id and year."""
        statement = select(DOEForm).where(
            DOEForm.district_id_fk == district_id,
            DOEForm.year == year
        )
        return session.exec(statement)
    
    def get_balance_sheets(self, session: Session, doe_form_id: int) -> List[BalanceSheet]:
        """Get balance sheets for a DOE form."""
        statement = select(BalanceSheet).where(BalanceSheet.doe_form_id_fk == doe_form_id)
        return session.exec(statement).all()
    
    def get_revenues(self, session: Session, doe_form_id: int) -> List[Revenue]:
        """Get revenues for a DOE form."""
        statement = select(Revenue).where(Revenue.doe_form_id_fk == doe_form_id)
        return session.exec(statement).all()
    
    def get_expenditures(self, session: Session, doe_form_id: int) -> List[Expenditure]:
        """Get expenditures for a DOE form."""
        statement = select(Expenditure).where(Expenditure.doe_form_id_fk == doe_form_id)
        return session.exec(statement).all()
    
    def _enhance_balance_sheets(self, session: Session, balance_sheets: List[BalanceSheet]) -> List[BalanceSheetGet]:
        """Enhance balance sheets with related data."""
        result = []
        for bs in balance_sheets:
            bs_dto = BalanceSheetGet.from_orm(bs)
            result.append(bs_dto)
            
        return result
    
    def _enhance_revenues(self, session: Session, revenues: List[Revenue]) -> List[RevenueGet]:
        """Enhance revenues with related data."""
        result = []
        for rev in revenues:
            rev_dto = RevenueGet.from_orm(rev)
            result.append(rev_dto)
            
        return result
    
    def _enhance_expenditures(self, session: Session, expenditures: List[Expenditure]) -> List[ExpenditureGet]:
        """Enhance expenditures with related data."""
        result = []
        for exp in expenditures:
            exp_dto = ExpenditureGet.from_orm(exp)
            result.append(exp_dto)
            
        return result
    
    def get_financial_report(self, session: Session, district_id: int, year: Optional[int] = None) -> List[FinancialReportGet]:
        """
        Get comprehensive financial report including DOE form and all related financial data
        for a specific district and year.
        
        Args:
            session: The database session
            district_id: The district ID to get the report for
            year: Optional year to filter by. If not provided, returns the most recent report.
        
        Returns:
            List[FinancialReportGet]: A list of comprehensive financial reports for the district
        """
        # Get the DOE form
        if year is not None:
            # If year is provided, get the specific DOE form
            statement = select(DOEForm).where(
                DOEForm.district_id_fk == district_id,
                DOEForm.year == year
            )
            doe_forms = session.exec(statement).all()
            if not doe_forms:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Financial report not found for district ID {district_id} and year {year}"
                )
        else:
            # If year is not provided, get the most recent DOE form for the district
            statement = select(DOEForm).where(
                DOEForm.district_id_fk == district_id
            ).order_by(DOEForm.year.desc())
            doe_forms = session.exec(statement).all()
            
            if not doe_forms:
                raise HTTPException(
                    status_code=404, 
                    detail=f"No financial reports found for district ID {district_id}"
                )
        
        results = []
        for doe_form in doe_forms:
            # Get related data
            balance_sheets = self.get_balance_sheets(session, doe_form.id)
            revenues = self.get_revenues(session, doe_form.id)
            expenditures = self.get_expenditures(session, doe_form.id)
            
            # Enhance data with related entities
            enhanced_balance_sheets = self._enhance_balance_sheets(session, balance_sheets)
            enhanced_revenues = self._enhance_revenues(session, revenues)
            enhanced_expenditures = self._enhance_expenditures(session, expenditures)
            
            doe_form_dto = DOEFormGet.model_validate(doe_form.model_dump())
            
            results.append(FinancialReportGet(
                doe_form=doe_form_dto,
                balance_sheets=enhanced_balance_sheets,
                revenues=enhanced_revenues,
                expenditures=enhanced_expenditures
            ))
        
        return results
    
    def get_balance_entry_types(self, session: Session) -> List[BalanceEntryTypeGet]:
        """Get all balance entry types with their categories and super categories."""
        # Get all balance entry types
        statement = select(BalanceEntryType)
        entry_types = session.exec(statement).all()
        
        # Enhance with category and super category
        result = []
        for entry_type in entry_types:
            # Get category
            category = session.get(BalanceEntryCategory, entry_type.balance_entry_category_type_id_fk)
            
            # Create enhanced entry type
            enhanced_entry_type = BalanceEntryTypeGet.model_validate(entry_type.model_dump())
            
            if category:
                # Get super category
                super_category = session.get(BalanceEntrySuperCategory, category.balance_entry_super_category_type_id_fk)
                
                # Create enhanced category
                enhanced_category = BalanceEntryCategoryGet.model_validate(category.model_dump())
                
                if super_category:
                    enhanced_category.super_category = super_category
                
                enhanced_entry_type.category = enhanced_category
            
            result.append(enhanced_entry_type)
        
        return result
    
    def get_revenue_entry_types(self, session: Session) -> List[RevenueEntryTypeGet]:
        """Get all revenue entry types with their categories and super categories."""
        # Get all revenue entry types
        statement = select(RevenueEntryType)
        entry_types = session.exec(statement).all()
        
        # Enhance with category and super category
        result = []
        for entry_type in entry_types:
            # Get category
            category = session.get(RevenueEntryCategory, entry_type.revenue_entry_category_type_id_fk)
            
            # Create enhanced entry type
            enhanced_entry_type = RevenueEntryTypeGet.model_validate(entry_type.model_dump())
            
            if category:
                # Get super category
                super_category = session.get(RevenueEntrySuperCategory, category.revenue_entry_super_category_type_id_fk)
                
                # Create enhanced category
                enhanced_category = RevenueEntryCategoryGet.model_validate(category.model_dump())
                
                if super_category:
                    enhanced_category.super_category = super_category
                
                enhanced_entry_type.category = enhanced_category
            
            result.append(enhanced_entry_type)
        
        return result
    
    def get_expenditure_entry_types(self, session: Session) -> List[ExpenditureEntryTypeGet]:
        """Get all expenditure entry types with their categories and super categories."""
        # Get all expenditure entry types
        statement = select(ExpenditureEntryType)
        entry_types = session.exec(statement).all()
        
        # Enhance with category and super category
        result = []
        for entry_type in entry_types:
            # Get category
            category = session.get(ExpenditureEntryCategory, entry_type.expenditure_entry_category_type_id_fk)
            
            # Create enhanced entry type
            enhanced_entry_type = ExpenditureEntryTypeGet.model_validate(entry_type.model_dump())
            
            if category:
                # Get super category
                super_category = session.get(ExpenditureEntrySuperCategory, category.expenditure_entry_super_category_type_id_fk)
                
                # Create enhanced category
                enhanced_category = ExpenditureEntryCategoryGet.model_validate(category.model_dump())
                
                if super_category:
                    enhanced_category.super_category = super_category
                
                enhanced_entry_type.category = enhanced_category
            
            result.append(enhanced_entry_type)
        
        return result
    
    def get_all_entry_types(self, session: Session) -> AllEntryTypesGet:
        """Get all entry types (balance, revenue, expenditure) with their categories and super categories."""
        balance_entry_types = self.get_balance_entry_types(session)
        revenue_entry_types = self.get_revenue_entry_types(session)
        expenditure_entry_types = self.get_expenditure_entry_types(session)
        
        return AllEntryTypesGet(
            balance_entry_types=balance_entry_types,
            revenue_entry_types=revenue_entry_types,
            expenditure_entry_types=expenditure_entry_types
        )
        
    def get_balance_fund_types(self, session: Session) -> List[BalanceFundTypeGet]:
        """Get all balance fund types."""
        statement = select(BalanceFundType)
        fund_types = session.exec(statement).all()
        
        result = []
        for fund_type in fund_types:
            fund_type_dto = BalanceFundTypeGet.model_validate(fund_type.model_dump())
            result.append(fund_type_dto)
            
        return result
    
    def get_revenue_fund_types(self, session: Session) -> List[RevenueFundTypeGet]:
        """Get all revenue fund types."""
        statement = select(RevenueFundType)
        fund_types = session.exec(statement).all()
        
        result = []
        for fund_type in fund_types:
            fund_type_dto = RevenueFundTypeGet.model_validate(fund_type.model_dump())
            result.append(fund_type_dto)
            
        return result
    
    def get_expenditure_fund_types(self, session: Session) -> List[ExpenditureFundTypeGet]:
        """Get all expenditure fund types."""
        statement = select(ExpenditureFundType)
        fund_types = session.exec(statement).all()
        
        result = []
        for fund_type in fund_types:
            fund_type_dto = ExpenditureFundTypeGet.model_validate(fund_type.model_dump())
            result.append(fund_type_dto)
            
        return result
        
    def get_all_fund_types(self, session: Session) -> AllFundTypesGet:
        """Get all fund types (balance, revenue, expenditure)."""
        balance_fund_types = self.get_balance_fund_types(session)
        revenue_fund_types = self.get_revenue_fund_types(session)
        expenditure_fund_types = self.get_expenditure_fund_types(session)
        
        return AllFundTypesGet(
            balance_fund_types=balance_fund_types,
            revenue_fund_types=revenue_fund_types,
            expenditure_fund_types=expenditure_fund_types
        )
        
    def get_state_per_pupil_costs(self, session: Session, year: Optional[int] = None) -> List[StateCostPerPupilGet]:
        """
        Get state level per pupil costs, optionally filtered by year.
        
        Args:
            session: The database session
            year: Optional year to filter by
            
        Returns:
            List[StateCostPerPupilGet]: A list of state per pupil costs
        """
        statement = select(StateCostPerPupil)
        
        # Apply year filter if provided
        if year is not None:
            statement = statement.where(StateCostPerPupil.year == year)
            
        # Order by year (most recent first)
        statement = statement.order_by(StateCostPerPupil.year.desc())
        
        # Execute query
        results = session.exec(statement).all()
        
        # Convert to response schema
        return [StateCostPerPupilGet.model_validate(result.model_dump()) for result in results]
        
    def get_district_per_pupil_costs(self, session: Session, district_id: Optional[int] = None, year: Optional[int] = None) -> List[DistrictCostPerPupilGet]:
        """
        Get district level per pupil costs, optionally filtered by district ID and year.
        
        Args:
            session: The database session
            district_id: Optional district ID to filter by
            year: Optional year to filter by
            
        Returns:
            List[DistrictCostPerPupilGet]: A list of district per pupil costs
        """
        statement = select(DistrictCostPerPupil)
        
        # Apply filters if provided
        if district_id is not None:
            statement = statement.where(DistrictCostPerPupil.district_id_fk == district_id)
            
        if year is not None:
            statement = statement.where(DistrictCostPerPupil.year == year)
            
        # Order by district ID and year (most recent first)
        statement = statement.order_by(DistrictCostPerPupil.district_id_fk, DistrictCostPerPupil.year.desc())
        
        # Execute query
        results = session.exec(statement).all()
        
        # Convert to response schema
        return [DistrictCostPerPupilGet.model_validate(result.model_dump()) for result in results]

    def get_state_expenditure_rollup(self, session: Session, year: Optional[int] = None) -> List[ExpenditureStateRollupGet]:
        """
        Get state level expenditure rollup data, optionally filtered by year.
        
        Args:
            session: The database session
            year: Optional year to filter by
            
        Returns:
            List[ExpenditureStateRollupGet]: A list of state expenditure rollup data
        """
        statement = select(ExpenditureStateRollup)
        
        # Apply year filter if provided
        if year is not None:
            statement = statement.where(ExpenditureStateRollup.year == year)
            
        # Order by year (most recent first)
        statement = statement.order_by(ExpenditureStateRollup.year.desc())
        
        # Execute query
        results = session.exec(statement).all()
        
        # Convert to response schema
        return [ExpenditureStateRollupGet.model_validate(result.model_dump()) for result in results]
        
    def get_state_expenditure(self, session: Session, year: Optional[int] = None, expenditure_entry_type_id: Optional[int] = None) -> List[ExpenditureStateTotalGet]:
        """
        Get state level expenditure total data, optionally filtered by year and expenditure entry type.
        
        Args:
            session: The database session
            year: Optional year to filter by
            expenditure_entry_type_id: Optional expenditure entry type ID to filter by
            
        Returns:
            List[ExpenditureStateTotalGet]: A list of state expenditure total data
        """
        statement = select(ExpenditureStateTotal)
        
        # Apply filters if provided
        if year is not None:
            statement = statement.where(ExpenditureStateTotal.year == year)
            
        if expenditure_entry_type_id is not None:
            statement = statement.where(ExpenditureStateTotal.expenditure_entry_type_id_fk == expenditure_entry_type_id)
            
        # Order by year (most recent first)
        statement = statement.order_by(ExpenditureStateTotal.year.desc())
        
        # Execute query
        results = session.exec(statement).all()
        
        # Convert to response schema
        return [ExpenditureStateTotalGet.model_validate(result.model_dump()) for result in results]

    def get_state_revenue(self, session: Session, year: Optional[int] = None, revenue_entry_type_id: Optional[int] = None) -> List[RevenueStateTotalGet]:
        """
        Get state level revenue total data, optionally filtered by year and revenue entry type.
        
        Args:
            session: The database session
            year: Optional year to filter by
            revenue_entry_type_id: Optional revenue entry type ID to filter by
            
        Returns:
            List[RevenueStateTotalGet]: A list of state revenue total data
        """
        statement = select(RevenueStateTotal)
        
        # Apply filters if provided
        if year is not None:
            statement = statement.where(RevenueStateTotal.year == year)
            
        if revenue_entry_type_id is not None:
            statement = statement.where(RevenueStateTotal.revenue_entry_type_id_fk == revenue_entry_type_id)
            
        # Order by year (most recent first)
        statement = statement.order_by(RevenueStateTotal.year.desc())
        
        # Execute query
        results = session.exec(statement).all()
        
        # Convert to response schema
        return [RevenueStateTotalGet.model_validate(result.model_dump()) for result in results]

# Create singleton instance
finance_service = FinanceService() 