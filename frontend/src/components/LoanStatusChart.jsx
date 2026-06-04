import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend
} from "recharts";

function LoanStatusChart({ loans }) {

  const pending = loans.filter(
    (loan) => loan.status === "PENDING"
  ).length;

  const approved = loans.filter(
    (loan) => loan.status === "APPROVED"
  ).length;

  const rejected = loans.filter(
    (loan) => loan.status === "REJECTED"
  ).length;

  const data = [
    {
      name: "Pending",
      value: pending
    },
    {
      name: "Approved",
      value: approved
    },
    {
      name: "Rejected",
      value: rejected
    },
  ];

  const COLORS = [
    "#facc15",
    "#22c55e",
    "#ef4444"
  ];

  return (

    <div className="bg-white p-6 rounded-2xl shadow-lg">

      <h2 className="text-2xl font-bold mb-6">
        Loan Status Analytics
      </h2>

      <PieChart width={400} height={300}>

        <Pie
          data={data}
          dataKey="value"
          cx="50%"
          cy="50%"
          outerRadius={100}
          label
        >

          {
            data.map((entry, index) => (

              <Cell
                key={index}
                fill={COLORS[index]}
              />

            ))
          }

        </Pie>

        <Tooltip />

        <Legend />

      </PieChart>

    </div>
  );
}

export default LoanStatusChart;