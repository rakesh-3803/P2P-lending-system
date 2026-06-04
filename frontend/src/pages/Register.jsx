import { useState } from "react";
import API from "../services/api";

function Register() {

  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    password: "",
    role: "BORROWER",
  });

  const handleChange = (e) => {

    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {

    e.preventDefault();

    try {

      await API.post(
        "/register",
        formData
      );

      alert("Registration Successful");

    } catch (error) {

      alert(
        error.response?.data?.detail ||
        "Registration Failed"
      );
    }
  };

  return (

    <div className="min-h-screen flex items-center justify-center bg-blue-100">

      <form
        onSubmit={handleSubmit}
        className="bg-white p-8 rounded-xl shadow-lg w-96"
      >

        <h2 className="text-3xl font-bold mb-6 text-center text-blue-600">
          Register
        </h2>

        <input
          type="text"
          name="full_name"
          placeholder="Full Name"
          className="w-full p-3 border rounded mb-4"
          onChange={handleChange}
        />

        <input
          type="email"
          name="email"
          placeholder="Email"
          className="w-full p-3 border rounded mb-4"
          onChange={handleChange}
        />

        <input
          type="password"
          name="password"
          placeholder="Password"
          className="w-full p-3 border rounded mb-4"
          onChange={handleChange}
        />

        <select
          name="role"
          className="w-full p-3 border rounded mb-4"
          onChange={handleChange}
        >
          <option value="BORROWER">
            Borrower
          </option>

          <option value="LENDER">
            Lender
          </option>
        </select>

        <button
          className="w-full bg-blue-600 text-white p-3 rounded"
        >
          Register
        </button>

      </form>

    </div>
  );
}

export default Register;