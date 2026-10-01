import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { getDashboardSummary } from "../api/Dashboard";
import type { DashboardSummary } from "../types/Dashboard";

export const fetchDashboardSummary = createAsyncThunk("dashboard/fetchSummary", async () =>
  getDashboardSummary()
);

const initial: { data: DashboardSummary | null; loading: boolean } = {
  data: null,
  loading: false
};

const dashboardSlice = createSlice({
  name: "dashboard",
  initialState: initial,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchDashboardSummary.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchDashboardSummary.fulfilled, (state, action) => {
        state.data = action.payload;
        state.loading = false;
      })
      .addCase(fetchDashboardSummary.rejected, (state) => {
        state.loading = false;
      });
  }
});

export default dashboardSlice.reducer;
