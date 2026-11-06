(function () {
  const csrfToken = document.querySelector(
    'meta[name="csrf-token"]'
  )?.content;

  const protectedMethods = new Set(["POST", "PUT", "PATCH", "DELETE"]);
  const originalFetch = window.fetch.bind(window);

  window.fetch = function (resource, options = {}) {
    const method = (
      options.method ||
      (resource instanceof Request ? resource.method : "GET")
    ).toUpperCase();

    if (!protectedMethods.has(method)) {
      return originalFetch(resource, options);
    }

    if (!csrfToken) {
      return Promise.reject(
        new Error("CSRF token is missing. Refresh the page and try again.")
      );
    }

    const headers = new Headers(options.headers);
    headers.set("X-CSRFToken", csrfToken);

    return originalFetch(resource, {
      ...options,
      headers
    });
  };
})();