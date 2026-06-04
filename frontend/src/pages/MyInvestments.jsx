import { useEffect, useState } from "react";

import Sidebar from "../components/Sidebar";

import API from "../services/api";

function MyInvestments() {

  const [investments, setInvestments] = useState([]);

  useEffect(() => {

    fetchInvestments();

  }, []);

  const fetchInvestments = async () => {

    try {

      const response = await API.get(
        "/my-investments"
      );

      setInvestments(response.data);

    } catch (error) {

      console.log(error);
    }
  };

  return (

    <div className="flex bg-gray-100 min-h-screen">

      <Sidebar />

      <div className="flex-1 p-10">

        <h1 className="text-4xl font-bold text-green-700 mb-10">
          My Investments
        </h1>

        <div className="grid grid-cols-3 gap-6">

          {
            investments.map((investment) => (

              <div
                key={investment.id}
                className="bg-white p-6 rounded-2xl shadow-lg"
              >

                <h2 className="text-2xl font-bold text-green-700">
                  ₹ {investment.amount}
                </h2>

                <p className="mt-3">
                  Loan ID:
                  {" "}
                  {investment.loan_id}
                </p>

              </div>

            ))
          }

        </div>

      </div>

    </div>
  );
}

export default MyInvestments;