import { configureStore } from "@reduxjs/toolkit";

import buildingReducer from "./BuildingStore";
import dashboardReducer from "./DashboardStore";
import deviceOutageReducer from "./DeviceOutageStore";
import fireDeviceReducer from "./FireDeviceStore";
import hazardTicketReducer from "./HazardTicketStore";
import inspectionResultReducer from "./InspectionResultStore";
import inspectionTaskReducer from "./InspectionTaskStore";
import sessionReducer from "./SessionStore";

export const store = configureStore({
  reducer: {
    session: sessionReducer,
    building: buildingReducer,
    fireDevice: fireDeviceReducer,
    inspectionTask: inspectionTaskReducer,
    inspectionResult: inspectionResultReducer,
    hazardTicket: hazardTicketReducer,
    deviceOutage: deviceOutageReducer,
    dashboard: dashboardReducer
  }
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
