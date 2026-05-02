(() => {
  const e = React.createElement;

  function fmt(ts) {
    try {
      return new Date(ts).toLocaleString();
    } catch {
      return ts;
    }
  }

  function App() {
    const [rows, setRows] = React.useState([]);
    const [error, setError] = React.useState("");
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
      (async () => {
        try {
          const data = await window.apiFetch("/api/leads/?page_size=50");
          setRows(data.results || data);
        } catch (err) {
          setError(String(err.message || err));
        } finally {
          setLoading(false);
        }
      })();
    }, []);

    if (loading) return e("p", { className: "muted" }, "Loading...");
    if (error) return e("p", { className: "muted" }, error);

    return e(
      "table",
      null,
      e("thead", null, e("tr", null, e("th", null, "Name"), e("th", null, "Phone"), e("th", null, "Interest"), e("th", null, "Intent"), e("th", null, "Created"))),
      e(
        "tbody",
        null,
        rows.map((r) =>
          e(
            "tr",
            { key: r.id },
            e("td", null, r.name || "—"),
            e("td", { className: "nowrap" }, r.phone || "—"),
            e("td", null, r.interest || "—"),
            e("td", null, e("span", { className: "pill pill--ok" }, r.intent || "—")),
            e("td", { className: "nowrap muted" }, fmt(r.created_at))
          )
        )
      )
    );
  }

  const rootEl = document.getElementById("leads-root");
  if (rootEl) ReactDOM.createRoot(rootEl).render(e(App));
})();

