import { create } from "zustand";
import {
  changeOutageWindow,
  confirmOutageWindow,
  confirmWithConflictGuard,
  listOutageWindows,
  listWindowAssignments,
  registerProcedure,
  resumeOutageWindow,
  restoreDevice,
  submitOutageWindow,
} from "../api/OutageWindow";
import type {
  ChangeWindowResponse,
  ConflictGuardResponse,
  DeviceOutageWindow,
  OutageChangePayload,
  OutageWindowCreatePayload,
} from "../types/DeviceOutageWindow";
import type { TaskDeviceAssignment } from "../types/TaskDeviceAssignment";

interface OutageState {
  windows: DeviceOutageWindow[];
  assignments: Record<number, TaskDeviceAssignment[]>;
  loading: boolean;
  lastConflict: ConflictGuardResponse | null;
  lastFailure: { windowId: number; resumeKey: string; message: string } | null;
  error: string | null;

  loadWindows: () => Promise<void>;
  loadAssignments: (windowId: number) => Promise<TaskDeviceAssignment[]>;
  submit: (payload: OutageWindowCreatePayload) => Promise<DeviceOutageWindow>;
  confirm: (windowId: number) => Promise<DeviceOutageWindow>;
  confirmGuard: (windowId: number, ownerId: number) => Promise<ConflictGuardResponse>;
  resume: (windowId: number, resumeKey: string) => Promise<DeviceOutageWindow>;
  change: (windowId: number, payload: OutageChangePayload) => Promise<ChangeWindowResponse>;
  addProcedure: (windowId: number, procedureType: string) => Promise<void>;
  restore: (deviceId: number) => Promise<{ rescheduled: number }>;
  clearError: () => void;
}

export const useOutageStore = create<OutageState>((set, get) => ({
  windows: [],
  assignments: {},
  loading: false,
  lastConflict: null,
  lastFailure: null,
  error: null,

  async loadWindows() {
    set({ loading: true, error: null });
    try {
      const windows = await listOutageWindows();
      set({ windows, loading: false });
    } catch (e) {
      set({ loading: false, error: (e as Error).message });
    }
  },

  async loadAssignments(windowId) {
    const rows = await listWindowAssignments(windowId);
    set((state) => ({
      assignments: { ...state.assignments, [windowId]: rows }
    }));
    return rows;
  },

  async submit(payload) {
    const row = await submitOutageWindow(payload);
    await get().loadWindows();
    return row;
  },

  async confirm(windowId) {
    set({ error: null, lastFailure: null });
    try {
      const row = await confirmOutageWindow(windowId);
      await get().loadWindows();
      await get().loadAssignments(windowId);
      return row;
    } catch (e) {
      const err = e as { message: string };
      // 后端返回的失败消息里带 resume_key，解析出来供“恢复”按钮直接续跑
      const match = /resume_key=([0-9a-f]+)/.exec(err.message ?? "");
      if (match) {
        set({ lastFailure: { windowId, resumeKey: match[1], message: err.message } });
      }
      set({ error: err.message });
      throw e;
    }
  },

  async confirmGuard(windowId, ownerId) {
    const response = await confirmWithConflictGuard(windowId, ownerId);
    set({ lastConflict: response });
    await get().loadWindows();
    return response;
  },

  async resume(windowId, resumeKey) {
    const row = await resumeOutageWindow(windowId, resumeKey);
    set({ lastFailure: null });
    await get().loadWindows();
    await get().loadAssignments(windowId);
    return row;
  },

  async change(windowId, payload) {
    const response = await changeOutageWindow(windowId, payload);
    await get().loadWindows();
    return response;
  },

  async addProcedure(windowId, procedureType) {
    await registerProcedure(windowId, procedureType);
  },

  async restore(deviceId) {
    return restoreDevice(deviceId);
  },

  clearError() {
    set({ error: null, lastFailure: null });
  }
}));
