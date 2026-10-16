/* ==========================================================================
   QC101 -- interactive widgets
   Pure JavaScript, no dependencies, no build step.

   Every widget is a factory that returns an HTMLElement, so the app can
   drop them into a page without any templating engine.
   ========================================================================== */
(function (global) {
  "use strict";

  /* ------------------------------------------------------------ helpers */
  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (key) {
        if (key === "class") node.className = attrs[key];
        else if (key === "html") node.innerHTML = attrs[key];
        else if (key === "text") node.textContent = attrs[key];
        else if (key.slice(0, 2) === "on") node.addEventListener(key.slice(2), attrs[key]);
        else if (attrs[key] !== null && attrs[key] !== undefined) node.setAttribute(key, attrs[key]);
      });
    }
    (children || []).forEach(function (child) {
      if (child === null || child === undefined) return;
      node.appendChild(typeof child === "string" ? document.createTextNode(child) : child);
    });
    return node;
  }

  function card(title, note, bodyNodes) {
    return el("div", { class: "widget" }, [
      el("div", { class: "widget-title", text: title }),
      note ? el("div", { class: "widget-note", text: note }) : null
    ].concat(bodyNodes || []));
  }

  function statTile(label, value, kind) {
    return el("div", { class: "stat" + (kind ? " " + kind : "") }, [
      el("div", { class: "stat-label", text: label }),
      el("div", { class: "stat-value", text: value })
    ]);
  }

  function barRow(label, value, max, color) {
    var fill = el("div", { class: "bar-fill" });
    fill.style.width = (max > 0 ? (value / max) * 100 : 0) + "%";
    if (color) fill.style.background = color;
    return el("div", { class: "bar-row" }, [
      el("div", { class: "bar-label", text: label }),
      el("div", { class: "bar" }, [fill]),
      el("div", { class: "bar-value", text: value.toFixed(3) })
    ]);
  }

  function fmt(value, digits) {
    if (typeof value !== "number" || !isFinite(value)) return "—";
    if (Math.abs(value) < 1e-12) return "0";
    return value.toFixed(digits === undefined ? 4 : digits);
  }

  function complexText(re, im) {
    if (Math.abs(im) < 1e-12) return fmt(re, 4);
    if (Math.abs(re) < 1e-12) return (im < 0 ? "-" : "") + fmt(Math.abs(im), 4) + "i";
    return fmt(re, 4) + (im < 0 ? " - " : " + ") + fmt(Math.abs(im), 4) + "i";
  }

  /* ====================================================== Bloch sphere === */
  function blochCanvas(state, size) {
    var canvas = el("canvas", { width: size * 2, height: size * 2,
                                style: "width:" + size + "px;height:" + size + "px" });
    canvas.width = size * 2;
    canvas.height = size * 2;
    var ctx = canvas.getContext("2d");
    var scale = 2;

    function project(x, y, z) {
      // simple isometric projection
      var px = (x - y) * 0.866;
      var py = (x + y) * 0.5 - z;
      return [size * scale / 2 + px * size * scale * 0.42,
              size * scale / 2 + py * size * scale * 0.42];
    }

    function draw() {
      var w = size * scale, h = size * scale;
      ctx.clearRect(0, 0, w, h);
      var style = getComputedStyle(document.body);
      var line = style.getPropertyValue("--border").trim() || "#333";
      var textDim = style.getPropertyValue("--text-dim").trim() || "#888";

      // axes
      ctx.lineWidth = 2;
      var axes = [[1, 0, 0, "|0>", "x"], [0, 1, 0, "|1>", "y"], [0, 0, 1, "z", "z"]];
      ctx.strokeStyle = line;
      ctx.fillStyle = textDim;
      ctx.font = (13 * scale) + "px monospace";
      axes.forEach(function (axis) {
        var a = project(-axis[0], -axis[1], -axis[2]);
        var b = project(axis[0], axis[1], axis[2]);
        ctx.beginPath();
        ctx.moveTo(a[0], a[1]);
        ctx.lineTo(b[0], b[1]);
        ctx.stroke();
        var label = project(axis[0] * 1.22, axis[1] * 1.22, axis[2] * 1.22);
        ctx.fillText(axis[3], label[0] - 6 * scale, label[1] + 4 * scale);
      });

      // equator
      ctx.strokeStyle = line;
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (var i = 0; i <= 64; i++) {
        var t = (i / 64) * 2 * Math.PI;
        var p = project(Math.cos(t), Math.sin(t), 0);
        if (i === 0) ctx.moveTo(p[0], p[1]); else ctx.lineTo(p[0], p[1]);
      }
      ctx.stroke();

      // state vector
      var s = project(state.x, state.y, state.z);
      var origin = project(0, 0, 0);
      ctx.strokeStyle = "#58a6ff";
      ctx.lineWidth = 3 * scale;
      ctx.beginPath();
      ctx.moveTo(origin[0], origin[1]);
      ctx.lineTo(s[0], s[1]);
      ctx.stroke();

      // the tip
      ctx.fillStyle = "#58a6ff";
      ctx.beginPath();
      ctx.arc(s[0], s[1], 6 * scale, 0, 2 * Math.PI);
      ctx.fill();

      // projection marker
      var shadow = project(state.x, state.y, 0);
      ctx.fillStyle = "rgba(126,231,135,0.75)";
      ctx.beginPath();
      ctx.arc(shadow[0], shadow[1], 4 * scale, 0, 2 * Math.PI);
      ctx.fill();
    }

    draw();
    return { canvas: canvas, draw: draw };
  }

  function blochWidget() {
    var state = { theta: Math.PI / 2, phi: 0 };
    var size = 210;

    function amplitudes() {
      var alpha = Math.cos(state.theta / 2);
      var beta = { re: Math.sin(state.theta / 2) * Math.cos(state.phi),
                   im: Math.sin(state.theta / 2) * Math.sin(state.phi) };
      return { alpha: alpha, beta: beta };
    }

    function vector() {
      return {
        x: Math.sin(state.theta) * Math.cos(state.phi),
        y: Math.sin(state.theta) * Math.sin(state.phi),
        z: Math.cos(state.theta)
      };
    }

    var info = el("div", { class: "kv" });
    var canvasBox = el("div");

    function refresh() {
      var amps = amplitudes();
      var p0 = amps.alpha * amps.alpha;
      var p1 = amps.beta.re * amps.beta.re + amps.beta.im * amps.beta.im;
      info.innerHTML =
        "<table>" +
        "<tr><td>|0&gt; amplitude</td><td>" + fmt(amps.alpha, 4) + "</td></tr>" +
        "<tr><td>|1&gt; amplitude</td><td>" + complexText(amps.beta.re, amps.beta.im) + "</td></tr>" +
        "<tr><td>P(0)</td><td>" + fmt(p0, 4) + "</td></tr>" +
        "<tr><td>P(1)</td><td>" + fmt(p1, 4) + "</td></tr>" +
        "<tr><td>theta</td><td>" + fmt(state.theta * 180 / Math.PI, 1) + "&deg;</td></tr>" +
        "<tr><td>phi</td><td>" + fmt(state.phi * 180 / Math.PI, 1) + "&deg;</td></tr>" +
        "</table>";
      var bars = el("div", { style: "margin-top:10px" }, [
        barRow("P(0)", p0, 1, "var(--accent)"),
        barRow("P(1)", p1, 1, "var(--accent-2)")
      ]);
      info.appendChild(bars);
      bloch.draw();
    }

    var bloch = blochCanvas(vector(), size);
    canvasBox.appendChild(bloch.canvas);

    // dragging
    var dragging = false, lastX = 0, lastY = 0;
    bloch.canvas.addEventListener("pointerdown", function (event) {
      dragging = true; lastX = event.clientX; lastY = event.clientY;
      bloch.canvas.setPointerCapture(event.pointerId);
    });
    bloch.canvas.addEventListener("pointermove", function (event) {
      if (!dragging) return;
      var dx = event.clientX - lastX, dy = event.clientY - lastY;
      lastX = event.clientX; lastY = event.clientY;
      state.phi += dx * 0.01;
      state.theta = Math.max(0, Math.min(Math.PI, state.theta - dy * 0.01));
      refresh();
    });
    ["pointerup", "pointercancel", "pointerleave"].forEach(function (name) {
      bloch.canvas.addEventListener(name, function () { dragging = false; });
    });

    var thetaSlider = el("input", { type: "range", min: "0", max: "180", value: "90",
                                     oninput: function () {
                                       state.theta = (+this.value) * Math.PI / 180;
                                       refresh();
                                     } });
    var phiSlider = el("input", { type: "range", min: "-180", max: "180", value: "0",
                                   oninput: function () {
                                     state.phi = (+this.value) * Math.PI / 180;
                                     refresh();
                                   } });

    var body = [
      el("div", { class: "grid-2" }, [
        el("div", {}, [canvasBox]),
        el("div", {}, [info])
      ]),
      el("div", { style: "margin-top:12px" }, [
        el("label", { text: "theta (polar angle)" }), thetaSlider,
        el("label", { text: "phi (azimuth)" }), phiSlider
      ])
    ];

    refresh();
    return card("The Bloch sphere", "Drag the sphere, or use the sliders. " +
      "The state is |psi> = cos(theta/2)|0> + e^{i phi} sin(theta/2)|1>.", body);
  }

  /* ================================================== gate playground === */
  var GATES = {
    I: { name: "I", matrix: [[1, 0], [0, 1]], label: "identity" },
    H: { name: "H", matrix: [[1 / Math.SQRT2, 1 / Math.SQRT2], [1 / Math.SQRT2, -1 / Math.SQRT2]],
         label: "Hadamard" },
    X: { name: "X", matrix: [[0, 1], [1, 0]], label: "Pauli X (bit flip)" },
    Y: { name: "Y", matrix: [[0, -1], [1, 0]], label: "Pauli Y" },
    Z: { name: "Z", matrix: [[1, 0], [0, -1]], label: "Pauli Z (phase flip)" },
    S: { name: "S", matrix: [[1, 0], [0, 1]], label: "S (phase pi/2)" },
    T: { name: "T", matrix: [[1, 0], [0, 1]], label: "T (phase pi/4)" }
  };
  GATES.S.matrix = [[1, 0], [0, { re: 0, im: 1 }]];
  GATES.T.matrix = [[1, 0], [0, { re: Math.SQRT1_2, im: Math.SQRT1_2 }]];

  function mul2x2(m, v) {
    return [
      { re: m[0][0] * v[0].re - m[0][1] * v[1].im,
        im: m[0][0] * v[0].im + m[0][1] * v[1].re },
      { re: m[1][0] * v[0].re - m[1][1] * v[1].im,
        im: m[1][0] * v[0].im + m[1][1] * v[1].re }
    ];
  }

  function gateWidget() {
    var alpha = { re: 1, im: 0 };
    var beta = { re: 0, im: 0 };
    var history = [];

    var stateBox = el("div", { class: "kv" });
    var matrixBox = el("div", { class: "kv" });
    var buttons = el("div", { class: "btn-row" });

    function vector() {
      var v = { x: 2 * alpha.re * beta.re + 2 * alpha.im * beta.im,
                y: 2 * (alpha.re * beta.im - alpha.im * beta.re),
                z: alpha.re * alpha.re + alpha.im * alpha.im - beta.re * beta.re - beta.im * beta.im };
      return v;
    }

    var bloch = blochCanvas(vector(), 190);
    var blochBox = el("div", {}, [bloch.canvas]);

    function refresh() {
      var p0 = alpha.re * alpha.re + alpha.im * alpha.im;
      var p1 = beta.re * beta.re + beta.im * beta.im;
      stateBox.innerHTML =
        "<table>" +
        "<tr><td>|psi&gt;</td><td>" + complexText(alpha.re, alpha.im) + " |0&gt; + " +
        complexText(beta.re, beta.im) + " |1&gt;</td></tr>" +
        "<tr><td>P(0)</td><td>" + fmt(p0, 4) + "</td></tr>" +
        "<tr><td>P(1)</td><td>" + fmt(p1, 4) + "</td></tr>" +
        "</table>";
      stateBox.appendChild(el("div", { style: "margin-top:8px" }, [
        barRow("P(0)", p0, 1, "var(--accent)"),
        barRow("P(1)", p1, 1, "var(--accent-2)")
      ]));

      var rows = history.map(function (name) {
        return "<tr><td>" + name + "</td></tr>";
      }).join("");
      matrixBox.innerHTML = "<table><tr><td>applied</td><td>" +
        (history.length ? history.join(" &rarr; ") : "—") + "</td></tr></table>";
      bloch.draw();
    }

    function apply(name) {
      var gate = GATES[name];
      var before = { a: { re: alpha.re, im: alpha.im }, b: { re: beta.re, im: beta.im } };
      var out = mul2x2(gate.matrix, { re: before.a.re, im: before.a.im,
                                      re2: 0, im2: 0 });
      // multiply by hand so the complex gate entries work
      var m = gate.matrix;
      var v = [{ re: before.a.re, im: before.a.im }, { re: before.b.re, im: before.b.im }];
      function mulEntry(mij, vec) {
        if (typeof mij === "number") {
          return { re: mij * vec.re, im: mij * vec.im };
        }
        return { re: mij.re * vec.re - mij.im * vec.im, im: mij.re * vec.im + mij.im * vec.re };
      }
      var res = [
        { re: mulEntry(m[0][0], v[0]).re + mulEntry(m[0][1], v[1]).re,
          im: mulEntry(m[0][0], v[0]).im + mulEntry(m[0][1], v[1]).im },
        { re: mulEntry(m[1][0], v[0]).re + mulEntry(m[1][1], v[1]).re,
          im: mulEntry(m[1][0], v[0]).im + mulEntry(m[1][1], v[1]).im }
      ];
      alpha = res[0];
      beta = res[1];
      history.push(name);
      refresh();
    }

    Object.keys(GATES).forEach(function (name) {
      buttons.appendChild(el("button", {
        class: "btn small", text: name,
        title: GATES[name].label,
        onclick: function () { apply(name); }
      }));
    });
    buttons.appendChild(el("button", {
      class: "btn ghost small", text: "reset",
      onclick: function () {
        alpha = { re: 1, im: 0 }; beta = { re: 0, im: 0 }; history = []; refresh();
      }
    }));

    refresh();
    return card("Gate playground", "Start in |0> and apply gates. The state " +
      "vector, the measurement probabilities and the Bloch sphere all update live.", [
      el("div", { class: "grid-2" }, [
        el("div", {}, [blochBox]),
        el("div", {}, [stateBox, matrixBox])
      ]),
      buttons
    ]);
  }

  /* ================================================== Malus / polarizer == */
  function polarizerWidget() {
    var thetaP = 0, thetaF = 45, mode = "quantum";
    var output = el("div");

    function malus(tp, tf) {
      var d = (tp - tf) * Math.PI / 180;
      return Math.cos(d) * Math.cos(d);
    }

    function refresh() {
      var p = malus(thetaP, thetaF);
      var rows = [
        el("div", { class: "stat-grid" }, [
          statTile("P(pass)", fmt(p, 4), p > 0.9 ? "good" : (p < 0.1 ? "bad" : "warn")),
          statTile("P(block)", fmt(1 - p, 4)),
          statTile("angle diff", fmt(thetaP - thetaF, 0) + "°")
        ]),
        el("div", { style: "margin-top:12px" }, [
          barRow("pass", p, 1, "var(--accent-2)"),
          barRow("block", 1 - p, 1, "var(--danger)")
        ])
      ];

      // the cascade
      var angles = [thetaP, thetaF];
      var cascade = el("table", {}, []);
      var head = el("tr", {}, [el("th", { text: "stage" }), el("th", { text: "axis" }),
                               el("th", { text: "P(pass | so far)" })]);
      cascade.appendChild(head);
      var current = 0;
      for (var i = 0; i < angles.length; i++) {
        var step = malus(current, angles[i]);
        current = current + 0;  // keep the axis
        cascade.appendChild(el("tr", {}, [
          el("td", { text: i === 0 ? "input" : "polarizer " + i }),
          el("td", { text: angles[i] + "°" }),
          el("td", { text: i === 0 ? "1.000" : fmt(step, 4) })
        ]));
        if (i > 0) current = angles[i];
      }
      rows.push(el("div", { class: "kv", style: "margin-top:14px" }, [cascade]));

      if (mode === "quantum") {
        rows.push(el("div", { class: "widget-note", style: "margin-top:10px",
          html: "In the quantum model the photon is found in one definite " +
                "polarization; in the classical model the intensity is split " +
                "between the two directions. The numbers agree — the " +
                "mechanism does not." }));
      } else {
        rows.push(el("div", { class: "widget-note", style: "margin-top:10px",
          html: "The classical model keeps both components and adds their " +
                "intensities. The quantum model collapses to a single one." }));
      }
      output.innerHTML = "";
      rows.forEach(function (node) { output.appendChild(node); });
    }

    var pSlider = el("input", { type: "range", min: "-90", max: "90", value: "0",
      oninput: function () { thetaP = (+this.value); refresh(); } });
    var fSlider = el("input", { type: "range", min: "-90", max: "90", value: "45",
      oninput: function () { thetaF = (+this.value); refresh(); } });

    var body = [
      el("div", { class: "grid-2" }, [
        el("div", {}, [
          el("label", { text: "input polarization theta_p: " + thetaP + "°" }), pSlider,
          el("label", { text: "polarizer axis theta_f: " + thetaF + "°" }), fSlider
        ]),
        output
      ])
    ];
    refresh();
    return card("Malus's law", "P(pass) = cos^2(theta_p - theta_f). " +
      "Slide the angles and watch the probability move.", body);
  }

  /* ==================================================== BB84 simulator === */
  function bb84Widget() {
    var rounds = 200, eveMode = "none", result = null;

    var output = el("div");

    function randomBit() { return Math.random() < 0.5 ? 0 : 1; }

    // The polarization model used by the qc101 library: a photon has an
    // angle, and measuring it in a basis whose axis differs gives a random
    // outcome with probability cos^2(delta).
    function basisAngle(basis, bit) {
      if (basis === 0) return bit === 0 ? 0 : 90;
      return bit === 0 ? 45 : 135;
    }

    function measure(angle, basis) {
      var axis = basisAngle(basis, 0);
      var delta = (angle - axis) * Math.PI / 180;
      var pZero = Math.cos(delta) * Math.cos(delta);
      return Math.random() < pZero ? 0 : 1;
    }

    function run() {
      var aliceKey = [], bobKey = [], errors = 0, sifted = 0;
      for (var i = 0; i < rounds; i++) {
        var bit = randomBit();
        var aliceBasis = randomBit();
        var angle = basisAngle(aliceBasis, bit);
        var bobBasis = randomBit();

        if (eveMode !== "none") {
          var eveBasis = randomBit();
          var eveBit = measure(angle, eveBasis);
          var resendBasis = eveMode === "same" ? eveBasis : randomBit();
          angle = basisAngle(resendBasis, eveBit);
        }

        var bobBit = measure(angle, bobBasis);
        if (aliceBasis === bobBasis) {
          sifted++;
          aliceKey.push(bit);
          bobKey.push(bobBit);
          if (bit !== bobBit) errors++;
        }
      }
      result = {
        sifted: sifted,
        errors: errors,
        qber: sifted ? errors / sifted : 0,
        alice: aliceKey.slice(0, 24).join(""),
        bob: bobKey.slice(0, 24).join("")
      };
      refresh();
    }

    function refresh() {
      output.innerHTML = "";
      if (!result) return;
      output.appendChild(el("div", { class: "stat-grid" }, [
        statTile("rounds", String(rounds)),
        statTile("sifted", String(result.sifted)),
        statTile("QBER", (result.qber * 100).toFixed(1) + "%",
                 result.qber > 0.11 ? "bad" : "good"),
        statTile("errors", String(result.errors))
      ]));
      output.appendChild(el("div", { class: "kv", style: "margin-top:12px" }, [
        el("div", { text: "Alice: " + (result.alice || "—") }),
        el("div", { text: "Bob  : " + (result.bob || "—") })
      ]));
      var verdict = result.qber === 0
        ? "Perfect: no eavesdropper detected."
        : (result.qber > 0.11
            ? "Abort! The error rate is above the 11% threshold."
            : "Suspicious, but below the abort threshold.");
      output.appendChild(el("div", { class: "widget-note", style: "margin-top:8px",
                                     text: verdict }));
    }

    var modeSelect = el("select", { onchange: function () { eveMode = this.value; } }, [
      el("option", { value: "none", text: "No eavesdropper" }),
      el("option", { value: "same", text: "Eve: resend in the basis she measured in (25% QBER)" }),
      el("option", { value: "random", text: "Eve: resend in a random basis (37.5% QBER)" })
    ]);

    var body = [
      el("div", { class: "btn-row" }, [
        el("label", { text: "eavesdropper: " }), modeSelect,
        el("label", { text: "rounds: " }),
        el("input", { type: "number", value: "200", min: "10", max: "5000",
                      onchange: function () { rounds = Math.max(10, Math.min(5000, (+this.value) || 200)); } }),
        el("button", { class: "btn", text: "Run the protocol", onclick: run })
      ]),
      output
    ];
    run();
    return card("BB84 in your browser", "Every random choice is made with " +
      "Math.random(); the protocol itself is the one from the course.  Expect " +
      "0% with no eavesdropper, 25% for the textbook intercept-resend attack, " +
      "and 37.5% when Eve resends in a random basis.  Raise the round count " +
      "to see the averages settle.", body);
  }

  /* ================================================ entanglement / Bell === */
  function bellWidget() {
    var sameBasis = true;
    var output = el("div");

    function refresh() {
      var outcomes;
      if (sameBasis) {
        outcomes = [["00", 0.5], ["01", 0], ["10", 0], ["11", 0.5]];
      } else {
        outcomes = [["00", 0.25], ["01", 0.25], ["10", 0.25], ["11", 0.25]];
      }
      output.innerHTML = "";
      var table = el("table", {});
      table.appendChild(el("tr", {}, [el("th", { text: "outcome" }),
                                      el("th", { text: "probability" })]));
      outcomes.forEach(function (pair) {
        table.appendChild(el("tr", {}, [
          el("td", { class: "mono", text: pair[0] }),
          el("td", { text: pair[1].toFixed(2) })
        ]));
      });
      output.appendChild(el("div", { class: "grid-2" }, [
        el("div", {}, [table]),
        el("div", { class: "widget-note", html: sameBasis
          ? "Same basis: only <code>00</code> and <code>11</code> occur. The " +
            "correlation is perfect — this is the resource BB84 and teleportation use."
          : "Different bases: all four outcomes are equally likely. The " +
            "correlation is gone, and with it any ability to send information." })
      ]));
    }

    var toggle = el("button", {
      class: "btn", text: "Switch the measurement basis",
      onclick: function () { sameBasis = !sameBasis; refresh(); }
    });

    refresh();
    return card("The Bell pair", "Measured on |Phi+> = (|00> + |11>)/sqrt(2). " +
      "Compare the two bases.", [output, el("div", { class: "btn-row" }, [toggle])]);
  }

  /* =================================================== quantum KNN demo === */
  function knnWidget() {
    var training = [[0.9798, 0.2, 1], [0.3, 0.954, 0]];
    var query = [0.85, 0.5268];
    var output = el("div");

    function normalize(v) {
      var n = Math.sqrt(v[0] * v[0] + v[1] * v[1]);
      return [v[0] / n, v[1] / n];
    }

    function refresh() {
      var vectors = training.map(function (t) { return normalize(t); });
      var q = normalize(query);
      var weights = vectors.map(function (v) {
        var d2 = (q[0] - v[0]) * (q[0] - v[0]) + (q[1] - v[1]) * (q[1] - v[1]);
        return { d2: d2, w: 1 - 0.25 * d2 };
      });
      var total = weights.reduce(function (s, x) { return s + x.w; }, 0);
      var classical = weights.map(function (x) { return x.w / total; });

      // the quantum answer: sum (v_i + q_i)^2 per class, normalised
      var quantum = [0, 0];
      vectors.forEach(function (v, i) {
        var s = 0;
        for (var k = 0; k < 2; k++) s += Math.pow(v[k] + q[k], 2);
        quantum[training[i][2]] += s;
      });
      var qtotal = quantum[0] + quantum[1];
      quantum = quantum.map(function (x) { return x / qtotal; });

      output.innerHTML = "";
      output.appendChild(el("div", { class: "stat-grid" }, [
        statTile("P(class 1) classical", fmt(classical[0], 4)),
        statTile("P(class 1) quantum", fmt(quantum[0], 4), "good"),
        statTile("difference", fmt(Math.abs(classical[0] - quantum[0]), 6))
      ]));
      var table = el("table", {});
      table.appendChild(el("tr", {}, [el("th", { text: "training point" }),
                                      el("th", { text: "class" }),
                                      el("th", { text: "d^2" }),
                                      el("th", { text: "w = 1 - 0.25 d^2" })]));
      weights.forEach(function (x, i) {
        table.appendChild(el("tr", {}, [
          el("td", { text: "#" + i }),
          el("td", { text: String(training[i][2]) }),
          el("td", { text: fmt(x.d2, 6) }),
          el("td", { text: fmt(x.w, 6) })
        ]));
      });
      output.appendChild(el("div", { class: "kv", style: "margin-top:12px" }, [table]));
      output.appendChild(el("div", { class: "widget-note", style: "margin-top:10px",
        html: "The quantum value is computed from the interference amplitudes: " +
              "&Sigma;(v<sub>i</sub> + q<sub>i</sub>)<sup>2</sup> = 4w<sub>i</sub>, " +
              "so the two agree exactly. Try changing the query below." }));
    }

    var qx = el("input", { type: "number", value: "0.85", step: "0.01",
      onchange: function () { query[0] = (+this.value) || 0; refresh(); } });
    var qy = el("input", { type: "number", value: "0.5268", step: "0.01",
      onchange: function () { query[1] = (+this.value) || 0; refresh(); } });

    refresh();
    return card("Quantum KNN vs classical KNN", "The course's own data, " +
      "computed both ways. Change the query and watch both answers move together.", [
      el("div", { class: "btn-row" }, [
        el("label", { text: "query x: " }), qx,
        el("label", { text: "query y: " }), qy
      ]),
      output
    ]);
  }

  /* ================================================== two-qubit circuit === */
  function twoQubitWidget() {
    var output = el("div");

    var GATES_1Q = {
      I: [[1, 0], [0, 1]],
      H: [[1 / Math.SQRT2, 1 / Math.SQRT2], [1 / Math.SQRT2, -1 / Math.SQRT2]],
      X: [[0, 1], [1, 0]],
      Z: [[1, 0], [0, -1]]
    };

    function apply1Q(m, v) {
      // v = [a, b] complex pairs
      return [
        { re: m[0][0] * v[0].re - m[0][1] * v[1].im, im: m[0][0] * v[0].im + m[0][1] * v[1].re },
        { re: m[1][0] * v[0].re - m[1][1] * v[1].im, im: m[1][0] * v[0].im + m[1][1] * v[1].re }
      ];
    }

    function cnot(v) {
      // little-endian index = q0 + 2*q1 ; CNOT with q0 control, q1 target
      var out = [v[0], v[1], v[2], v[3]].map(function (c) {
        return { re: c.re, im: c.im };
      });
      // |10> (index 2) <-> |11> (index 3)
      var tmp = out[2]; out[2] = out[3]; out[3] = tmp;
      return out;
    }

    function refresh() {
      var v = [
        { re: 1, im: 0 }, { re: 0, im: 0 }, { re: 0, im: 0 }, { re: 0, im: 0 }
      ];
      v = apply1Q(GATES_1Q.H, v.slice(0, 2));
      v = v.concat([{ re: 0, im: 0 }, { re: 0, im: 0 }]);
      v = cnot(v);
      output.innerHTML = "";
      var table = el("table", {});
      table.appendChild(el("tr", {}, [el("th", { text: "basis (q1 q0)" }),
                                      el("th", { text: "amplitude" }),
                                      el("th", { text: "probability" })]));
      v.forEach(function (c, index) {
        var bitstring = ("00" + index.toString(2)).slice(-2);
        table.appendChild(el("tr", {}, [
          el("td", { class: "mono", text: bitstring }),
          el("td", { class: "mono", text: complexText(c.re, c.im) }),
          el("td", { text: fmt(c.re * c.re + c.im * c.im, 4) })
        ]));
      });
      output.appendChild(el("div", { class: "kv" }, [table]));
      output.appendChild(el("div", { class: "widget-note", style: "margin-top:10px",
        html: "A Bell state: H on q0 then CNOT with q0 as the control. Only " +
              "<code>00</code> and <code>11</code> occur, each with probability ½." }));
    }

    refresh();
    return card("Bell state, step by step", "The circuit from lab L11, with " +
      "the state after every stage.", [output]);
  }

  /* ====================================================== QFT / period === */
  function periodWidget() {
    var output = el("div");
    var m = 4, r = 4;

    function refresh() {
      var peaks = [];
      for (var k = 0; k * (1 << m) / r < (1 << m); k++) {
        peaks.push(k * (1 << m) / r);
      }
      var counts = {};
      peaks.forEach(function (p) { counts[p] = 1; });
      output.innerHTML = "";
      output.appendChild(el("div", { class: "stat-grid" }, [
        statTile("counting qubits m", String(m)),
        statTile("period r", String(r)),
        statTile("2^m / r", String((1 << m) / r)),
        statTile("peaks", peaks.join(", "))
      ]));
      output.appendChild(el("div", { class: "widget-note", style: "margin-top:12px",
        html: "Shor's period finding lands the measurement on multiples of " +
              "2<sup>m</sup>/r. The continued-fraction expansion of " +
              "y/2<sup>m</sup> then recovers r. The lab L15 runs this for real " +
              "with N = 15 and a = 2." }));
    }

    var mSlider = el("input", { type: "range", min: "3", max: "8", value: "4",
      oninput: function () { m = (+this.value); refresh(); } });
    var rSlider = el("input", { type: "range", min: "2", max: "8", value: "4",
      oninput: function () { r = (+this.value); refresh(); } });

    refresh();
    return card("Where the period-finding peaks land", "Move the sliders to " +
      "see the measurement distribution change.", [
      el("label", { text: "counting qubits m: " + m }), mSlider,
      el("label", { text: "period r: " + r }), rSlider,
      output
    ]);
  }

  global.QC101Widgets = {
    el: el,
    card: card,
    statTile: statTile,
    barRow: barRow,
    fmt: fmt,
    complexText: complexText,
    bloch: blochWidget,
    gates: gateWidget,
    polarizer: polarizerWidget,
    bb84: bb84Widget,
    bell: bellWidget,
    knn: knnWidget,
    twoQubit: twoQubitWidget,
    period: periodWidget
  };
})(window);
