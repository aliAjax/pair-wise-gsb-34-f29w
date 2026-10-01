import { createSlice } from "@reduxjs/toolkit";
import { getActorId, setActorId } from "../api/client";

// 本地会话：切换演示身份（巡检员/维保商/物业主管/审计员），按钮显隐由角色驱动
const sessionSlice = createSlice({
  name: "session",
  initialState: { actorId: getActorId() },
  reducers: {
    switchActor(state, action: { payload: number }) {
      state.actorId = action.payload;
      setActorId(action.payload);
    }
  }
});

export const { switchActor } = sessionSlice.actions;
export default sessionSlice.reducer;
