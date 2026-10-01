from src.models.building import Building


class BuildingRepository:
    def __init__(self, db):
        self.db = db

    def find_all(self):
        return self.db.query(Building).order_by(Building.id.asc()).all()

    def get(self, building_id):
        return self.db.query(Building).filter(Building.id == building_id).one_or_none()

    def create(self, **fields):
        row = Building(**fields)
        self.db.add(row)
        self.db.flush()
        return row
