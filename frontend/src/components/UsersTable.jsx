function UsersTable({ users }) {

  return (

    <div className="bg-white rounded-2xl shadow-lg p-6 overflow-x-auto">

      <table className="w-full">

        <thead>

          <tr className="border-b">

            <th className="text-left p-3">
              ID
            </th>

            <th className="text-left p-3">
              Name
            </th>

            <th className="text-left p-3">
              Email
            </th>

            <th className="text-left p-3">
              Role
            </th>

          </tr>

        </thead>

        <tbody>

          {
            users.map((user) => (

              <tr
                key={user.id}
                className="border-b"
              >

                <td className="p-3">
                  {user.id}
                </td>

                <td className="p-3">
                  {user.full_name}
                </td>

                <td className="p-3">
                  {user.email}
                </td>

                <td className="p-3">
                  {user.role}
                </td>

              </tr>

            ))
          }

        </tbody>

      </table>

    </div>
  );
}

export default UsersTable;