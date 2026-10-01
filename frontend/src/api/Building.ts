import { http } from "./http";
import type { Building } from "../types/Building";

export function listBuilding(): Promise<Building[]> {
  return http.get<Building[]>("/building");
}

export function createBuilding(payload: Partial<Building>): Promise<Building> {
  return http.post<Building>("/building", payload);
}
