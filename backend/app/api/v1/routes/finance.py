from fastapi import APIRouter, Query, Path, HTTPException
from typing import List, Optional
from uuid import UUID

from app.api.v1.deps import SessionDep
from app.schema.finance_schema import (
    DOEFormGet, BalanceSheetGet, RevenueGet, ExpenditureGet,
    FinancialReportGet, AllEntryTypesGet, AllFundTypesGet,
    StateCostPerPupilGet, DistrictCostPerPupilGet,
    ExpenditureStateRollupGet, RevenueStateTotalGet, ExpenditureStateTotalGet
)
from app.service.public.finance_service import finance_service

router = APIRouter()

@router.get("/report", 
    response_model=List[FinancialReportGet],
    summary="Get financial report",
    description="Retrieves a comprehensive financial report for a specific district and year, including DOE form data and all related financial data.",
    response_description="Financial report with DOE form and related financial data")
def get_financial_report(
    session: SessionDep,
    district_id: int = Query(..., description="District ID"),
    year: Optional[int] = Query(None, description="Optional year to filter by")
):
    """
    Get a comprehensive financial report for a specific district and year.
    
    This includes:
    - DOE Form data
    - Balance sheets
    - Revenues
    - Expenditures
    
    All related data is included with appropriate details.
    """
    return finance_service.get_financial_report(
        session=session,
        district_id=district_id,
        year=year
    )

@router.get("/entry-types",
    response_model=AllEntryTypesGet,
    summary="Get all entry types",
    description="Retrieves all entry types (balance, revenue, expenditure) with their categories and super categories.",
    response_description="All entry types with categories and super categories")
def get_all_entry_types(
    session: SessionDep
):
    """
    Get all entry types (balance, revenue, expenditure) with their categories and super categories.
    
    This includes:
    - Balance entry types with their categories and super categories
    - Revenue entry types with their categories and super categories
    - Expenditure entry types with their categories and super categories
    """
    return finance_service.get_all_entry_types(session=session)

@router.get("/fund-types",
    response_model=AllFundTypesGet,
    summary="Get all fund types",
    description="Retrieves all fund types (balance, revenue, expenditure).",
    response_description="All fund types")
def get_all_fund_types(
    session: SessionDep
):
    """
    Get all fund types (balance, revenue, expenditure).
    
    This includes:
    - Balance fund types
    - Revenue fund types
    - Expenditure fund types
    """
    return finance_service.get_all_fund_types(session=session)

@router.get("/per-pupil/state",
    response_model=List[StateCostPerPupilGet],
    summary="Get state level per pupil costs",
    description="Retrieves state level per pupil costs, optionally filtered by year.",
    response_description="State level per pupil costs")
def get_state_per_pupil_costs(
    session: SessionDep,
    year: Optional[int] = Query(None, description="Optional year to filter by")
):
    """
    Get state level per pupil costs, optionally filtered by year.
    
    If year is not provided, returns data for all available years.
    """
    return finance_service.get_state_per_pupil_costs(
        session=session,
        year=year
    )

@router.get("/per-pupil/district",
    response_model=List[DistrictCostPerPupilGet],
    summary="Get district level per pupil costs",
    description="Retrieves district level per pupil costs, optionally filtered by district ID and year.",
    response_description="District level per pupil costs")
def get_district_per_pupil_costs(
    session: SessionDep,
    district_id: Optional[int] = Query(None, description="Optional district ID to filter by"),
    year: Optional[int] = Query(None, description="Optional year to filter by")
):
    """
    Get district level per pupil costs, optionally filtered by district ID and year.
    
    If district_id is not provided, returns data for all districts.
    If year is not provided, returns data for all available years.
    """
    return finance_service.get_district_per_pupil_costs(
        session=session,
        district_id=district_id,
        year=year
    )

@router.get("/state-expenditure-rollup", 
    response_model=List[ExpenditureStateRollupGet],
    summary="Get state level expenditure totals",
    description="Retrieves state level expenditure totals, optionally filtered by year. Pulled from https://www.education.nh.gov/who-we-are/division-of-educator-and-analytic-resources/bureau-of-education-statistics/financial-reports: State Average Cost Per Pupil and Total Expenditures",
    response_description="State level expenditure totals")
def get_state_expenditure_rollup(
    session: SessionDep,
    year: Optional[int] = Query(None, description="Optional year to filter by")
):
    """
    Get state level expenditure totals, optionally filtered by year.
    
    If year is provided, returns data for that specific year.
    If year is not provided, returns data for all available years in descending order (most recent first).
    
    The data includes:
    - Operating expenses (elementary, middle, high, total)
    - Current expenses (elementary, middle, high, total)
    - Total expenditures
    """
    return finance_service.get_state_expenditure_rollup(
        session=session,
        year=year
    )

@router.get("/state-expenditure", 
    response_model=List[ExpenditureStateTotalGet],
    summary="Get state level expenditure totals by entry type",
    description="Retrieves state level expenditure totals, optionally filtered by year and expenditure entry type.",
    response_description="State level expenditure totals by entry type")
def get_state_expenditure(
    session: SessionDep,
    year: Optional[int] = Query(None, description="Optional year to filter by"),
    expenditure_entry_type_id: Optional[int] = Query(None, description="Optional expenditure entry type ID to filter by")
):
    """
    Get state level expenditure totals, optionally filtered by year and expenditure entry type.
    
    If year is provided, returns data for that specific year.
    If expenditure_entry_type_id is provided, returns data for that specific expenditure entry type.
    If neither is provided, returns data for all available years and entry types in descending order by year (most recent first).
    
    The data includes:
    - Year
    - Expenditure entry type ID
    - Expenditure value
    """
    return finance_service.get_state_expenditure(
        session=session,
        year=year,
        expenditure_entry_type_id=expenditure_entry_type_id
    )

@router.get("/state-revenue", 
    response_model=List[RevenueStateTotalGet],
    summary="Get state level revenue totals",
    description="Retrieves state level revenue totals, optionally filtered by year and revenue entry type.",
    response_description="State level revenue totals")
def get_state_revenue(
    session: SessionDep,
    year: Optional[int] = Query(None, description="Optional year to filter by"),
    revenue_entry_type_id: Optional[int] = Query(None, description="Optional revenue entry type ID to filter by")
):
    """
    Get state level revenue totals, optionally filtered by year and revenue entry type.
    
    If year is provided, returns data for that specific year.
    If revenue_entry_type_id is provided, returns data for that specific revenue entry type.
    If neither is provided, returns data for all available years and entry types in descending order by year (most recent first).
    
    The data includes:
    - Year
    - Revenue entry type ID
    - Revenue value
    """
    return finance_service.get_state_revenue(
        session=session,
        year=year,
        revenue_entry_type_id=revenue_entry_type_id
    ) 