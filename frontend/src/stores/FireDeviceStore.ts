import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { listFireDevice } from "../api/FireDevice";
import type { FireDevice } from "../types/FireDevice";

interface DeviceQuery {
  building_id?: number;
  status?: string;
  device_type?: string;
}

export const fetchFireDevices = createAsyncThunk(
  "fireDevice/fetchAll",
  async (query: DeviceQuery | void) => listFireDevice(query ?? {})
);

const fireDeviceSlice = createSlice({
  name: "fireDevice",
  initialState: { rows: [] as FireDevice[], loading: false },
  reducers: {
    upsertDevice(state, action: { payload: FireDevice }) {
      const idx = state.rows.findIndex((row) => row.id === action.payload.id);
      if (idx >= 0) state.rows[idx] = action.payload;
      else state.rows.unshift(action.payload);
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchFireDevices.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchFireDevices.fulfilled, (state, action) => {
        state.rows = action.payload;
        state.loading = false;
      })
      .addCase(fetchFireDevices.rejected, (state) => {
        state.loading = false;
      });
  }
});

export const { upsertDevice } = fireDeviceSlice.actions;
export default fireDeviceSlice.reducer;
