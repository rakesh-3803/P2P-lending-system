import API from "../services/api";

function LoanCard({

  loan,
  showInvestButton,
  showRepayButton,
  refreshLoans,
  refreshWallet

}) {

  // =====================================
  // INVEST
  // =====================================

  const handleInvest = async () => {

    const amount = prompt(
      "Enter investment amount"
    );

    if (!amount) return;

    try {

      await API.post(
        "/invest",
        {
          loan_id: loan.id,
          amount: Number(amount)
        }
      );

      alert("Investment successful");

      if (refreshLoans) {

        refreshLoans();
      }

      if (refreshWallet) {

        refreshWallet();
      }

    } catch (error) {

      console.log(error);

      alert(
        error.response?.data?.detail ||
        "Investment failed"
      );
    }
  };

  // =====================================
  // REPAY
  // =====================================

  const handleRepay = async () => {

    try {

      await API.put(
        `/repay-loan/${loan.id}`
      );

      alert("Loan repaid successfully");

      if (refreshLoans) {

        refreshLoans();
      }

      if (refreshWallet) {

        refreshWallet();
      }

    } catch (error) {

      console.log(error);

      alert(
        error.response?.data?.detail ||
        "Repayment failed"
      );
    }
  };

  return (

    <div className="bg-white p-6 rounded-2xl shadow-md w-[350px]">

      <h2 className="text-2xl font-bold mb-4">
        ₹ {loan.amount}
      </h2>

      <p className="mb-2">
        Interest: {loan.interest_rate}%
      </p>

      <p className="mb-2">
        Tenure: {loan.tenure_months} months
      </p>

      <p className="mb-4">
        Purpose: {loan.purpose}
      </p>

      {
        showInvestButton && (

          <button
            onClick={handleInvest}
            className="bg-green-600 text-white px-6 py-3 rounded-xl w-full"
          >
            Invest
          </button>
        )
      }

      {
        showRepayButton && (

          <button
            onClick={handleRepay}
            className="bg-blue-700 text-white px-6 py-3 rounded-xl w-full"
          >
            Repay Loan
          </button>
        )
      }

    </div>
  );
}

export default LoanCard;