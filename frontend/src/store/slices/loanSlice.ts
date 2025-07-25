
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { LoanApplication } from '../../types';

interface LoanState {
  applications: LoanApplication[];
  loading: boolean;
  error: string | null;
}

const initialState: LoanState = {
  applications: [],
  loading: false,
  error: null,
};

const loanSlice = createSlice({
  name: 'loans',
  initialState,
  reducers: {
    fetchLoansStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    fetchLoansSuccess: (state, action: PayloadAction<LoanApplication[]>) => {
      state.applications = action.payload;
      state.loading = false;
    },
    fetchLoansFailure: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.loading = false;
    },
    updateLoanStatus: (state, action: PayloadAction<{ id: string; status: LoanApplication['status'] }>) => {
      const loan = state.applications.find(app => app.id === action.payload.id);
      if (loan) {
        loan.status = action.payload.status;
      }
    },
  },
});

export const { fetchLoansStart, fetchLoansSuccess, fetchLoansFailure, updateLoanStatus } = loanSlice.actions;
export default loanSlice.reducer;
