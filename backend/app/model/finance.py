from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship
from .base import BaseMixin

if TYPE_CHECKING:
    from .location import District
else:
    # Need to use a string type hint at runtime
    District = "District"

class DOEForm(BaseMixin, table=True):
    __tablename__ = "doe_form"
    
    district_id_fk: int = Field(foreign_key="district.id")
    year: int
    
    district: District = Relationship()
    balance_sheets: List["BalanceSheet"] = Relationship(back_populates="doe_form")
    revenues: List["Revenue"] = Relationship(back_populates="doe_form")
    expenditures: List["Expenditure"] = Relationship(back_populates="doe_form")

# Balance Sheet Models
class BalanceEntrySuperCategory(BaseMixin, table=True):
    __tablename__ = "balance_entry_super_category_type"
    
    name: str = Field(max_length=255)
    categories: List["BalanceEntryCategory"] = Relationship(back_populates="super_category")

class BalanceEntryCategory(BaseMixin, table=True):
    __tablename__ = "balance_entry_category_type"
    
    name: str = Field(max_length=255)
    balance_entry_super_category_type_id_fk: int = Field(foreign_key="balance_entry_super_category_type.id")
    super_category: BalanceEntrySuperCategory = Relationship(back_populates="categories")
    entry_types: List["BalanceEntryType"] = Relationship(back_populates="category")

class BalanceEntryType(BaseMixin, table=True):
    __tablename__ = "balance_entry_type"
    
    name: str = Field(max_length=255)
    account_no: str = Field(max_length=50)
    page: Optional[str] = Field(max_length=50)
    line: Optional[str] = Field(max_length=50)
    balance_entry_category_type_id_fk: int = Field(foreign_key="balance_entry_category_type.id")
    
    category: BalanceEntryCategory = Relationship(back_populates="entry_types")
    balance_sheets: List["BalanceSheet"] = Relationship(back_populates="entry_type")

class BalanceFundType(BaseMixin, table=True):
    __tablename__ = "balance_fund_type"
    
    state_id: str = Field(max_length=50)
    state_name: str = Field(max_length=255)
    balance_sheets: List["BalanceSheet"] = Relationship(back_populates="fund_type")

class BalanceSheet(BaseMixin, table=True):
    __tablename__ = "balance_sheet"
    
    doe_form_id_fk: int = Field(foreign_key="doe_form.id")
    balance_entry_type_id_fk: int = Field(foreign_key="balance_entry_type.id")
    balance_fund_type_id_fk: int = Field(foreign_key="balance_fund_type.id")
    value: Optional[float]
    
    doe_form: DOEForm = Relationship(back_populates="balance_sheets")
    entry_type: BalanceEntryType = Relationship(back_populates="balance_sheets")
    fund_type: BalanceFundType = Relationship(back_populates="balance_sheets")

# Revenue Models
class RevenueEntrySuperCategory(BaseMixin, table=True):
    __tablename__ = "revenue_entry_super_category_type"
    
    name: str = Field(max_length=255)
    categories: List["RevenueEntryCategory"] = Relationship(back_populates="super_category")

class RevenueEntryCategory(BaseMixin, table=True):
    __tablename__ = "revenue_entry_category_type"
    
    name: str = Field(max_length=255)
    revenue_entry_super_category_type_id_fk: int = Field(foreign_key="revenue_entry_super_category_type.id")
    super_category: RevenueEntrySuperCategory = Relationship(back_populates="categories")
    entry_types: List["RevenueEntryType"] = Relationship(back_populates="category")

class RevenueEntryType(BaseMixin, table=True):
    __tablename__ = "revenue_entry_type"
    
    name: str = Field(max_length=255)
    account_no: str = Field(max_length=50)
    page: Optional[str] = Field(max_length=50)
    line: Optional[str] = Field(max_length=50)
    revenue_entry_category_type_id_fk: int = Field(foreign_key="revenue_entry_category_type.id")
    
    category: RevenueEntryCategory = Relationship(back_populates="entry_types")
    revenues: List["Revenue"] = Relationship(back_populates="entry_type")

class RevenueFundType(BaseMixin, table=True):
    __tablename__ = "revenue_fund_type"
    
    state_id: str = Field(max_length=50)
    state_name: str = Field(max_length=255)
    revenues: List["Revenue"] = Relationship(back_populates="fund_type")

class Revenue(BaseMixin, table=True):
    __tablename__ = "revenue"
    
    doe_form_id_fk: int = Field(foreign_key="doe_form.id")
    revenue_entry_type_id_fk: int = Field(foreign_key="revenue_entry_type.id")
    revenue_fund_type_id_fk: int = Field(foreign_key="revenue_fund_type.id")
    value: Optional[float]
    
    doe_form: DOEForm = Relationship(back_populates="revenues")
    entry_type: RevenueEntryType = Relationship(back_populates="revenues")
    fund_type: RevenueFundType = Relationship(back_populates="revenues")

class RevenueStateTotal(BaseMixin, table=True):
    """State-level revenue data by year and entry type"""
    __tablename__ = "revenue_state_total"
    
    revenue_entry_type_id_fk: int = Field(foreign_key="revenue_entry_type.id", index=True)
    year: int = Field(index=True)
    value: Optional[float] = Field(default=None)

# Expenditure Models
class ExpenditureEntrySuperCategory(BaseMixin, table=True):
    __tablename__ = "expenditure_entry_super_category_type"
    
    name: str = Field(max_length=255)
    categories: List["ExpenditureEntryCategory"] = Relationship(back_populates="super_category")

class ExpenditureEntryCategory(BaseMixin, table=True):
    __tablename__ = "expenditure_entry_category_type"
    
    name: str = Field(max_length=255)
    expenditure_entry_super_category_type_id_fk: int = Field(foreign_key="expenditure_entry_super_category_type.id")
    super_category: ExpenditureEntrySuperCategory = Relationship(back_populates="categories")
    entry_types: List["ExpenditureEntryType"] = Relationship(back_populates="category")

class ExpenditureEntryType(BaseMixin, table=True):
    __tablename__ = "expenditure_entry_type"
    
    name: str = Field(max_length=255)
    account_no: str = Field(max_length=50)
    page: Optional[str] = Field(max_length=50)
    line: Optional[str] = Field(max_length=50)
    expenditure_entry_category_type_id_fk: int = Field(foreign_key="expenditure_entry_category_type.id")
    
    category: ExpenditureEntryCategory = Relationship(back_populates="entry_types")
    expenditures: List["Expenditure"] = Relationship(back_populates="entry_type")

class ExpenditureFundType(BaseMixin, table=True):
    __tablename__ = "expenditure_fund_type"
    
    state_id: str = Field(max_length=50)
    state_name: str = Field(max_length=255)
    expenditures: List["Expenditure"] = Relationship(back_populates="fund_type")

class Expenditure(BaseMixin, table=True):
    __tablename__ = "expenditure"
    
    doe_form_id_fk: int = Field(foreign_key="doe_form.id")
    expenditure_entry_type_id_fk: int = Field(foreign_key="expenditure_entry_type.id")
    expenditure_fund_type_id_fk: int = Field(foreign_key="expenditure_fund_type.id")
    value: Optional[float]
    
    doe_form: DOEForm = Relationship(back_populates="expenditures")
    entry_type: ExpenditureEntryType = Relationship(back_populates="expenditures")
    fund_type: ExpenditureFundType = Relationship(back_populates="expenditures")

class ExpenditureStateRollup(BaseMixin, table=True):
    """State-level expenditure data by year and school level"""
    __tablename__ = "expenditure_state_rollup"
    
    year: int = Field(index=True)
    operating_elementary: Optional[float] = Field(default=None)
    operating_middle: Optional[float] = Field(default=None)
    operating_high: Optional[float] = Field(default=None)
    operating_total: Optional[float] = Field(default=None)
    current_elementary: Optional[float] = Field(default=None) 
    current_middle: Optional[float] = Field(default=None)
    current_high: Optional[float] = Field(default=None)
    current_total: Optional[float] = Field(default=None)
    total: Optional[float] = Field(default=None)

class ExpenditureStateTotal(BaseMixin, table=True):
    """State-level expenditure data by year and entry type"""
    __tablename__ = "expenditure_state_total"
    
    expenditure_entry_type_id_fk: int = Field(foreign_key="expenditure_entry_type.id", index=True)
    year: int = Field(index=True)
    value: Optional[float] = Field(default=None)

class StateCostPerPupil(BaseMixin, table=True):
    """State level cost per pupil data by year"""
    __tablename__ = "state_cost_per_pupil"
    
    year: int = Field(index=True)
    elementary: Optional[int] = None
    middle: Optional[int] = None
    high: Optional[int] = None
    total: Optional[int] = None

class DistrictCostPerPupil(BaseMixin, table=True):
    """District level cost per pupil data by year"""
    __tablename__ = "district_cost_per_pupil"
    
    district_id_fk: int = Field(foreign_key="district.id", index=True)
    year: int = Field(index=True)
    elementary: Optional[int] = None
    middle: Optional[int] = None
    high: Optional[int] = None
    total: Optional[int] = None
    
    district: "District" = Relationship(back_populates="cost_per_pupil") 