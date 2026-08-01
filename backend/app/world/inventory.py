"""
Inventory data models for Headcanon.

The Inventory System manages the ownership, location, condition, and
interaction state of all objects within the universe.

Every item exists in exactly one inventory at any time.  Transfers atomically
move an item from one owner to another.

Reference: docs/universe/11_inventory.md
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator, model_validator

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class InventoryType(StrEnum):
    """Who or what owns this inventory."""

    CHARACTER = "Character"
    LOCATION = "Location"
    CONTAINER = "Container"
    WORLD = "World"


class ItemCondition(StrEnum):
    """Physical condition of an inventory item."""

    NEW = "New"
    GOOD = "Good"
    WORN = "Worn"
    DAMAGED = "Damaged"
    BROKEN = "Broken"
    DESTROYED = "Destroyed"


class ItemVisibility(StrEnum):
    """Visibility state of an inventory item."""

    VISIBLE = "Visible"
    HIDDEN = "Hidden"
    EQUIPPED = "Equipped"
    STORED = "Stored"
    LOCKED = "Locked"


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class InventoryItem(BaseModel, frozen=True):
    """
    A single item entry within an inventory.

    References the canonical Object definition by ID; mutable state is
    tracked here in the inventory record rather than mutating the immutable
    Object definition.

    Attributes:
        item_id:           Object ID of the item (must follow ``obj_`` convention).
        name:              Canonical item name (denormalised for fast display).
        description:       Brief description.
        category:          Item category label.
        current_owner:     ID of the current owner (character / location / container).
        current_location:  Location ID where the item physically resides.
        condition:         Physical condition.
        visibility:        Current visibility state.
        quantity:          Number of units (≥ 1).
        interaction_state: Free-form key/value pairs tracking interaction flags
                           (e.g. ``{"locked": true, "charged": 80}``).
    """

    item_id: str = Field(pattern=r"^obj_\S+$")
    name: str = Field(min_length=1)
    description: str = ""
    category: str | None = None
    current_owner: str | None = None
    current_location: str | None = None
    condition: ItemCondition = ItemCondition.GOOD
    visibility: ItemVisibility = ItemVisibility.VISIBLE
    quantity: int = Field(default=1, ge=1)
    interaction_state: dict[str, bool | int | float | str] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Root model
# ---------------------------------------------------------------------------


class Inventory(BaseModel):
    """
    An inventory belonging to a character, location, container, or the world.

    Attributes:
        inventory_id: Unique identifier for this inventory record.
        owner_id:     ID of the entity that owns this inventory.
        type:         What kind of entity owns this inventory.
        capacity:     Maximum number of item slots (``None`` = unlimited).
        items:        List of inventory items currently held.
    """

    inventory_id: str = Field(min_length=1)
    owner_id: str = Field(min_length=1)
    type: InventoryType
    capacity: int | None = Field(default=None, ge=1)
    items: list[InventoryItem] = Field(default_factory=list)

    @field_validator("items")
    @classmethod
    def item_ids_are_unique(cls, v: list[InventoryItem]) -> list[InventoryItem]:
        """An item must not appear more than once in the same inventory."""
        ids = [item.item_id for item in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Each object ID must appear at most once in an inventory.")
        return v

    @model_validator(mode="after")
    def capacity_not_exceeded(self) -> Inventory:
        """The number of items must not exceed the declared capacity."""
        if self.capacity is not None and len(self.items) > self.capacity:
            raise ValueError(
                f"Inventory '{self.inventory_id}' exceeds its capacity of "
                f"{self.capacity} (currently holds {len(self.items)} items)."
            )
        return self
