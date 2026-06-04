function AnalyticsCard({
  title,
  value,
  color
}) {

  return (

    <div className={`p-6 rounded-2xl shadow-lg text-white ${color}`}>

      <h2 className="text-xl font-semibold">
        {title}
      </h2>

      <h1 className="text-4xl font-bold mt-4">
        {value}
      </h1>

    </div>
  );
}

export default AnalyticsCard;