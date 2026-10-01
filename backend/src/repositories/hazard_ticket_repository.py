from src.models.hazard_ticket import HazardTicket


class HazardTicketRepository:
    def __init__(self, db):
        self.db = db

    def find_all(self, rectify_status=None, device_id=None):
        query = self.db.query(HazardTicket)
        if rectify_status:
            query = query.filter(HazardTicket.rectify_status == rectify_status)
        if device_id is not None:
            query = query.filter(HazardTicket.device_id == device_id)
        return query.order_by(HazardTicket.id.asc()).all()

    def find_by_devices(self, device_ids, include_verified=False):
        if not device_ids:
            return []
        query = self.db.query(HazardTicket).filter(HazardTicket.device_id.in_(device_ids))
        if not include_verified:
            # 已复验关闭的不再级联作废
            query = query.filter(HazardTicket.rectify_status != "VERIFIED")
        return query.all()

    def get(self, ticket_id):
        return self.db.query(HazardTicket).filter(HazardTicket.id == ticket_id).one_or_none()

    def get_by_result(self, result_id):
        return (
            self.db.query(HazardTicket)
            .filter(HazardTicket.result_id == result_id)
            .one_or_none()
        )

    def create(self, **fields):
        row = HazardTicket(**fields)
        self.db.add(row)
        self.db.flush()
        return row
