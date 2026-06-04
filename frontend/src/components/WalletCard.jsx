function WalletCard({ balance }) {

  return (

    <div className="bg-white shadow-lg rounded-2xl p-6 w-80">

      <h2 className="text-gray-500 text-lg">
        Wallet Balance
      </h2>

      <h1 className="text-4xl font-bold text-blue-600 mt-3">
        ₹ {balance}
      </h1>

    </div>
  );
}

export default WalletCard;