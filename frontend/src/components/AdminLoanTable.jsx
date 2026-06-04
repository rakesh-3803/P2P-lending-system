import API from "../services/api";

function AdminLoanTable({
  loans,
  refreshLoans
}) {

  const approveLoan = async (loanId) => {

    try {

      await API.put(
        `/admin/loan/${loanId}/approve`
      );

      alert("Loan Approved");

      refreshLoans();

    } catch (error) {

      console.log(error);
    }
  };

  const rejectLoan = async (loanId) => {

    try {

      await API.put(
        `/admin/loan/${loanId}/reject`
      );

      alert("Loan Rejected");

      refreshLoans();

    } catch (error) {

      console.log(error);
    }
  };

  return (

    <div className="bg-white rounded-2xl shadow-lg p-6 overflow-x-auto">

      <table className="w-full">

        <thead>

          <tr className="border-b">

            <th className="text-left p-3">
              Loan ID
            </th>

            <th className="text-left p-3">
              Amount
            </th>

            <th className="text-left p-3">
              Purpose
            </th>

            <th className="text-left p-3">
              Status
            </th>

            <th className="text-left p-3">
              Actions
            </th>

          </tr>

        </thead>

        <tbody>

          {
            loans.map((loan) => (

              <tr
                key={loan.id}
                className="border-b"
              >

                <td className="p-3">
                  {loan.id}
                </td>

                <td className="p-3">
                  ₹ {loan.amount}
                </td>

                <td className="p-3">
                  {loan.purpose}
                </td>

                <td className="p-3">
                  {loan.status}
                </td>

                <td className="p-3 flex gap-3">

                  <button
                    onClick={() => approveLoan(loan.id)}
                    className="bg-green-600 text-white px-4 py-2 rounded"
                  >
                    Approve
                  </button>

                  <button
                    onClick={() => rejectLoan(loan.id)}
                    className="bg-red-600 text-white px-4 py-2 rounded"
                  >
                    Reject
                  </button>

                </td>

              </tr>

            ))
          }

        </tbody>

      </table>

    </div>
  );
}

export default AdminLoanTable;