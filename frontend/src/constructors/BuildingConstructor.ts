import type { Building } from "../types/Building";

export const createDefaultBuilding = (
  overrides: Partial<Building> = {}
): Building => ({
  id: 0,
  name: "",
  campus: "",
  floor_count: 1,
  fire_grade: "SECOND",
  manager_id: null,
  address_code: "",
  ...overrides
});

export const createBuildingForm = createDefaultBuilding;
export const createBuildingResponse = createDefaultBuilding;
