import { useEffect, useState } from "react";

import Sidebar from "../components/Sidebar";
import WalletCard from "../components/WalletCard";
import LoanCard from "../components/LoanCard";

import API from "../services/api";

function BorrowerDashboard() {

  const [wallet, setWallet] = useState(null);

  const [loans, setLoans] = useState([]);

  useEffect(() => {

    fetchWallet();

    fetchLoans();

  }, []);

  const fetchWallet = async () => {

    try {

      const response = await API.get("/wallet");

      setWallet(response.data);

    } catch (error) {

      console.log(error);
    }
  };

  const fetchLoans = async () => {

    try {

      const response = await API.get("/loans");

      setLoans(response.data);

    } catch (error) {

      console.log(error);
    }
  };

  return (

    <div className="flex bg-gray-100 min-h-screen">

      <Sidebar />

      <div className="flex-1 p-10">

        <h1 className="text-4xl font-bold text-blue-700 mb-10">
          Borrower Dashboard
        </h1>

        {
          wallet && (
            <WalletCard balance={wallet.balance} />
          )
        }

        <h2 className="text-3xl font-bold mt-12 mb-6">
          My Loans
        </h2>

        <div className="flex flex-wrap gap-6">

          {
            loans.map((loan) => (

              <LoanCard
                key={loan.id}
                loan={loan}
              />

            ))
          }

        </div>

      </div>

    </div>
  );
}

export default BorrowerDashboard;