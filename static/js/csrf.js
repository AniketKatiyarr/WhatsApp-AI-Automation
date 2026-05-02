window.getCookie = function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
};

window.apiFetch = async function apiFetch(url, options = {}) {
  const opts = { ...options };
  opts.headers = { ...(options.headers || {}) };
  const csrf = window.getCookie("csrftoken");
  if (csrf) opts.headers["X-CSRFToken"] = csrf;
  if (!opts.headers["Content-Type"] && opts.body) opts.headers["Content-Type"] = "application/json";
  const res = await fetch(url, opts);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) return await res.json();
  return await res.text();
};

