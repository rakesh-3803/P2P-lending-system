import {
  BrowserRouter,
  Routes,
  Route
} from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";

import BorrowerDashboard from "./pages/BorrowerDashboard";
import LenderDashboard from "./pages/LenderDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import ApplyLoan from "./pages/ApplyLoan";
import MyInvestments from "./pages/MyInvestments";
import EMICalculator from "./pages/EMICalculator";
import Transactions from "./pages/Transactions";
import Notifications from "./pages/Notifications";
import MyLoans from "./pages/MyLoans";
import Wallet from "./pages/Wallet";

function App() {

  return (

    <BrowserRouter>

      <Routes>

        <Route
          path="/"
          element={<Login />}
        />

        

        <Route
          path="/borrower"
          element={<BorrowerDashboard />}
        />
        
        <Route
          path="/borrower/apply-loan"
          element={<ApplyLoan />}
        />

        <Route
          path="/lender"
          element={<LenderDashboard />}
        />

        <Route
          path="/lender/investments"
          element={<MyInvestments />}
        />

        <Route
          path="/admin"
          element={<AdminDashboard />}
        />

        <Route
          path="/emi-calculator"
          element={<EMICalculator />}
        />

        <Route
          path="/transactions"
          element={<Transactions />}
        />

        <Route
          path="/notifications"
          element={<Notifications />}
        />

        <Route
          path="/my-loans"
          element={<MyLoans />}
        />

        <Route
          path="/wallet"
          element={<Wallet />}
        />

      </Routes>

    </BrowserRouter>
  );
}

export default App;