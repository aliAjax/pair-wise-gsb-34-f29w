import { http } from "./client";
import type { Building } from "../types/Building";

export function listBuilding(): Promise<Building[]> {
  return http.get<Building[]>("/building");
}

export function createBuilding(payload: Partial<Building>) {
  return http.post<Building>("/building", payload);
}
