import { useState } from "react";

import Sidebar from "../components/Sidebar";

import API from "../services/api";

function ApplyLoan() {

  const [formData, setFormData] =
    useState({

      amount: "",
      interest_rate: "",
      tenure_months: "",
      purpose: ""

    });

  // =====================================
  // HANDLE INPUT CHANGE
  // =====================================

  const handleChange = (e) => {

    setFormData({

      ...formData,
      [e.target.name]: e.target.value

    });
  };

  // =====================================
  // APPLY LOAN
  // =====================================

  const handleApplyLoan = async () => {

    try {

      const response = await API.post(
        "/apply-loan",
        {
          amount: Number(formData.amount),
          interest_rate: Number(formData.interest_rate),
          tenure_months: Number(formData.tenure_months),
          purpose: formData.purpose
        }
      );

      console.log(response.data);

      alert("Loan applied successfully");

      // CLEAR FORM
      setFormData({

        amount: "",
        interest_rate: "",
        tenure_months: "",
        purpose: ""

      });

    } catch (error) {

      console.log(error);

      alert(
        JSON.stringify(error.response?.data) ||
        "Something went wrong"
      );
    }
  };

  return (

    <div className="flex">

      <Sidebar />

      <div className="p-10 w-full">

        <h1 className="text-4xl font-bold text-blue-700 mb-10">
          Apply Loan
        </h1>

        <div className="bg-white shadow-xl rounded-3xl p-10 w-[700px]">

          {/* AMOUNT */}

          <input
            type="number"
            name="amount"
            placeholder="Loan Amount"
            value={formData.amount}
            onChange={handleChange}
            className="w-full border p-4 rounded-xl mb-5"
          />

          {/* INTEREST */}

          <input
            type="number"
            name="interest_rate"
            placeholder="Interest Rate"
            value={formData.interest_rate}
            onChange={handleChange}
            className="w-full border p-4 rounded-xl mb-5"
          />

          {/* TENURE */}

          <input
            type="number"
            name="tenure_months"
            placeholder="Tenure Months"
            value={formData.tenure_months}
            onChange={handleChange}
            className="w-full border p-4 rounded-xl mb-5"
          />

          {/* PURPOSE */}

          <input
            type="text"
            name="purpose"
            placeholder="Purpose"
            value={formData.purpose}
            onChange={handleChange}
            className="w-full border p-4 rounded-xl mb-8"
          />

          {/* BUTTON */}

          <button
            onClick={handleApplyLoan}
            className="bg-blue-700 text-white px-8 py-4 rounded-xl w-full text-lg"
          >
            Apply Loan
          </button>

        </div>

      </div>

    </div>
  );
}

export default ApplyLoan;