from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.entities import UserProfile, PantryItem
from app.schemas.api_models import PantryItemRead, PantryItemCreate

router = APIRouter(prefix="/pantry", tags=["Pantry"])

@router.get("", response_model=List[PantryItemRead])
def list_pantry_items(db: Session = Depends(get_db)):
    profile = db.query(UserProfile).first()
    if not profile:
        return []
    items = db.query(PantryItem).filter(PantryItem.user_id == profile.id).order_by(PantryItem.added_at.desc()).all()
    return [
        PantryItemRead(
            id=p.id,
            name=p.name,
            quantity=p.quantity,
            category=p.category,
            added_at=p.added_at
        ) for p in items
    ]

@router.post("", response_model=PantryItemRead, status_code=status.HTTP_201_CREATED)
def add_pantry_item(item_in: PantryItemCreate, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    clean_name = item_in.name.strip()
    # Check for duplicate pantry item
    existing = db.query(PantryItem).filter(
        PantryItem.user_id == profile.id,
        PantryItem.name.ilike(clean_name)
    ).first()

    if existing:
        # Update quantity or return existing without duplicating
        existing.quantity = item_in.quantity.strip()
        existing.category = item_in.category.strip()
        db.commit()
        db.refresh(existing)
        return PantryItemRead(
            id=existing.id,
            name=existing.name,
            quantity=existing.quantity,
            category=existing.category,
            added_at=existing.added_at
        )

    new_item = PantryItem(
        user_id=profile.id,
        name=clean_name,
        quantity=item_in.quantity.strip(),
        category=item_in.category.strip()
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return PantryItemRead(
        id=new_item.id,
        name=new_item.name,
        quantity=new_item.quantity,
        category=new_item.category,
        added_at=new_item.added_at
    )

@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_pantry_item(item_id: int, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    item = db.query(PantryItem).filter(
        PantryItem.id == item_id,
        PantryItem.user_id == profile.id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail=f"Pantry item with ID {item_id} not found.")

    db.delete(item)
    db.commit()
    return {"status": "ok", "message": f"Pantry item '{item.name}' removed."}
