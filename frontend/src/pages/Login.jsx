import { useState } from "react";

import { useNavigate } from "react-router-dom";

import API from "../services/api";

function Login() {

  const navigate = useNavigate();

  const [isRegister, setIsRegister] =
    useState(false);

  const [formData, setFormData] =
    useState({
      full_name: "",
      email: "",
      password: "",
      role: "BORROWER"
    });

  // =====================================
  // HANDLE INPUT CHANGE
  // =====================================

  const handleChange = (e) => {

    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  // =====================================
  // LOGIN
  // =====================================

  const handleLogin = async () => {

    try {

      const response = await API.post(
        "/login",
        {
          email: formData.email,
          password: formData.password
        }
      );

      // STORE TOKEN
      localStorage.setItem(
        "token",
        response.data.access_token
      );

      // STORE ROLE
      localStorage.setItem(
        "role",
        response.data.role
      );

      alert("Login successful");

      // REDIRECT BASED ON ROLE
      if (
        response.data.role === "ADMIN"
      ) {

        navigate("/admin");

      } else if (
        response.data.role === "LENDER"
      ) {

        navigate("/lender");

      } else {

        navigate("/borrower");
      }

    } catch (error) {

      console.log(error);

      alert(
        error.response?.data?.detail ||
        "Login failed"
      );
    }
  };

  // =====================================
  // REGISTER
  // =====================================

  const handleRegister = async () => {

    try {

      // REGISTER USER
      await API.post(
        "/register",
        formData
      );

      // AUTO LOGIN
      const loginResponse = await API.post(
        "/login",
        {
          email: formData.email,
          password: formData.password
        }
      );

      // STORE TOKEN
      localStorage.setItem(
        "token",
        loginResponse.data.access_token
      );

      // STORE ROLE
      localStorage.setItem(
        "role",
        loginResponse.data.role
      );

      alert("Registration successful");

      // REDIRECT BASED ON ROLE
      if (
        loginResponse.data.role === "BORROWER"
      ) {

        navigate("/borrower");

      } else if (
        loginResponse.data.role === "LENDER"
      ) {

        navigate("/lender");

      } else if (
        loginResponse.data.role === "ADMIN"
      ) {

        navigate("/admin");
      }

    } catch (error) {

      console.log(error);

      alert(
        error.response?.data?.detail ||
        "Registration failed"
      );
    }
  };

  return (

    <div className="min-h-screen flex items-center justify-center bg-gray-100">

      <div className="bg-white p-10 rounded-3xl shadow-2xl w-[450px]">

        <h1 className="text-4xl font-bold text-center text-blue-700 mb-8">
          FinFlow
        </h1>

        <h2 className="text-2xl font-semibold text-center mb-8">

          {
            isRegister
            ? "Create Account"
            : "Welcome Back"
          }

        </h2>

        {/* FULL NAME */}

        {
          isRegister && (

            <input
              type="text"
              name="full_name"
              placeholder="Full Name"
              onChange={handleChange}
              className="w-full p-3 border rounded-xl mb-4"
            />

          )
        }

        {/* EMAIL */}

        <input
          type="email"
          name="email"
          placeholder="Email"
          onChange={handleChange}
          className="w-full p-3 border rounded-xl mb-4"
        />

        {/* PASSWORD */}

        <input
          type="password"
          name="password"
          placeholder="Password"
          onChange={handleChange}
          className="w-full p-3 border rounded-xl mb-4"
        />

        {/* ROLE */}

        {
          isRegister && (

            <select
              name="role"
              onChange={handleChange}
              className="w-full p-3 border rounded-xl mb-6"
            >

              <option value="BORROWER">
                Borrower
              </option>

              <option value="LENDER">
                Lender
              </option>

            </select>

          )
        }

        {/* BUTTON */}

        <button
          onClick={
            isRegister
            ? handleRegister
            : handleLogin
          }
          className="w-full bg-blue-600 text-white p-3 rounded-xl text-lg font-semibold"
        >

          {
            isRegister
            ? "Register"
            : "Login"
          }

        </button>

        {/* TOGGLE */}

        <p className="text-center mt-6">

          {
            isRegister
            ? "Already have an account?"
            : "Don't have an account?"
          }

          <span
            onClick={() =>
              setIsRegister(!isRegister)
            }
            className="text-blue-600 ml-2 cursor-pointer font-semibold"
          >

            {
              isRegister
              ? "Login"
              : "Register"
            }

          </span>

        </p>

      </div>

    </div>
  );
}

export default Login;