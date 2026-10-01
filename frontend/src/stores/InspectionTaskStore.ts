import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { listInspectionTask } from "../api/InspectionTask";
import type { InspectionTask } from "../types/InspectionTask";

interface TaskQuery {
  status?: string;
  building_id?: number;
}

export const fetchInspectionTasks = createAsyncThunk(
  "inspectionTask/fetchAll",
  async (query: TaskQuery | void) => listInspectionTask(query ?? {})
);

const inspectionTaskSlice = createSlice({
  name: "inspectionTask",
  initialState: { rows: [] as InspectionTask[], loading: false },
  reducers: {
    upsertTask(state, action: { payload: InspectionTask }) {
      const idx = state.rows.findIndex((row) => row.id === action.payload.id);
      if (idx >= 0) state.rows[idx] = action.payload;
      else state.rows.unshift(action.payload);
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchInspectionTasks.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchInspectionTasks.fulfilled, (state, action) => {
        state.rows = action.payload;
        state.loading = false;
      })
      .addCase(fetchInspectionTasks.rejected, (state) => {
        state.loading = false;
      });
  }
});

export const { upsertTask } = inspectionTaskSlice.actions;
export default inspectionTaskSlice.reducer;
