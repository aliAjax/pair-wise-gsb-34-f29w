import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { listOutageBatches } from "../api/DeviceOutage";
import type { OutageBatch } from "../types/DeviceOutage";

export const fetchOutageBatches = createAsyncThunk("deviceOutage/fetchBatches", async () =>
  listOutageBatches()
);

const deviceOutageSlice = createSlice({
  name: "deviceOutage",
  initialState: { batches: [] as OutageBatch[], loading: false },
  reducers: {
    upsertBatch(state, action: { payload: OutageBatch }) {
      const idx = state.batches.findIndex((row) => row.id === action.payload.id);
      if (idx >= 0) state.batches[idx] = action.payload;
      else state.batches.unshift(action.payload);
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchOutageBatches.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchOutageBatches.fulfilled, (state, action) => {
        state.batches = action.payload;
        state.loading = false;
      })
      .addCase(fetchOutageBatches.rejected, (state) => {
        state.loading = false;
      });
  }
});

export const { upsertBatch } = deviceOutageSlice.actions;
export default deviceOutageSlice.reducer;
