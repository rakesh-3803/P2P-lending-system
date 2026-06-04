import { useEffect, useState } from "react";

import API from "../services/api";

import Sidebar from "../components/Sidebar";

function Wallet() {

  const [wallet, setWallet] = useState(null);

  const [amount, setAmount] = useState("");

  const [withdrawAmount, setWithdrawAmount] =
    useState("");

  // =====================================
  // FETCH WALLET
  // =====================================

  const fetchWallet = async () => {

    try {

      const response = await API.get("/wallet");

      setWallet(response.data);

    } catch (error) {

      console.log(error);
    }
  };

  useEffect(() => {

    fetchWallet();

  }, []);

  // =====================================
  // ADD MONEY
  // =====================================

  const handleAddMoney = async () => {

    try {

      await API.post(
        "/wallet/add-money",
        {
          amount: Number(amount)
        }
      );

      alert("Money added successfully");

      setAmount("");

      fetchWallet();

    } catch (error) {

      alert(
        error.response?.data?.detail
      );
    }
  };

  // =====================================
  // WITHDRAW MONEY
  // =====================================

  const handleWithdraw = async () => {

    try {

      await API.post(
        "/wallet/withdraw",
        {
          amount: Number(withdrawAmount)
        }
      );

      alert("Withdrawal successful");

      setWithdrawAmount("");

      fetchWallet();

    } catch (error) {

      alert(
        error.response?.data?.detail
      );
    }
  };

  return (

    <div className="flex">

      <Sidebar />

      <div className="p-10 w-full">

        <h1 className="text-3xl font-bold mb-8">
          Wallet
        </h1>

        {/* WALLET BALANCE */}

        <div className="bg-white shadow-lg rounded-2xl p-8 mb-10 w-[400px]">

          <h2 className="text-xl font-semibold mb-3">
            Current Balance
          </h2>

          <p className="text-4xl font-bold text-blue-700">

            ₹ {wallet?.balance || 0}

          </p>

        </div>

        {/* ADD MONEY */}

        <div className="bg-white shadow-lg rounded-2xl p-8 mb-10 w-[400px]">

          <h2 className="text-2xl font-semibold mb-5">
            Add Money
          </h2>

          <input
            type="number"
            placeholder="Enter amount"
            value={amount}
            onChange={(e) =>
              setAmount(e.target.value)
            }
            className="border p-3 rounded-xl w-full mb-5"
          />

          <button
            onClick={handleAddMoney}
            className="bg-green-600 text-white px-5 py-3 rounded-xl w-full"
          >
            Add Money
          </button>

        </div>

        {/* WITHDRAW */}

        <div className="bg-white shadow-lg rounded-2xl p-8 w-[400px]">

          <h2 className="text-2xl font-semibold mb-5">
            Withdraw Money
          </h2>

          <input
            type="number"
            placeholder="Enter amount"
            value={withdrawAmount}
            onChange={(e) =>
              setWithdrawAmount(e.target.value)
            }
            className="border p-3 rounded-xl w-full mb-5"
          />

          <button
            onClick={handleWithdraw}
            className="bg-red-600 text-white px-5 py-3 rounded-xl w-full"
          >
            Withdraw
          </button>

        </div>

      </div>

    </div>
  );
}

export default Wallet;