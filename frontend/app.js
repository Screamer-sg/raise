const { useState, useEffect } = React;

function fetchJSON(url, options) {
  return fetch(url, options).then((response) => {
    if (!response.ok) {
      return response.json().then((body) => Promise.reject(body.error || response.statusText));
    }
    return response.json();
  });
}

function Sidebar({ onCreate, onImport, onConvert, profiles, onSelect }) {
  const [name, setName] = useState("Нова конфігурація");
  const [model, setModel] = useState("RCMS2104");
  const [csvFile, setCsvFile] = useState(null);
  const [convertId, setConvertId] = useState("");
  const [targetModel, setTargetModel] = useState("RCMS2108");

  function handleCreate() {
    const template = {
      hostname: name.toLowerCase().replace(/\s+/g, "-"),
      model,
      management: { ip: "192.168.1.2", mask: "255.255.255.0", gateway: "192.168.1.1" },
      ports: [],
    };
    onCreate({ name, model, data: template });
  }

  function handleImport(event) {
    event.preventDefault();
    if (!csvFile) return;
    const formData = new FormData();
    formData.append("file", csvFile);
    onImport(formData).finally(() => setCsvFile(null));
  }

  function handleConvert() {
    const profile = profiles.find((item) => item.id === convertId);
    if (!profile) return;
    onConvert(profile, targetModel);
  }

  return (
    React.createElement("div", { className: "sidebar" },
      React.createElement("h1", null, "Raisecom Configurator"),
      React.createElement("p", null, "Створюйте, імпортуйте й конвертуйте конфігурації комутаторів."),
      React.createElement("label", null, "Назва профілю"),
      React.createElement("input", { value: name, onChange: (e) => setName(e.target.value) }),
      React.createElement("label", null, "Модель"),
      React.createElement("select", { value: model, onChange: (e) => setModel(e.target.value) },
        React.createElement("option", { value: "RCMS2104" }, "RCMS2104"),
        React.createElement("option", { value: "RCMS2108" }, "RCMS2108"),
      ),
      React.createElement("button", { onClick: handleCreate }, "Створити профіль"),
      React.createElement("hr"),
      React.createElement("form", { onSubmit: handleImport },
        React.createElement("label", null, "Імпорт CSV"),
        React.createElement("input", {
          type: "file",
          accept: ".csv",
          onChange: (event) => setCsvFile(event.target.files[0] ?? null),
        }),
        React.createElement("button", { type: "submit" }, "Імпортувати"),
      ),
      React.createElement("hr"),
      React.createElement("label", null, "Конвертація профілю"),
      React.createElement("select", { value: convertId, onChange: (e) => setConvertId(e.target.value) },
        React.createElement("option", { value: "" }, "Оберіть профіль"),
        profiles.map((profile) => React.createElement("option", { key: profile.id, value: profile.id }, profile.name)),
      ),
      React.createElement("select", { value: targetModel, onChange: (e) => setTargetModel(e.target.value) },
        React.createElement("option", { value: "RCMS2104" }, "RCMS2104"),
        React.createElement("option", { value: "RCMS2108" }, "RCMS2108"),
      ),
      React.createElement("button", { type: "button", onClick: handleConvert }, "Конвертувати"),
      React.createElement("hr"),
      React.createElement("label", null, "Оберіть профіль"),
      React.createElement("select", { onChange: (e) => onSelect(e.target.value) },
        React.createElement("option", { value: "" }, "--"),
        profiles.map((profile) => React.createElement("option", { key: profile.id, value: profile.id }, profile.name)),
      )
    )
  );
}

function ProfileCard({ profile, onValidate, onExport }) {
  const [portMap, setPortMap] = useState([]);
  const [exported, setExported] = useState(null);
  const [validation, setValidation] = useState(null);

  useEffect(() => {
    if (!profile) return;
    fetchJSON(`/api/configs/${profile.id}/ports`).then((data) => setPortMap(data.ports));
  }, [profile]);

  function handleValidate() {
    onValidate(profile).then((result) => setValidation(result));
  }

  function handleExport(format) {
    onExport(profile, format).then((result) => setExported(result));
  }

  if (!profile) {
    return React.createElement("p", null, "Оберіть профіль для перегляду детальної інформації.");
  }

  return (
    React.createElement("div", { className: "profile-card" },
      React.createElement("h3", null, profile.name),
      React.createElement("p", null, `Модель: ${profile.model}`),
      React.createElement("div", { className: "port-map" },
        portMap.map((port) => React.createElement("div", {
          key: port.id,
          className: "port-tile",
          style: { background: port.colour },
        },
          React.createElement("div", null, port.id),
          React.createElement("small", null, `${port.mode.toUpperCase()} VLANS: ${port.vlans.join(', ')}`),
        ))
      ),
      React.createElement("div", { className: "actions" },
        React.createElement("button", { onClick: handleValidate }, "Перевірити"),
        React.createElement("button", { onClick: () => handleExport("cli") }, "CLI"),
        React.createElement("button", { onClick: () => handleExport("cfg") }, ".cfg"),
        React.createElement("button", { onClick: () => handleExport("json") }, ".json"),
      ),
      validation && React.createElement("div", { className: "preformatted" },
        validation.valid ? "Помилок не знайдено" : validation.issues.map((issue) => `• ${issue.path}: ${issue.message}`).join("\n")
      ),
      exported && React.createElement("div", { className: "preformatted" }, exported.content)
    )
  );
}

function App() {
  const [profiles, setProfiles] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [error, setError] = useState(null);

  function loadProfiles() {
    fetchJSON("/api/configs").then((data) => setProfiles(data.profiles));
  }

  useEffect(() => {
    loadProfiles();
  }, []);

  function handleCreate(payload) {
    fetchJSON("/api/configs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then((profile) => {
        setProfiles((list) => [...list, profile]);
        setSelectedId(profile.id);
      })
      .catch(setError);
  }

  function handleImport(formData) {
    return fetch("/api/import/csv", { method: "POST", body: formData })
      .then((res) => res.json())
      .then((data) => {
        if (data.error) throw data.error;
        loadProfiles();
      })
      .catch(setError);
  }

  function handleConvert(profile, targetModel) {
    fetchJSON("/api/convert", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ config: profile.data, target_model: targetModel }),
    })
      .then((converted) => {
        const payload = { name: `${profile.name} (${targetModel})`, model: targetModel, data: converted };
        return fetchJSON("/api/configs", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      })
      .then(loadProfiles)
      .catch(setError);
  }

  function handleValidate(profile) {
    return fetchJSON("/api/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(profile.data),
    }).catch(setError);
  }

  function handleExport(profile, format) {
    return fetchJSON(`/api/configs/${profile.id}/export?format=${format}`).catch(setError);
  }

  const selectedProfile = profiles.find((item) => item.id === selectedId);

  return (
    React.createElement("div", { className: "app-shell" },
      React.createElement(Sidebar, {
        onCreate: handleCreate,
        onImport: handleImport,
        onConvert: handleConvert,
        profiles,
        onSelect: setSelectedId,
      }),
      React.createElement("main", { className: "content" },
        error && React.createElement("div", { className: "preformatted" }, `Помилка: ${error}`),
        React.createElement("section", { className: "profile-list" },
          React.createElement(ProfileCard, {
            key: selectedProfile ? selectedProfile.id : "placeholder",
            profile: selectedProfile,
            onValidate: handleValidate,
            onExport: handleExport,
          }),
        ),
      ),
    )
  );
}

ReactDOM.createRoot(document.getElementById("app")).render(React.createElement(App));

