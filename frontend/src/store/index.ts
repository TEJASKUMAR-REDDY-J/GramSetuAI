
import { configureStore } from '@reduxjs/toolkit';
import authSlice from './slices/authSlice';
import loanSlice from './slices/loanSlice';

export const store = configureStore({
  reducer: {
    auth: authSlice,
    loans: loanSlice,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
