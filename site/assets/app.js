/* ==========================================================================
   QC101 study site -- the app shell
   Hash routing, chapter rendering, the quiz engine and the progress tracker.
   ========================================================================== */
(function () {
  "use strict";

  var W = window.QC101Widgets;
  var el = W.el;

  var state = {
    manifest: null,
    questions: {},        // section number -> array of questions
    progress: loadProgress()
  };

  var STORE_KEY = "qc101-progress-v1";

  /* ------------------------------------------------------------ storage */
  function loadProgress() {
    try {
      var raw = localStorage.getItem(STORE_KEY);
      if (raw) return JSON.parse(raw);
    } catch (err) { /* private mode, quota, ... */ }
    return { sections: {}, attempts: 0, lastVisit: null, visited: [] };
  }

  function saveProgress() {
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify(state.progress));
    } catch (err) { /* ignore */ }
  }

  function markVisited(route) {
    if (!state.progress.visited) state.progress.visited = [];
    if (state.progress.visited.indexOf(route) === -1) {
      state.progress.visited.push(route);
    }
    state.progress.lastVisit = new Date().toISOString();
    saveProgress();
  }

  /* -------------------------------------------------------------- fetch */
  function fetchText(url) {
    return fetch(url, { cache: "no-cache" }).then(function (response) {
      if (!response.ok) throw new Error(url + " -> HTTP " + response.status);
      return response.text();
    });
  }

  function fetchJSON(url) {
    return fetch(url, { cache: "no-cache" }).then(function (response) {
      if (!response.ok) throw new Error(url + " -> HTTP " + response.status);
      return response.json();
    });
  }

  /* --------------------------------------------------------------- boot */
  function boot() {
    fetchJSON("content/manifest.json")
      .then(function (manifest) {
        state.manifest = manifest;
        buildNav();
        return Promise.all(manifest.sections.map(function (section) {
          return fetchJSON("content/quizzes/section_" +
            String(section.number).padStart(2, "0") + ".json")
            .then(function (questions) { state.questions[section.number] = questions; })
            .catch(function () { state.questions[section.number] = []; });
        }));
      })
      .then(function () {
        window.addEventListener("hashchange", route);
        route();
        updateTopProgress();
      })
      .catch(function (error) {
        document.getElementById("content").innerHTML =
          '<div class="card callout warn"><h3>Could not load the site content</h3>' +
          "<p>" + error.message + "</p>" +
          "<p>Run <code>python tools/build_site.py</code> first, and serve the " +
          "<code>site/</code> directory over HTTP (not <code>file://</code>).</p></div>";
      });
  }

  /* ---------------------------------------------------------------- nav */
  function buildNav() {
    var chapterNav = document.getElementById("chapterNav");
    var appendixNav = document.getElementById("appendixNav");
    chapterNav.innerHTML = "";
    appendixNav.innerHTML = "";

    state.manifest.sections.forEach(function (section) {
      var link = el("a", { class: "nav-link", href: "#/chapter/" + section.slug,
                            "data-section": section.number }, [
        el("span", { class: "nav-num", text: String(section.number) }),
        el("span", { text: section.title })
      ]);
      chapterNav.appendChild(link);
    });

    state.manifest.appendix.forEach(function (page) {
      appendixNav.appendChild(el("a", { class: "nav-link", href: "#/chapter/" + page.slug }, [
        el("span", { class: "nav-num", text: "§" }),
        el("span", { text: page.title })
      ]));
    });
  }

  function markActiveNav(route) {
    var links = document.querySelectorAll(".nav-link");
    Array.prototype.forEach.call(links, function (link) {
      link.classList.toggle("active", link.getAttribute("href") === "#" + route);
    });
    var section = Number((route.split("/")[2] || "").match(/(\d+)/)?.[1] || 0);
    Array.prototype.forEach.call(links, function (link) {
      var num = link.getAttribute("data-section");
      if (!num) return;
      var stats = state.progress.sections[num];
      link.classList.remove("done", "partial");
      if (stats && stats.total > 0) {
        link.classList.add(stats.correct / stats.total >= 0.8 ? "done" : "partial");
      }
    });
  }

  /* ------------------------------------------------------------ routing */
  function route() {
    var hash = window.location.hash.replace(/^#/, "") || "/welcome";
    var content = document.getElementById("content");
    markActiveNav(hash);
    markVisited(hash);
    document.getElementById("sidebar").classList.remove("open");

    var parts = hash.split("/").filter(Boolean);
    content.innerHTML = '<div class="loading">Loading…</div>';

    if (parts[0] === "chapter" && parts[1]) {
      loadChapter(parts[1]);
    } else if (parts[0] === "playground") {
      showPlayground();
    } else if (parts[0] === "quiz") {
      showQuiz(parts[1] ? Number(parts[1]) : null);
    } else if (parts[0] === "progress") {
      showProgress();
    } else {
      showWelcome();
    }
    try { content.scrollIntoView({ block: "start" }); } catch (err) { /* older browsers */ }
    window.scrollTo(0, 0);
  }

  function renderMath() {
    if (window.renderMathInElement) {
      window.renderMathInElement(document.getElementById("content"), {
        delimiters: [
          { left: "\\(", right: "\\)", display: false },
          { left: "\\[", right: "\\]", display: true }
        ],
        throwOnError: false,
        ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"]
      });
    }
  }

  function loadChapter(slug) {
    fetchText("content/chapters/" + slug + ".html")
      .then(function (html) {
        var content = document.getElementById("content");
        content.innerHTML = html;
        renderMath();
        enhanceChapter(slug);
      })
      .catch(function (error) {
        document.getElementById("content").innerHTML =
          '<div class="card callout warn"><h3>Chapter not found</h3><p>' +
          error.message + "</p></div>";
      });
  }

  function enhanceChapter(slug) {
    var number = Number((slug.match(/^(\d+)/) || [])[1] || 0);
    if (!number) return;
    var content = document.getElementById("content");

    // a "try this lab" button and a "quiz this section" button
    var bar = el("div", { class: "btn-row" }, [
      el("a", { class: "btn", href: "../tools/labcheck.py", target: "_blank",
                text: "Run the labs" }),
      el("a", { class: "btn ghost", href: "#/quiz/" + number, text: "Quiz this section" }),
      el("a", { class: "btn ghost", href: "#/progress", text: "My progress" })
    ]);
    var head = content.querySelector("h1");
    if (head) head.parentNode.insertBefore(bar, head.nextSibling);
  }

  /* ------------------------------------------------------------ welcome */
  function showWelcome() {
    var content = document.getElementById("content");
    var total = 0;
    Object.keys(state.questions).forEach(function (key) { total += state.questions[key].length; });

    content.innerHTML = "";
    content.appendChild(el("div", { class: "hero" }, [
      el("h1", { text: "QC101 — Quantum Computing & Introduction to Quantum Machine Learning" }),
      el("p", { class: "sub", html: "A complete, interactive study package for the " +
        "Udemy course by Kumaresan Ramanathan: 17 chapter guides, 17 runnable " +
        "labs with 350 auto-graded checks, " + total + " quiz questions and live simulators." }),
      el("div", { class: "btn-row" }, [
        el("a", { class: "btn", href: "#/chapter/01-introduction", text: "Start with section 1" }),
        el("a", { class: "btn ghost", href: "#/playground", text: "Open the playground" }),
        el("a", { class: "btn ghost", href: "#/quiz", text: "Take a quiz" })
      ])
    ]));

    var cards = el("div", { class: "grid-3", style: "margin-top:26px" });
    var features = [
      ["17", "chapter guides", "One for every section of the course, with the maths worked out and a self-check list."],
      ["17", "runnable labs", "Every lab executes real code, checks 350 assertions and prints a pass/fail summary."],
      [String(total), "quiz questions", "Auto-graded, with an explanation for every answer, and a progress report."],
      ["8", "live simulators", "Bloch sphere, gate playground, Malus's law, BB84, Bell states, quantum KNN and more."],
      ["350", "auto-graded checks", "Every number in this package was produced by running the code, not by copying slides."],
      ["100%", "self-contained", "No accounts, no API keys, no network calls. Everything runs in your browser or locally."]
    ];
    features.forEach(function (feature) {
      cards.appendChild(el("div", { class: "card" }, [
        el("div", { style: "font-size:1.8rem;font-weight:700;color:var(--accent)",
                    text: feature[0] }),
        el("div", { style: "font-weight:600", text: feature[1] }),
        el("div", { class: "widget-note", style: "margin-top:6px", text: feature[2] })
      ]));
    });
    content.appendChild(cards);

    content.appendChild(el("div", { class: "card callout info", style: "margin-top:22px" }, [
      el("h3", { text: "How the pieces fit together" }),
      el("p", { html: "Each chapter names the lab that goes with it. The labs are " +
        "plain Python in <code>labs/</code> and run with " +
        "<code>python labs/L01_quantum_vs_classical/lab.py</code>. " +
        "<code>python tools/labcheck.py</code> runs them all and prints a " +
        "pass/fail table, and <code>python tools/quiz.py</code> is the same " +
        "quiz you can take here, in the terminal." })
    ]));
  }

  /* --------------------------------------------------------- playground */
  function showPlayground() {
    var content = document.getElementById("content");
    content.innerHTML = "";
    content.appendChild(el("h1", { text: "Interactive playground" }));
    content.appendChild(el("p", { class: "widget-note", style: "font-size:1rem;max-width:70ch",
      text: "Every widget below runs entirely in your browser — no server, no " +
            "network calls. They are the interactive versions of the ideas in the labs." }));

    content.appendChild(W.bloch());
    content.appendChild(W.gates());
    content.appendChild(W.polarizer());
    content.appendChild(W.bb84());
    content.appendChild(W.bell());
    content.appendChild(W.twoQubit());
    content.appendChild(W.knn());
    content.appendChild(W.period());
    renderMath();
  }

  /* --------------------------------------------------------------- quiz */
  function showQuiz(section) {
    var content = document.getElementById("content");
    content.innerHTML = "";

    var sections = state.manifest.sections;
    var head = el("div", { class: "quiz-head" }, [
      el("h1", { style: "margin:0;font-size:1.5rem", text: "Quiz" }),
      el("div", { class: "spacer" })
    ]);

    var select = el("select", { onchange: function () { window.location.hash = "#/quiz/" + this.value; } });
    sections.forEach(function (s) {
      var option = el("option", { value: String(s.number), text: s.number + " — " + s.title });
      if (section === s.number) option.selected = true;
      select.appendChild(option);
    });
    if (!section) {
      var all = el("option", { value: "", text: "All sections" });
      all.selected = true;
      select.insertBefore(all, select.firstChild);
    }
    head.appendChild(el("label", { text: "Section: " }));
    head.appendChild(select);
    head.appendChild(el("button", { class: "btn small", text: "Shuffle & restart",
      onclick: function () { window.location.hash = "#/quiz/" + (section || "") + "?r=" + Date.now(); } }));
    content.appendChild(head);

    var pool = [];
    sections.forEach(function (s) {
      if (section && s.number !== section) return;
      (state.questions[s.number] || []).forEach(function (question) {
        pool.push(Object.assign({ _section: s.number, _title: s.title }, question));
      });
    });
    if (!pool.length) {
      content.appendChild(el("div", { class: "card callout warn" }, [
        el("h3", { text: "No questions found" }),
        el("p", { text: "Run python tools/build_site.py to copy the question bank into the site." })
      ]));
      return;
    }

    // shuffle
    for (var i = pool.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = pool[i]; pool[i] = pool[j]; pool[j] = tmp;
    }

    var shell = el("div", { class: "quiz-shell" });
    var scoreBox = el("div", { class: "stat-grid", style: "margin-bottom:20px" });

    function updateScore(correct, answered) {
      scoreBox.innerHTML = "";
      scoreBox.appendChild(W.statTile("answered", String(answered) + " / " + pool.length));
      scoreBox.appendChild(W.statTile("correct", String(correct),
        answered === 0 ? "" : (correct / answered >= 0.8 ? "good" : "warn")));
      var pct = answered ? Math.round(100 * correct / answered) : 0;
      scoreBox.appendChild(W.statTile("score", pct + "%"));
    }
    updateScore(0, 0);
    content.appendChild(scoreBox);
    content.appendChild(shell);

    var correct = 0, answered = 0;

    pool.forEach(function (question, index) {
      var block = el("div", { class: "quiz-question" });
      block.appendChild(el("div", { class: "qid",
        text: question.id + "  ·  section " + question._section + " — " + question._title }));
      block.appendChild(el("div", { class: "qtext", text: question.question }));

      var feedback = null;
      var locked = false;

      function submit() {
        if (locked) return;
        var picked = gather();
        if (picked === null || (Array.isArray(picked) && !picked.length)) return;
        locked = true;
        var isCorrect = check(picked, question);
        answered++;
        if (isCorrect) correct++;
        updateScore(correct, answered);
        record(question, isCorrect);
        Array.prototype.forEach.call(block.querySelectorAll(".choice"), function (node) {
          node.classList.add("disabled");
        });
        markChoices(block, question, picked);
        feedback = el("div", { class: "quiz-feedback " + (isCorrect ? "good" : "bad") }, [
          el("div", { class: "verdict " + (isCorrect ? "good" : "bad"),
            text: isCorrect ? "Correct." : "Not quite." }),
          el("div", { style: "margin-top:6px", html: question.explanation || "" })
        ]);
        block.appendChild(feedback);
        submitButton.remove();
      }

      function gather() {
        if (question.type === "multi") {
          var chosen = [];
          Array.prototype.forEach.call(block.querySelectorAll(".choice.selected"), function (node) {
            chosen.push(Number(node.dataset.index));
          });
          return chosen.length ? chosen : null;
        }
        var selected = block.querySelector(".choice.selected");
        return selected ? Number(selected.dataset.index) : null;
      }

      function check(picked, q) {
        if (q.type === "multi") {
          var a = q.answer.slice().sort();
          var b = picked.slice().sort();
          return a.length === b.length && a.every(function (x, i) { return x === b[i]; });
        }
        return Number(picked) === Number(q.answer);
      }

      function markChoices(scope, q, picked) {
        var nodes = scope.querySelectorAll(".choice");
        Array.prototype.forEach.call(nodes, function (node) {
          var index = Number(node.dataset.index);
          if (q.type === "multi") {
            if (q.answer.indexOf(index) !== -1) node.classList.add("correct");
            else if (picked.indexOf(index) !== -1) node.classList.add("wrong");
          } else {
            if (index === Number(q.answer)) node.classList.add("correct");
            else if (index === Number(picked)) node.classList.add("wrong");
          }
        });
      }

      var choices = question.choices || [];
      choices.forEach(function (choice, index) {
        var node = el("div", { class: "choice", "data-index": String(index) }, [
          el("span", { class: "marker", text: String.fromCharCode(65 + index) }),
          el("span", { class: "text", text: choice })
        ]);
        node.addEventListener("click", function () {
          if (locked) return;
          if (question.type === "multi") {
            node.classList.toggle("selected");
          } else {
            Array.prototype.forEach.call(block.querySelectorAll(".choice"), function (other) {
              other.classList.remove("selected");
            });
            node.classList.add("selected");
          }
        });
        block.appendChild(node);
      });

      var submitButton = el("button", { class: "btn", text: "Check answer", onclick: submit });
      block.appendChild(el("div", { class: "btn-row" }, [submitButton]));
      shell.appendChild(block);
    });
  }

  function record(question, correct) {
    var key = String(question._section);
    var stats = state.progress.sections[key] ||
      { correct: 0, total: 0, attempts: 0 };
    stats.correct += correct ? 1 : 0;
    stats.total += 1;
    stats.attempts += 1;
    state.progress.sections[key] = stats;
    state.progress.attempts = (state.progress.attempts || 0) + 1;
    saveProgress();
    updateTopProgress();
  }

  /* ----------------------------------------------------------- progress */
  function showProgress() {
    var content = document.getElementById("content");
    content.innerHTML = "";
    content.appendChild(el("h1", { text: "My progress" }));
    content.appendChild(el("p", { class: "widget-note", style: "font-size:1rem",
      text: "Stored in this browser only. The terminal tools keep their own " +
            "record in progress/ — run python tools/progress.py for that one." }));

    var sections = state.manifest.sections;
    var totalCorrect = 0, totalAnswered = 0, sectionsTouched = 0;

    var table = el("table", { class: "progress-table" });
    table.appendChild(el("tr", {}, [
      el("th", { text: "§" }), el("th", { text: "Section" }), el("th", { text: "Lab" }),
      el("th", { text: "Score" }), el("th", { text: "Progress" }), el("th", { text: "Quiz" })
    ]));

    sections.forEach(function (section) {
      var stats = state.progress.sections[String(section.number)] || { correct: 0, total: 0 };
      var questions = (state.questions[section.number] || []).length;
      totalCorrect += stats.correct;
      totalAnswered += stats.total;
      if (stats.total > 0) sectionsTouched++;

      var fraction = stats.total ? stats.correct / stats.total : 0;
      var fill = el("div", { class: "bar-fill" +
        (stats.total === 0 ? " none" : (fraction >= 0.8 ? "" : " partial")) });
      fill.style.width = (fraction * 100) + "%";

      table.appendChild(el("tr", {}, [
        el("td", { text: String(section.number) }),
        el("td", { text: section.title }),
        el("td", { class: "mono", text: section.lab }),
        el("td", { text: stats.total ? (stats.correct + "/" + stats.total) : "—" }),
        el("td", { class: "progress-bar" }, [el("div", { class: "bar" }, [fill])]),
        el("td", {}, [el("a", { class: "btn small", href: "#/quiz/" + section.number,
                                text: "Quiz " + questions })])
      ]));
    });

    content.appendChild(el("div", { class: "card" }, [table]));

    var overall = totalAnswered ? totalCorrect / totalAnswered : 0;
    content.appendChild(el("div", { class: "stat-grid", style: "margin-top:18px" }, [
      W.statTile("sections quizzed", sectionsTouched + " / " + sections.length),
      W.statTile("questions answered", String(totalAnswered)),
      W.statTile("correct", String(totalCorrect)),
      W.statTile("overall", Math.round(overall * 100) + "%",
                 overall >= 0.8 ? "good" : (overall > 0 ? "warn" : ""))
    ]));

    content.appendChild(el("div", { class: "btn-row" }, [
      el("button", { class: "btn ghost", text: "Reset my progress", onclick: function () {
        if (confirm("Delete all your quiz progress in this browser?")) {
          state.progress = { sections: {}, attempts: 0, lastVisit: null, visited: [] };
          saveProgress();
          updateTopProgress();
          showProgress();
        }
      } })
    ]));
  }

  function updateTopProgress() {
    var totalCorrect = 0, totalAnswered = 0;
    Object.keys(state.progress.sections || {}).forEach(function (key) {
      totalCorrect += state.progress.sections[key].correct;
      totalAnswered += state.progress.sections[key].total;
    });
    var pct = totalAnswered ? Math.round(100 * totalCorrect / totalAnswered) : 0;
    document.getElementById("topBarFill").style.width = pct + "%";
    document.getElementById("topProgressText").textContent = totalAnswered
      ? pct + "% (" + totalCorrect + "/" + totalAnswered + ")"
      : "not started";
  }

  /* ------------------------------------------------------------- chrome */
  function setupChrome() {
    document.getElementById("menuBtn").addEventListener("click", function () {
      document.getElementById("sidebar").classList.toggle("open");
    });
    document.getElementById("themeBtn").addEventListener("click", function () {
      var root = document.documentElement;
      var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("qc101-theme", next); } catch (err) { /* ignore */ }
    });
    try {
      var saved = localStorage.getItem("qc101-theme");
      if (saved) document.documentElement.setAttribute("data-theme", saved);
    } catch (err) { /* ignore */ }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { setupChrome(); boot(); });
  } else {
    setupChrome();
    boot();
  }
})();
