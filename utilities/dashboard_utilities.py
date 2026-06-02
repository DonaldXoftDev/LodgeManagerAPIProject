from typing import Any

from sqlalchemy import or_, and_, Select

from app.schemas.dashboard import DashboardFilters


def apply_dashboard_filters(filters: dict ,  filter_by: DashboardFilters, stmt: Select):
    if filter_by:
        room_expressions = []
        if filter_by.room_status_filters:
            for status in filter_by.room_status_filters:
                sql_expr = filters.get(status)

                if sql_expr is not None:
                    room_expressions.append(sql_expr)

        if room_expressions:
            stmt = stmt.where(or_(*room_expressions))

        financial_expressions = []
        if filter_by.financial_filters:
            for badge in filter_by.financial_filters:
                sql_expr = filters.get(badge)

                if sql_expr is not None:
                    financial_expressions.append(and_(*sql_expr))

        if financial_expressions:
            stmt = stmt.where(or_(*financial_expressions))

    return stmt