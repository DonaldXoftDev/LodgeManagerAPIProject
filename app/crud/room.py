from app.core.enums import RoomStatus, BadgeTexts, BadgeVariants
from app.crud.payment import crud_payment
from app.models.lease import Lease
from app.models.room import Room
from app.models.tenantprofile import TenantProfile
from app.models.user import User
from app.schemas.dashboard import DashboardFilters
from app.schemas.room import RoomCreate, RoomUpdate, RoomGridSummary
from sqlalchemy.orm import Session
from app.crud.base_crud import CRUDBase
from sqlalchemy import func, select, case, and_, Integer, cast, or_


class CRUDRoom(CRUDBase[Room, RoomCreate, RoomUpdate]):
    #method to get room by lodge and number
    # method to get many rooms in a lodge with pagination support

    def get_room_by_lodge_and_number(self, db: Session, room_no: str, lodge_id: int):
        """Retrieve a specific room by its room number."""

        return db.query(self.model).filter(
            self.model.lodge_id == lodge_id,
            self.model.room_no == room_no
        ).first()

    def get_rooms(self, db: Session, lodge_id: int, skip: int = 0, max_limit: int = 50):
        """Retrieve a list of rooms with pagination support."""
        return db.query(self.model).filter(self.model.lodge_id == lodge_id).offset(skip).limit(max_limit).all()

    def get_dashboard_rooms(
            self,
            db: Session,
            filter_by: DashboardFilters,
            lodge_id: int,
            skip: int = 0,
            limit: int = 50
    ) :

        payment_subq = crud_payment.get_payment_subq()

        days_left = cast(func.julianday(Lease.end_date) - func.julianday('now'), Integer)  # only supported by sqlite,
        # change in production to postgres

        total_paid = func.coalesce(payment_subq.c.total_amt_paid, 0)

        has_payed_in_full = total_paid == Lease.agreed_rent_amt
        incomplete_payment = total_paid < Lease.agreed_rent_amt
        full_name = User.full_name
        stmt = (select(
            Lease.id.label('lease_id'),
            Room.room_no.label('room_no'),
            case(
                (and_(Room.status == RoomStatus.OCCUPIED, days_left >= 90, has_payed_in_full), BadgeTexts.SAFE),
                (and_(Room.status == RoomStatus.OCCUPIED, days_left >= 0, days_left < 90,has_payed_in_full), BadgeTexts.EXPIRING),
                (and_(Room.status == RoomStatus.OCCUPIED, days_left < 0, has_payed_in_full), BadgeTexts.OVERDUE),
                (and_(Room.status == RoomStatus.OCCUPIED, incomplete_payment ), BadgeTexts.OWING),
                (Room.status == RoomStatus.VACANT, RoomStatus.VACANT),
                (Room.status == RoomStatus.MAINTENANCE, RoomStatus.MAINTENANCE),
                else_='Unknown_badge_text'
            ).label('badge_text'),

            case(
                (and_(Room.status == RoomStatus.OCCUPIED, days_left >= 90, has_payed_in_full), BadgeVariants.SUCCESS),
                (and_(Room.status == RoomStatus.OCCUPIED, days_left >= 0, has_payed_in_full), BadgeVariants.WARNING),
                (and_(Room.status == RoomStatus.OCCUPIED, days_left < 0, has_payed_in_full), BadgeVariants.DANGER),
                (and_(Room.status == RoomStatus.OCCUPIED, incomplete_payment), BadgeVariants.INFO),
                (Room.status == RoomStatus.VACANT, BadgeVariants.INACTIVE),
                (Room.status == RoomStatus.MAINTENANCE, BadgeVariants.NEED_REPAIR),
                else_= 'Unknown_variant'
            ).label('badge_variant'),

            case(
                (Room.status == RoomStatus.OCCUPIED, func.concat(User.first_name, ' ', User.last_name, )),
                (Room.status == RoomStatus.VACANT, 'Ready to Lease'),
                (Room.status == RoomStatus.MAINTENANCE, 'Unavailable'),
                else_='Invalid'
            ).label('main_display_text'),

            case(
                (
                    and_(Room.status == RoomStatus.OCCUPIED, days_left < 0, has_payed_in_full),
                    func.concat(func.abs(days_left, ), 'days overdue')
                ),
                (Room.status == RoomStatus.OCCUPIED, func.concat(days_left, 'days left')),
                (Room.status == RoomStatus.VACANT, 'Available'),
                (Room.status == RoomStatus.MAINTENANCE, 'Under Maintenance'),
                else_='Invalid'
            ).label('sub_display_text'),

        ).select_from(
            Room
        ).outerjoin(
            Lease, Lease.room_id == Room.id
        ).outerjoin(
            TenantProfile, Lease.tenant_id == TenantProfile.id
        ).outerjoin(
            User, TenantProfile.user_id == User.id
        ).outerjoin(
            payment_subq, payment_subq.c.lease_id == Lease.id
        ).where(
            Room.lodge_id == lodge_id
        ).group_by(
            Lease.id,
            User.first_name,
            User.last_name,
            Room.room_no,
            Lease.agreed_rent_amt,
            Lease.end_date,
            Room.status,

        ))

        #if filters dict is empty, fetch the list of categorized rooms with pagination support
        #otherwise only fetch the list of room categories that match the provided filters

        occupied_expr = Room.status == RoomStatus.OCCUPIED
        vacant_expr = Room.status == RoomStatus.VACANT
        maintenance_expr = Room.status == RoomStatus.MAINTENANCE

        filter_menu = {
            RoomStatus.OCCUPIED : occupied_expr,
            RoomStatus.VACANT : vacant_expr,
            RoomStatus.MAINTENANCE: maintenance_expr,
            BadgeTexts.SAFE: (occupied_expr, has_payed_in_full, days_left >= 90),
            BadgeTexts.EXPIRING: (occupied_expr, has_payed_in_full, days_left >= 0, days_left < 90),
            BadgeTexts.OVERDUE: (occupied_expr, has_payed_in_full , days_left < 0),
            BadgeTexts.OWING: (occupied_expr, has_payed_in_full, incomplete_payment)
        }

        if filter_by:

            all_expr = []
            if filter_by.room_status_filters:
                for status in filter_by.room_status_filters:
                    sql_expr = filter_menu.get(status)

                    if sql_expr is not None:
                        all_expr.append(sql_expr)

            if filter_by.financial_filters:
                for badge in filter_by.financial_filters:
                    sql_expr  = filter_menu.get(badge)

                    if sql_expr is not None:
                        all_expr.append(and_(*sql_expr))


            stmt = stmt.where(or_(*all_expr))


        # if filter_by == BadgeTexts.SAFE:
        #     stmt = stmt.where((Room.status == RoomStatus.OCCUPIED)).having(has_payed_in_full, days_left >= 90)
        #
        # elif filter_by == BadgeTexts.EXPIRING:
        #     stmt = stmt.where((Room.status == RoomStatus.OCCUPIED)).having(
        #         has_payed_in_full, days_left >= 0, days_left < 90)
        #
        # elif filter_by == BadgeTexts.OVERDUE:
        #     stmt = stmt.where((Room.status == RoomStatus.OCCUPIED)).having(has_payed_in_full, days_left < 0)
        #
        # elif filter_by == RoomStatus.VACANT:
        #     stmt = stmt.where((Room.status == RoomStatus.VACANT))
        #
        # elif filter_by == RoomStatus.MAINTENANCE:
        #     stmt = stmt.where((Room.status == RoomStatus.MAINTENANCE))
        #
        # elif filter_by == BadgeTexts.OWING:
        #     stmt = stmt.where((Room.status == RoomStatus.OCCUPIED)).having(incomplete_payment)

        stmt = stmt.offset(skip).limit(limit)

        db_rooms = db.execute(stmt).mappings().all()
        return db_rooms


crud_room = CRUDRoom(Room)
