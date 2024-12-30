from typing import List, Optional
from pydantic import BaseModel

class MarketToken(BaseModel):
    """Represents a token in a market with its price and other details."""
    token_id: str
    name: str
    price: str

class Market(BaseModel):
    """Represents a market with its details, including tokens and statistics."""
    id: str
    question: str
    description: Optional[str] = None
    volume: Optional[str] = None
    open_interest: Optional[str] = None
    tokens: List[MarketToken]
    is_active: bool = True

class EventMarket(BaseModel):
    """Represents a market from the Gamma API with additional event-level details."""
    id: str
    question: str
    description: Optional[str] = None
    volume: Optional[str] = None
    open_interest: Optional[str] = None
    tokens: List[MarketToken]
    is_active: bool = True
    event_id: str
    event_status: str
    created_at: str
    expires_at: Optional[str] = None
    
    @classmethod
    def from_gamma_event(cls, event: dict) -> "EventMarket":
        """Convert a Gamma API event to an EventMarket."""
        tokens = [
            MarketToken(
                token_id=outcome["id"],
                name=outcome["title"],
                price=str(outcome.get("probability", "0"))
            )
            for outcome in event.get("outcomes", [])
        ]
        
        return cls(
            id=event["id"],
            question=event["title"],
            description=event.get("description"),
            volume=str(event.get("volume", "0")),
            open_interest=str(event.get("liquidity", "0")),
            tokens=tokens,
            is_active=(
                event.get("active", False) is True
            ),
            event_id=event["id"],
            event_status=event.get("status", "unknown"),
            created_at=event.get("created_at", ""),
            expires_at=event.get("expires_at")
        )
