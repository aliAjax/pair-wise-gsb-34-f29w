import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { listHazardTicket } from "../api/HazardTicket";
import type { HazardTicket } from "../types/HazardTicket";

interface TicketQuery {
  rectify_status?: string;
  device_id?: number;
}

export const fetchHazardTickets = createAsyncThunk(
  "hazardTicket/fetchAll",
  async (query: TicketQuery | void) => listHazardTicket(query ?? {})
);

const hazardTicketSlice = createSlice({
  name: "hazardTicket",
  initialState: { rows: [] as HazardTicket[], loading: false },
  reducers: {
    upsertTicket(state, action: { payload: HazardTicket }) {
      const idx = state.rows.findIndex((row) => row.id === action.payload.id);
      if (idx >= 0) state.rows[idx] = action.payload;
      else state.rows.unshift(action.payload);
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchHazardTickets.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchHazardTickets.fulfilled, (state, action) => {
        state.rows = action.payload;
        state.loading = false;
      })
      .addCase(fetchHazardTickets.rejected, (state) => {
        state.loading = false;
      });
  }
});

export const { upsertTicket } = hazardTicketSlice.actions;
export default hazardTicketSlice.reducer;
