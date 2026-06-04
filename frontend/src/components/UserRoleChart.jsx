import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from "recharts";

function UserRoleChart({ users }) {

  const borrowers = users.filter(
    (user) => user.role === "BORROWER"
  ).length;

  const lenders = users.filter(
    (user) => user.role === "LENDER"
  ).length;

  const admins = users.filter(
    (user) => user.role === "ADMIN"
  ).length;

  const data = [
    {
      role: "Borrowers",
      count: borrowers
    },
    {
      role: "Lenders",
      count: lenders
    },
    {
      role: "Admins",
      count: admins
    },
  ];

  return (

    <div className="bg-white p-6 rounded-2xl shadow-lg">

      <h2 className="text-2xl font-bold mb-6">
        User Role Analytics
      </h2>

      <BarChart
        width={500}
        height={300}
        data={data}
      >

        <CartesianGrid strokeDasharray="3 3" />

        <XAxis dataKey="role" />

        <YAxis />

        <Tooltip />

        <Bar dataKey="count" fill="#2563eb" />

      </BarChart>

    </div>
  );
}

export default UserRoleChart;