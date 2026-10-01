import { useMemo } from "react";
import type { DeviceOutageWindow } from "../types/DeviceOutageWindow";
import type { TaskDeviceAssignment } from "../types/TaskDeviceAssignment";
import type { FireDevice } from "../types/FireDevice";
import { AssignmentStatusText } from "../constants/AssignmentStatus";
import { OutageStatusText } from "../constants/OutageStatus";

export interface SchedulingSummary {
  totalOriginal: number;
  totalBackup: number;
  totalPending: number;
  totalRescheduled: number;
  occupiedSeats: number;
  /** 每台备用设备在停用期间的占用率。 */
  backupUsage: { device: FireDevice; used: number; ratio: number }[];
  /** 每个原排期当前的落地方式（备用 / 待补检 / 已补排）。 */
  originResolution: {
    originId: number;
    taskId: number;
    kind: "BACKUP" | "PENDING_RECHECK" | "RESCHEDULED";
    targetDeviceId: number | null;
  }[];
}

/**
 * 停用排期汇总：原关系数、备用切换数、待补检数、备用设备占用率。
 * 原任务关系（ORIGINAL）永不删除，这里通过派生关系反推其落地方式。
 */
export function useOutageScheduling(
  devices: FireDevice[],
  windows: DeviceOutageWindow[],
  assignmentsByWindow: Record<number, TaskDeviceAssignment[]>,
  originals: TaskDeviceAssignment[] = []
): SchedulingSummary {
  return useMemo(() => {
    const allDerived = Object.values(assignmentsByWindow).flat();
    const totalBackup = allDerived.filter(
      (a) => a.assignment_status === "BACKUP"
    ).length;
    const totalPending = allDerived.filter(
      (a) => a.assignment_status === "PENDING_RECHECK"
    ).length;
    const totalRescheduled = allDerived.filter(
      (a) => a.assignment_status === "RESCHEDULED"
    ).length;
    const occupiedSeats = windows
      .filter((w) => w.outage_status === "CONFIRMED")
      .reduce((sum, w) => sum + (w.occupied_capacity ?? 0), 0);

    const usedByDevice = new Map<number, number>();
    allDerived
      .filter((a) => a.assignment_status === "BACKUP" && a.actual_device_id)
      .forEach((a) => {
        const id = a.actual_device_id as number;
        usedByDevice.set(id, (usedByDevice.get(id) ?? 0) + a.seats);
      });
    const backupUsage = devices
      .filter((d) => usedByDevice.has(d.id))
      .map((device) => {
        const used = usedByDevice.get(device.id) ?? 0;
        return {
          device,
          used,
          ratio: device.capacity > 0 ? used / device.capacity : 0
        };
      });

    const originResolution = originals.map((origin) => {
      const derived = allDerived
        .filter((a) => a.origin_assignment_id === origin.id)
        // 优先展示补排 > 备用 > 待补检
        .sort((a, b) => {
          const rank: Record<string, number> = {
            RESCHEDULED: 0,
            BACKUP: 1,
            PENDING_RECHECK: 2
          };
          return rank[a.assignment_status] - rank[b.assignment_status];
        })[0];
      return {
        originId: origin.id,
        taskId: origin.task_id,
        kind: (derived?.assignment_status ??
          "PENDING_RECHECK") as SchedulingSummary["originResolution"][number]["kind"],
        targetDeviceId: derived?.actual_device_id ?? null
      };
    });

    return {
      totalOriginal: originals.length,
      totalBackup,
      totalPending,
      totalRescheduled,
      occupiedSeats,
      backupUsage,
      originResolution
    };
  }, [devices, windows, assignmentsByWindow, originals]);
}

export function assignmentLabel(status: string): string {
  return (
    AssignmentStatusText[status as keyof typeof AssignmentStatusText] ?? status
  );
}

export function outageStatusLabel(status: string): string {
  return OutageStatusText[status as keyof typeof OutageStatusText] ?? status;
}
