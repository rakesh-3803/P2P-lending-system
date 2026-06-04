import { useEffect, useState } from "react";

import Sidebar from "../components/Sidebar";

import API from "../services/api";

function Transactions() {

  const [transactions, setTransactions] = useState([]);

  useEffect(() => {

    fetchTransactions();

  }, []);

  const fetchTransactions = async () => {

    try {

      const response = await API.get(
        "/transactions"
      );

      setTransactions(response.data);

    } catch (error) {

      console.log(error);
    }
  };

  return (

    <div className="flex bg-gray-100 min-h-screen">

      <Sidebar />

      <div className="flex-1 p-10">

        <h1 className="text-4xl font-bold text-blue-700 mb-10">
          Transaction History
        </h1>

        <div className="bg-white rounded-2xl shadow-lg p-6">

          <table className="w-full">

            <thead>

              <tr className="border-b">

                <th className="text-left p-3">
                  ID
                </th>

                <th className="text-left p-3">
                  Type
                </th>

                <th className="text-left p-3">
                  Amount
                </th>

                <th className="text-left p-3">
                  Description
                </th>

              </tr>

            </thead>

            <tbody>

              {
                transactions.map((txn) => (

                  <tr
                    key={txn.id}
                    className="border-b"
                  >

                    <td className="p-3">
                      {txn.id}
                    </td>

                    <td className="p-3">
                      {txn.transaction_type}
                    </td>

                    <td className="p-3">
                      ₹ {txn.amount}
                    </td>

                    <td className="p-3">
                      {txn.description}
                    </td>

                  </tr>

                ))
              }

            </tbody>

          </table>

        </div>

      </div>

    </div>
  );
}

export default Transactions;