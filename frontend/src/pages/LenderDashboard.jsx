import { useEffect, useState } from "react";

import Sidebar from "../components/Sidebar";
import WalletCard from "../components/WalletCard";
import LoanCard from "../components/LoanCard";

import API from "../services/api";

function LenderDashboard() {

  const [wallet, setWallet] = useState(null);

  const [loans, setLoans] = useState([]);

  // =====================================
  // FETCH DATA
  // =====================================

  useEffect(() => {

    fetchWallet();

    fetchApprovedLoans();

  }, []);

  // =====================================
  // FETCH WALLET
  // =====================================

  const fetchWallet = async () => {

    try {

      const response = await API.get(
        "/wallet"
      );

      setWallet(response.data);

    } catch (error) {

      console.log(error);
    }
  };

  // =====================================
  // FETCH APPROVED LOANS
  // =====================================

  const fetchApprovedLoans = async () => {

    try {

      const response = await API.get(
        "/approved-loans"
      );

      console.log("APPROVED LOANS:", response.data);

      setLoans(response.data);

    } catch (error) {

      console.log(error);
    }
  };

  // =====================================
  // UI
  // =====================================

  return (

    <div className="flex bg-gray-100 min-h-screen">

      <Sidebar />

      <div className="flex-1 p-10">

        <h1 className="text-5xl font-bold text-green-700 mb-10">
          Lender Dashboard
        </h1>

        {/* WALLET */}

        {
          wallet && (

            <div className="mb-10">

              <WalletCard
                balance={wallet.balance}
              />

            </div>
          )
        }

        {/* APPROVED LOANS */}

        <h2 className="text-3xl font-bold mb-8">
          Approved Loans
        </h2>

        {
          loans.length === 0 ? (

            <div className="bg-white p-10 rounded-3xl shadow-md text-xl text-gray-500">

              No approved loans available

            </div>

          ) : (

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">

              {
                loans.map((loan) => (

                  <LoanCard
                    key={loan.id}
                    loan={loan}
                    showInvestButton={true}
                    refreshLoans={fetchApprovedLoans}
                    refreshWallet={fetchWallet}
                  />

                ))
              }

            </div>
          )
        }

      </div>

    </div>
  );
}

export default LenderDashboard;