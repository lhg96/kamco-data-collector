from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class KamcoBasicInfo(BaseModel):
    """Basic information about an auction item."""
    PLNM_NO: str = Field(..., description="Public Announcement Number (공고번호)")
    PBCT_NO: str = Field(..., description="Public Auction Number (물건번호)")
    PLNM_NM: str = Field(..., description="Announcement Name (공고명)")
    PBCT_CLM_NM: Optional[str] = Field(None, description="Item Name (물건명)")
    LCTN_ADDR: Optional[str] = Field(None, description="Location Address (소재지)")
    LWSBID_PRC: Optional[str] = Field(None, description="Minimum Bid Price (최저입찰가)")
    PBANC_BGNG_YMD: Optional[str] = Field(None, description="Bidding Start Date (입찰시작일)")
    PBANC_END_YMD: Optional[str] = Field(None, description="Bidding End Date (입찰마감일)")
    # Additional fields that might be present
    ORG_NM: Optional[str] = None
    PRPT_DVSN_NM: Optional[str] = None
    BID_MTD_NM: Optional[str] = None
    DPSL_MTD_NM: Optional[str] = None
    PLNM_DT: Optional[str] = None
    AR: Optional[str] = None # Area
    CTGR_NM: Optional[str] = None # Category
    
    class Config:
        populate_by_name = True
        extra = "allow" # Allow extra fields from API response


class KamcoScheduleInfo(BaseModel):
    """Bidding schedule information."""
    PLNM_NO: str
    PBCT_NO: str
    BID_BGNG_DT: Optional[str] = Field(None, description="Bid Start Datetime")
    BID_END_DT: Optional[str] = Field(None, description="Bid End Datetime")
    OPENG_DT: Optional[str] = Field(None, description="Opening Datetime")
    # Add other fields as necessary
    
    class Config:
        populate_by_name = True
        extra = "allow"


class KamcoFileInfo(BaseModel):
    """Attached file information."""
    BATCH_FILE_SN: Optional[str] = None
    ATCH_FILE_PTCS_NO: Optional[str] = None
    ATCH_FILE_NM: Optional[str] = None
    ATCH_FILE_PATH_NM: Optional[str] = None
    
    class Config:
        populate_by_name = True
        extra = "allow"


class KamcoItem(BaseModel):
    """Complete aggregated KAMCO auction item."""
    PLNM_NO: str
    PBCT_NO: str
    announce_list_item: Dict[str, Any]
    basic_info: Optional[Dict[str, Any]] = None  # Storing Raw dict for flexibility, or could use KamcoBasicInfo
    schedule_info: List[Dict[str, Any]] = []
    file_info: List[Dict[str, Any]] = []
    collected_at: datetime = Field(default_factory=datetime.now)

    class Config:
        arbitrary_types_allowed = True
