document.addEventListener("DOMContentLoaded", () => {
    const analyzeBtn = document.getElementById("analyzeBtn");
    const textInput = document.getElementById("inputText");
    const styleButtons = document.querySelectorAll(".style-btn");
    const riskButtons = document.querySelectorAll(".risk-btn");
    const charCount = document.getElementById("charCount");
    const summaryText = document.getElementById("summaryText");
    const foundDrugsBox = document.getElementById("foundDrugs");
    const lowCountSpan = document.getElementById("low-count");
    const mediumCountSpan = document.getElementById("medium-count");
    const highCountSpan = document.getElementById("high-count");

    const riskPanels = {
        low: document.getElementById("panel-low"),
        medium: document.getElementById("panel-medium"),
        high: document.getElementById("panel-high")
    };

    let selectedStyle = 1;

    textInput.addEventListener("input", () => {
        const len = textInput.value.length;
        charCount.textContent = len + " karakter";
    });

    styleButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            styleButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            selectedStyle = parseInt(btn.dataset.style);
        });
    });

    function setLoading(isLoading) {
        if (isLoading) {
            analyzeBtn.classList.add("loading", "shake");
            analyzeBtn.disabled = true;
            setTimeout(() => analyzeBtn.classList.remove("shake"), 260);
        } else {
            analyzeBtn.classList.remove("loading");
            analyzeBtn.disabled = false;
        }
    }

    analyzeBtn.addEventListener("click", () => {
        const text = textInput.value.trim();
        if (!text) {
            alert("Lütfen analiz için bir metin yazın.");
            return;
        }

        setLoading(true);

        fetch("https://drug-interaction-ai.onrender.com/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text, style: selectedStyle })
        })
            .then(r => r.json())
            .then(data => {
                renderResults(data);
                setLoading(false);
            })
            .catch(err => {
                console.error("FETCH ERROR:", err);
                alert("Sunucuya bağlanılamadı. Backend çalışmıyor olabilir.");
                setLoading(false);
            });
    });

    function renderResults(data) {
        const lowPanel = riskPanels.low;
        const midPanel = riskPanels.medium;
        const highPanel = riskPanels.high;

        lowPanel.innerHTML = "";
        midPanel.innerHTML = "";
        highPanel.innerHTML = "";

        let counts = { low: 0, medium: 0, high: 0 };

        if (!data || !Array.isArray(data.pairs) || data.pairs.length === 0) {
            summaryText.textContent = data && data.summary ? data.summary : "Metinden klinik olarak anlamlı bir etkileşim tespit edilmedi.";
            renderFoundDrugs(data && data.found_drugs);
            lowCountSpan.textContent = "0";
            mediumCountSpan.textContent = "0";
            highCountSpan.textContent = "0";
            syncRiskButtonBadges(0, 0, 0);
            Object.values(riskPanels).forEach(panel => {
                panel.classList.remove("open");
                panel.style.maxHeight = "0px";
            });
            riskButtons.forEach(b => b.classList.remove("active"));
            return;
        }

        data.pairs.forEach(pair => {
            const box = document.createElement("div");
            box.classList.add("pair-box");

            if (pair.severity === "1") box.classList.add("pair-box-low");
            else if (pair.severity === "2") box.classList.add("pair-box-medium");
            else box.classList.add("pair-box-high");

            const title = document.createElement("div");
            title.classList.add("pair-title");
            title.innerText = "Etkileşim: " + pair.drug_1 + " + " + pair.drug_2;

            const content = document.createElement("div");
            content.classList.add("pair-content");
            content.innerHTML = pair.explanation;

            title.addEventListener("click", () => {
                content.classList.toggle("open");
                const parentPanel = box.parentElement;
                setTimeout(() => {
                    parentPanel.style.maxHeight = parentPanel.scrollHeight + "px";
                }, 200);
            });

            box.appendChild(title);
            box.appendChild(content);

            if (pair.severity === "1") {
                lowPanel.appendChild(box);
                counts.low++;
            } else if (pair.severity === "2") {
                midPanel.appendChild(box);
                counts.medium++;
            } else {
                highPanel.appendChild(box);
                counts.high++;
            }
        });

        lowCountSpan.textContent = counts.low;
        mediumCountSpan.textContent = counts.medium;
        highCountSpan.textContent = counts.high;
        syncRiskButtonBadges(counts.low, counts.medium, counts.high);

        summaryText.textContent = data.summary || "Özet bilgisi alınamadı.";

        renderFoundDrugs(data.found_drugs);

        openInitialPanel(counts);
    }

    function syncRiskButtonBadges(low, medium, high) {
        riskButtons.forEach(btn => {
            const target = btn.dataset.target;
            const span = btn.querySelector("span");
            if (!span) return;
            if (target === "low") span.textContent = low;
            if (target === "medium") span.textContent = medium;
            if (target === "high") span.textContent = high;
        });
    }

    function renderFoundDrugs(foundDrugs) {
        foundDrugsBox.innerHTML = "";
        if (!Array.isArray(foundDrugs) || foundDrugs.length === 0) {
            const empty = document.createElement("span");
            empty.classList.add("pill-empty");
            empty.textContent = "İlaç bulunmadı";
            foundDrugsBox.appendChild(empty);
            return;
        }

        foundDrugs.forEach(name => {
            const pill = document.createElement("span");
            pill.classList.add("drug-pill");

            const dot = document.createElement("span");
            dot.classList.add("drug-pill-dot");

            const label = document.createElement("span");
            label.textContent = name;

            pill.appendChild(dot);
            pill.appendChild(label);
            foundDrugsBox.appendChild(pill);
        });
    }

    function openInitialPanel(counts) {
        Object.values(riskPanels).forEach(panel => {
            panel.classList.remove("open");
            panel.style.maxHeight = "0px";
        });
        riskButtons.forEach(b => b.classList.remove("active"));

        let target = null;
        if (counts.high > 0) target = "high";
        else if (counts.medium > 0) target = "medium";
        else if (counts.low > 0) target = "low";

        if (!target) return;

        const btn = Array.from(riskButtons).find(b => b.dataset.target === target);
        const panel = riskPanels[target];
        if (btn && panel) {
            btn.classList.add("active");
            panel.classList.add("open");
            setTimeout(() => {
                panel.style.maxHeight = panel.scrollHeight + "px";
            }, 150);
        }
    }

    riskButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const target = btn.dataset.target;

            Object.values(riskPanels).forEach(panel => {
                panel.classList.remove("open");
                panel.style.maxHeight = "0px";
            });

            riskButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const activePanel = riskPanels[target];
            if (activePanel) {
                activePanel.classList.add("open");
                setTimeout(() => {
                    activePanel.style.maxHeight = activePanel.scrollHeight + "px";
                }, 150);
            }
        });
    });
});
