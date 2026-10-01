
def build_building_dto(row):
    """ORM 楼栋 -> 响应 DTO；页面/store/service 不得散写字段。"""
    return {
        "id": row.id,
        "name": row.name,
        "campus": row.campus,
        "floor_count": row.floor_count,
        "fire_grade": row.fire_grade,
        "manager_id": row.manager_id,
        "address_code": row.address_code,
    }
