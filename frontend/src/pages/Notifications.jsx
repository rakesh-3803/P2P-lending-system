import { useEffect, useState } from "react";

import Sidebar from "../components/Sidebar";

import API from "../services/api";

function Notifications() {

  const [notifications, setNotifications] =
    useState([]);

  useEffect(() => {

    fetchNotifications();

  }, []);

  const fetchNotifications = async () => {

    try {

      const response = await API.get(
        "/notifications"
      );

      setNotifications(response.data);

    } catch (error) {

      console.log(error);
    }
  };

  return (

    <div className="flex bg-gray-100 min-h-screen">

      <Sidebar />

      <div className="flex-1 p-10">

        <h1 className="text-4xl font-bold mb-10">
          Notifications
        </h1>

        <div className="space-y-4">

          {
            notifications.map((note) => (

              <div
                key={note.id}
                className="bg-white p-5 rounded-2xl shadow-lg"
              >

                <p className="text-lg">
                  {note.message}
                </p>

                <span className="text-sm text-gray-500">
                  {note.status}
                </span>

              </div>

            ))
          }

        </div>

      </div>

    </div>
  );
}

export default Notifications;