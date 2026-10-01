"""建筑楼栋响应构造器：ORM -> DTO。"""


def create_building_dto(row, **overrides):
    data = {
        "id": row.id,
        "name": row.name,
        "campus": row.campus,
        "floor_count": row.floor_count,
        "fire_grade": row.fire_grade,
        "manager_id": row.manager_id,
        "address_code": row.address_code,
    }
    data.update(overrides)
    return data
