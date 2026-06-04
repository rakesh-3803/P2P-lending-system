import { Link } from "react-router-dom";

function Sidebar() {

  const role = localStorage
    .getItem("role")
    ?.trim()
    .toUpperCase();

  return (

    <div className="w-64 h-screen bg-blue-900 text-white p-5">

      <h1 className="text-3xl font-bold mb-10">
        FinFlow
      </h1>

      <div className="flex flex-col gap-5">

        {/* ================================= */}
        {/* BORROWER */}
        {/* ================================= */}

        {
          role === "BORROWER" && (
            <>

              <Link to="/borrower">
                Dashboard
              </Link>

              <Link to="/borrower/apply-loan">
                Apply Loan
              </Link>

              <Link to="/my-loans">
                My Loans
              </Link>

              <Link to="/wallet">
                Wallet
              </Link>

              <Link to="/transactions">
                Transactions
              </Link>

              <Link to="/notifications">
                Notifications
              </Link>

              <Link to="/emi-calculator">
                EMI Calculator
              </Link>

            </>
          )
        }

        {/* ================================= */}
        {/* LENDER */}
        {/* ================================= */}

        {
          role === "LENDER" && (
            <>

              <Link to="/lender">
                Dashboard
              </Link>

              <Link to="/lender/investments">
                Investments
              </Link>

              <Link to="/wallet">
                Wallet
              </Link>

              <Link to="/transactions">
                Transactions
              </Link>

              <Link to="/notifications">
                Notifications
              </Link>

              <Link to="/emi-calculator">
                EMI Calculator
              </Link>

            </>
          )
        }

        {/* ================================= */}
        {/* ADMIN */}
        {/* ================================= */}

        {
          role === "ADMIN" && (
            <>

              <Link to="/admin">
                Admin Dashboard
              </Link>

              <Link to="/admin/users">
                Users
              </Link>

              <Link to="/transactions">
                Transactions
              </Link>

              <Link to="/notifications">
                Notifications
              </Link>

            </>
          )
        }

      </div>

    </div>
  );
}

export default Sidebar;