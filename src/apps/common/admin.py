from typing import Any, override

from django.contrib import admin
from django.db import transaction
from django.db.models import (
    Count,
    F,
    Func,
    IntegerField,
    Model,
    QuerySet,
)
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html


def heal_order(child_ids: list[Any], order: list[Any]) -> list[Any]:
    """Drop duplicates and stale ids from the order array, append new ones."""
    known = set(child_ids)
    healed = [pk for pk in dict.fromkeys(order) if pk in known]
    healed.extend(pk for pk in child_ids if pk not in healed)
    return healed


def _move_view_name(model: Any, direction: str) -> str:
    """Admin url name for a child's move view, shared by inline and parent."""
    meta = model._meta
    return f"{meta.app_label}_{meta.model_name}_move_{direction}"


class ArrayOrderedInline(admin.TabularInline):  # type: ignore[type-arg]
    """Inline whose rows are ordered by an id array stored on the parent."""

    order_field: str
    parent_fk: str

    readonly_fields = ("reorder",)
    extra = 0
    show_change_link = True

    @override
    def get_formset(
        self, request: HttpRequest, obj: Any = None, **kwargs: Any
    ) -> Any:
        if obj is not None:
            child_ids = list(
                self.model.objects.filter(**{self.parent_fk: obj})
                .order_by("id")
                .values_list("pk", flat=True)
            )
            healed = heal_order(child_ids, getattr(obj, self.order_field))
            if healed != getattr(obj, self.order_field):
                setattr(obj, self.order_field, healed)
                obj.save(update_fields=[self.order_field])
        return super().get_formset(request, obj, **kwargs)

    @override
    def has_add_permission(
        self, request: HttpRequest, obj: Any = None
    ) -> bool:
        return False

    @override
    def get_queryset(self, request: HttpRequest) -> QuerySet[Model]:
        """Order rows by array position; annotate position/total for arrows."""
        array = F(f"{self.parent_fk}__{self.order_field}")
        return (  # type: ignore[no-any-return]
            super()
            .get_queryset(request)
            .annotate(
                order_position=Func(
                    array,
                    F("id"),
                    function="array_position",
                    output_field=IntegerField(),
                ),
                order_total=Func(
                    array, function="cardinality", output_field=IntegerField()
                ),
            )
            .order_by("order_position")
        )

    @admin.display(description="order")
    def reorder(self, obj: Any) -> Any:
        """First row gets only down, last row only up, middle rows both."""
        if obj._state.adding:  # empty add-form row carries no annotations
            return ""
        position = obj.order_position
        total = obj.order_total
        if position is None:  # id missing from the parent's order array
            return ""
        up_name = _move_view_name(self.model, "up")
        down_name = _move_view_name(self.model, "down")
        up = format_html(
            '<a class="button" href="{}">&#9650;</a>',
            reverse(f"admin:{up_name}", args=[obj.pk]),
        )
        down = format_html(
            '<a class="button" href="{}">&#9660;</a>',
            reverse(f"admin:{down_name}", args=[obj.pk]),
        )
        if position <= 1:
            return down
        if position >= total:
            return up
        return format_html("{} {}", up, down)


class ArrayOrderedParentAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Parent admin that owns the move-up/down views for ordered children."""

    child_model: Any
    child_fk: str
    child_related_name: str  # reverse accessor to children, e.g. "questions"
    order_field: str

    @override
    def get_queryset(self, request: HttpRequest) -> QuerySet[Model]:
        """Annotate the child count once, so list_display avoids an N+1."""
        return (  # type: ignore[no-any-return]
            super()
            .get_queryset(request)
            .annotate(child_count=Count(self.child_related_name))
        )

    @override
    def get_urls(self) -> list[Any]:
        own = [
            path(
                "reorder/<uuid:pk>/up/",
                self.admin_site.admin_view(self.move_up),
                name=_move_view_name(self.child_model, "up"),
            ),
            path(
                "reorder/<uuid:pk>/down/",
                self.admin_site.admin_view(self.move_down),
                name=_move_view_name(self.child_model, "down"),
            ),
        ]
        return own + super().get_urls()

    @transaction.atomic
    def _swap(self, pk: Any, delta: int) -> None:
        """Swap a child with its neighbour in the parent's order array."""
        child = self.child_model.objects.get(pk=pk)
        parent = self.model.objects.select_for_update().get(
            pk=getattr(child, f"{self.child_fk}_id")
        )
        child_ids = list(
            self.child_model.objects.filter(**{self.child_fk: parent})
            .order_by("id")
            .values_list("pk", flat=True)
        )
        order = heal_order(child_ids, getattr(parent, self.order_field))
        if child.pk not in order:
            return
        index = order.index(child.pk)
        neighbour = index + delta
        if 0 <= neighbour < len(order):
            order[index], order[neighbour] = order[neighbour], order[index]
            setattr(parent, self.order_field, order)
            parent.save(update_fields=[self.order_field])

    def move_up(self, request: HttpRequest, pk: Any) -> HttpResponse:
        self._swap(pk, -1)
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "../../"))

    def move_down(self, request: HttpRequest, pk: Any) -> HttpResponse:
        self._swap(pk, +1)
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "../../"))
