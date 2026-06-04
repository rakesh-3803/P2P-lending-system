import { useState } from "react";

import Sidebar from "../components/Sidebar";

function EMICalculator() {

  const [loanAmount, setLoanAmount] = useState("");

  const [interestRate, setInterestRate] = useState("");

  const [months, setMonths] = useState("");

  const [emi, setEmi] = useState(null);

  const [totalPayment, setTotalPayment] =
    useState(null);

  const [totalInterest, setTotalInterest] =
    useState(null);

  const calculateEMI = () => {

    const P = Number(loanAmount);

    const annualRate = Number(interestRate);

    const N = Number(months);

    if (!P || !annualRate || !N) {

      alert("Please enter valid values");

      return;
    }

    // Monthly interest rate
    const R = annualRate / 12 / 100;

    // EMI Formula
    const EMI =
      (P * R * Math.pow(1 + R, N)) /
      (Math.pow(1 + R, N) - 1);

    const total = EMI * N;

    const interest = total - P;

    setEmi(
      EMI.toFixed(2)
    );

    setTotalPayment(
      total.toFixed(2)
    );

    setTotalInterest(
      interest.toFixed(2)
    );
  };

  return (

    <div className="flex bg-gray-100 min-h-screen">

      <Sidebar />

      <div className="flex-1 p-10">

        <h1 className="text-4xl font-bold text-blue-700 mb-10">
          EMI Calculator
        </h1>

        <div className="bg-white p-8 rounded-2xl shadow-lg w-[500px]">

          <input
            type="number"
            placeholder="Loan Amount"
            className="w-full p-3 border rounded mb-4"
            onChange={(e) =>
              setLoanAmount(e.target.value)
            }
          />

          <input
            type="number"
            placeholder="Annual Interest Rate (%)"
            className="w-full p-3 border rounded mb-4"
            onChange={(e) =>
              setInterestRate(e.target.value)
            }
          />

          <input
            type="number"
            placeholder="Tenure (Months)"
            className="w-full p-3 border rounded mb-4"
            onChange={(e) =>
              setMonths(e.target.value)
            }
          />

          <button
            onClick={calculateEMI}
            className="w-full bg-blue-600 text-white p-3 rounded-xl hover:bg-blue-700"
          >
            Calculate EMI
          </button>

          {
            emi && (

              <div className="mt-8 space-y-4">

                <div className="bg-blue-100 p-5 rounded-xl">

                  <h2 className="text-xl font-bold text-blue-700">
                    Monthly EMI
                  </h2>

                  <h1 className="text-4xl font-bold mt-2">
                    ₹ {emi}
                  </h1>

                </div>

                <div className="bg-green-100 p-5 rounded-xl">

                  <h2 className="text-xl font-bold text-green-700">
                    Total Payment
                  </h2>

                  <h1 className="text-3xl font-bold mt-2">
                    ₹ {totalPayment}
                  </h1>

                </div>

                <div className="bg-red-100 p-5 rounded-xl">

                  <h2 className="text-xl font-bold text-red-700">
                    Total Interest
                  </h2>

                  <h1 className="text-3xl font-bold mt-2">
                    ₹ {totalInterest}
                  </h1>

                </div>

              </div>

            )
          }

        </div>

      </div>

    </div>
  );
}

export default EMICalculator;