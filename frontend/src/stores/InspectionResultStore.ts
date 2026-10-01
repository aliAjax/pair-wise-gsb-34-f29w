import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { listInspectionResult } from "../api/InspectionResult";
import type { InspectionResult } from "../types/InspectionResult";

interface ResultQuery {
  task_id?: number;
  device_id?: number;
  review_flag?: string;
}

export const fetchInspectionResults = createAsyncThunk(
  "inspectionResult/fetchAll",
  async (query: ResultQuery | void) => listInspectionResult(query ?? {})
);

const inspectionResultSlice = createSlice({
  name: "inspectionResult",
  initialState: { rows: [] as InspectionResult[], loading: false },
  reducers: {
    upsertResult(state, action: { payload: InspectionResult }) {
      const idx = state.rows.findIndex((row) => row.id === action.payload.id);
      if (idx >= 0) state.rows[idx] = action.payload;
      else state.rows.unshift(action.payload);
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchInspectionResults.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchInspectionResults.fulfilled, (state, action) => {
        state.rows = action.payload;
        state.loading = false;
      })
      .addCase(fetchInspectionResults.rejected, (state) => {
        state.loading = false;
      });
  }
});

export const { upsertResult } = inspectionResultSlice.actions;
export default inspectionResultSlice.reducer;
