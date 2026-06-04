import { useEffect, useState } from "react";

import Sidebar from "../components/Sidebar";

import API from "../services/api";

function MyLoans() {

  const [loans, setLoans] = useState([]);

  useEffect(() => {

    fetchLoans();

  }, []);

  const fetchLoans = async () => {

    try {

      const response = await API.get(
        "/my-loans"
      );

      setLoans(response.data);

    } catch (error) {

      console.log(error);
    }
  };

  const repayLoan = async (loanId) => {

    try {

      const response = await API.post(
        `/repay-loan/${loanId}`
      );

      alert(response.data.message);

      fetchLoans();

    } catch (error) {

      alert(
        error.response.data.detail
      );
    }
  };

  return (

    <div className="flex bg-gray-100 min-h-screen">

      <Sidebar />

      <div className="flex-1 p-10">

        <h1 className="text-4xl font-bold text-blue-700 mb-10">
          My Loans
        </h1>

        <div className="grid grid-cols-2 gap-6">

          {
            loans.map((loan) => (

              <div
                key={loan.id}
                className="bg-white p-6 rounded-2xl shadow-lg"
              >

                <h2 className="text-3xl font-bold text-blue-600">
                  ₹ {loan.amount}
                </h2>

                <p className="mt-3">
                  Interest:
                  {" "}
                  {loan.interest_rate}%
                </p>

                <p>
                  Tenure:
                  {" "}
                  {loan.tenure_days} Days
                </p>

                <p>
                  Status:
                  {" "}
                  {loan.status}
                </p>

                {
                  loan.status === "APPROVED" && (

                    <button
                      onClick={() =>
                        repayLoan(loan.id)
                      }
                      className="mt-5 bg-green-600 text-white px-5 py-2 rounded-xl"
                    >
                      Repay Loan
                    </button>

                  )
                }

              </div>

            ))
          }

        </div>

      </div>

    </div>
  );
}

export default MyLoans;