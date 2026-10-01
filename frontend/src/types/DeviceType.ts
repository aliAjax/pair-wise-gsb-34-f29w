export const DeviceType = ["EXTINGUISHER", "HYDRANT", "SMOKE_DETECTOR", "SPRINKLER", "EXIT_LIGHT"] as const;
export type DeviceType = (typeof DeviceType)[number];
