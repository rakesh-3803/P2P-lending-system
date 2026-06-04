import { useEffect, useState } from "react";

import Sidebar from "../components/Sidebar";
import AnalyticsCard from "../components/AnalyticsCard";
import AdminLoanTable from "../components/AdminLoanTable";
import UsersTable from "../components/UsersTable";

import API from "../services/api";
import LoanStatusChart from "../components/LoanStatusChart";
import UserRoleChart from "../components/UserRoleChart";

function AdminDashboard() {

  const [users, setUsers] = useState([]);

  const [loans, setLoans] = useState([]);

  useEffect(() => {

    fetchUsers();

    fetchLoans();

  }, []);

  const fetchUsers = async () => {

    try {

      const response = await API.get(
        "/admin/users"
      );

      setUsers(response.data);

    } catch (error) {

      console.log(error);
    }
  };

  const fetchLoans = async () => {

    try {

      const response = await API.get(
        "/admin/loans"
      );

      setLoans(response.data);

    } catch (error) {

      console.log(error);
    }
  };

  return (

    <div className="flex bg-gray-100 min-h-screen">

      <Sidebar />

      <div className="flex-1 p-10">

        <h1 className="text-4xl font-bold text-red-700 mb-10">
          Admin Dashboard
        </h1>

        {/* Analytics Cards */}

        <div className="grid grid-cols-3 gap-6 mb-10">

          <AnalyticsCard
            title="Total Users"
            value={users.length}
            color="bg-blue-600"
          />

          <AnalyticsCard
            title="Total Loans"
            value={loans.length}
            color="bg-green-600"
          />

          <AnalyticsCard
            title="Pending Loans"
            value={
              loans.filter(
                (loan) =>
                  loan.status === "PENDING"
              ).length
            }
            color="bg-yellow-500"
          />

        </div>

        <div className="grid grid-cols-2 gap-6 mb-10">

          <LoanStatusChart loans={loans} />

          <UserRoleChart users={users} />

        </div>

        {/* Loan Table */}

        <h2 className="text-3xl font-bold mb-6">
          Loan Management
        </h2>

        <AdminLoanTable
          loans={loans}
          refreshLoans={fetchLoans}
        />

        {/* Users Table */}

        <h2 className="text-3xl font-bold mt-12 mb-6">
          Users
        </h2>

        <UsersTable users={users} />

      </div>

    </div>
  );
}

export default AdminDashboard;