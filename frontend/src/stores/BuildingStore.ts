import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { listBuilding } from "../api/Building";
import type { Building } from "../types/Building";

export const fetchBuildings = createAsyncThunk("building/fetchAll", async () => listBuilding());

const buildingSlice = createSlice({
  name: "building",
  initialState: { rows: [] as Building[], loading: false },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchBuildings.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchBuildings.fulfilled, (state, action) => {
        state.rows = action.payload;
        state.loading = false;
      })
      .addCase(fetchBuildings.rejected, (state) => {
        state.loading = false;
      });
  }
});

export default buildingSlice.reducer;
