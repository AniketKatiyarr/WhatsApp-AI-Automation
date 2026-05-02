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
          const data = await window.apiFetch("/api/messages/?page_size=20");
          setRows(data.results || data);
        } catch (err) {
          setError(String(err.message || err));
        } finally {
          setLoading(false);
        }
      })();
    }, []);

    if (loading) return e("div", { className: "muted" }, "Loading...");
    if (error) return e("div", { className: "muted" }, error);

    return e(
      "table",
      null,
      e(
        "thead",
        null,
        e(
          "tr",
          null,
          e("th", null, "Phone"),
          e("th", null, "Message"),
          e("th", null, "Response"),
          e("th", null, "Time"),
          e("th", null, "Status")
        )
      ),
      e(
        "tbody",
        null,
        rows.map((r) => {
          const statusClass =
            r.status === "responded" ? "pill pill--ok" : r.status === "failed" ? "pill pill--danger" : "pill pill--warn";
          return e(
            "tr",
            { key: r.id },
            e("td", { className: "nowrap" }, r.phone),
            e("td", null, r.inbound_message),
            e("td", null, r.outbound_response || e("span", { className: "muted" }, "—")),
            e("td", { className: "nowrap muted" }, fmt(r.timestamp)),
            e("td", null, e("span", { className: statusClass }, r.status))
          );
        })
      )
    );
  }

  const rootEl = document.getElementById("recent-messages-root");
  if (rootEl) ReactDOM.createRoot(rootEl).render(e(App));
})();

