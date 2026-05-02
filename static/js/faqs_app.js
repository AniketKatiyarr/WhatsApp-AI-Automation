(() => {
  const e = React.createElement;

  function App() {
    const [faqs, setFaqs] = React.useState([]);
    const [q, setQ] = React.useState("");
    const [a, setA] = React.useState("");
    const [error, setError] = React.useState("");
    const [loading, setLoading] = React.useState(true);

    async function load() {
      setLoading(true);
      setError("");
      try {
        const data = await window.apiFetch("/api/faqs/");
        setFaqs(data.results || data);
      } catch (err) {
        setError(String(err.message || err));
      } finally {
        setLoading(false);
      }
    }

    React.useEffect(() => {
      load();
    }, []);

    async function createFaq(ev) {
      ev.preventDefault();
      setError("");
      try {
        await window.apiFetch("/api/faqs/", { method: "POST", body: JSON.stringify({ question: q, answer: a }) });
        setQ("");
        setA("");
        await load();
      } catch (err) {
        setError(String(err.message || err));
      }
    }

    async function delFaq(id) {
      if (!confirm("Delete this FAQ?")) return;
      setError("");
      try {
        await window.apiFetch(`/api/faqs/${id}/`, { method: "DELETE" });
        await load();
      } catch (err) {
        setError(String(err.message || err));
      }
    }

    return e(
      "div",
      null,
      e(
        "form",
        { className: "form", onSubmit: createFaq },
        e("label", null, "Question"),
        e("input", { value: q, onChange: (ev) => setQ(ev.target.value), placeholder: "e.g., What are your opening hours?" }),
        e("label", null, "Answer"),
        e("textarea", { value: a, onChange: (ev) => setA(ev.target.value), rows: 4, placeholder: "Your answer..." }),
        e("button", { className: "btn btn--primary", type: "submit" }, "Add FAQ")
      ),
      error ? e("p", { className: "muted" }, error) : null,
      loading
        ? e("p", { className: "muted" }, "Loading...")
        : e(
            "table",
            null,
            e("thead", null, e("tr", null, e("th", null, "Question"), e("th", null, "Answer"), e("th", null, ""))),
            e(
              "tbody",
              null,
              faqs.map((f) =>
                e(
                  "tr",
                  { key: f.id },
                  e("td", null, f.question),
                  e("td", null, f.answer),
                  e("td", null, e("button", { className: "btn btn--sm", type: "button", onClick: () => delFaq(f.id) }, "Delete"))
                )
              )
            )
          )
    );
  }

  const rootEl = document.getElementById("faqs-root");
  if (rootEl) ReactDOM.createRoot(rootEl).render(e(App));
})();

